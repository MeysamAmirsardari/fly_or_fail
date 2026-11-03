"""fastlif: fast, exact-semantics re-implementation of the Shiu et al. 2024 whole-brain LIF model
(Drosophila_brain_model/model.py, commit 91bdd1e7) for batched silencing experiments.

Semantics replicated (verified against the Brian2 2.11 generated code, see docs/research/sim_validation.md):
  per time step s (t = s*dt, dt = 0.1 ms, s = 0..T-1, T = 10000 for 1 s):
   1. groups/stateupdate: not_refractory = (s - lastspike_step) >= rfc_steps   (rfc 2.2 ms -> 22 steps; 0 for Poisson targets)
        if not_refractory:  v <- L8 + (L9*g + L10*v);  g <- L2*g     (exact 'linear' solution, Brian2's own loop invariants)
   2. thresholds: spike if (v > v_th) and not_refractory; then not_refractory <- False, lastspike <- s
   3. synapses (order -1): spikes emitted at step s-18 (delay 1.8 ms rounded to 18 steps) are delivered:
        g_post += w  ONLY IF not_refractory[post]   (Brian2 conditional write for '(unless refractory)' variables)
        delivery order: presynaptic neurons ascending, synapses in connectivity-file order (= Brian2 spike queue order)
   4. PoissonInput (synapses slot, order 0): v += 68.75 mV * Bernoulli(rate*dt)  ONLY IF not_refractory
   5. resets: v <- v_rst, g <- 0 for neurons that spiked in step 2 ('w = 0' in the reset is a no-op temporary)
  Silencing: outgoing weights of silenced neurons are zero (their spikes are not delivered). Optional 'inout' mode also
  drops input to silenced neurons (sensitivity analysis only; NOT the original code).

Common random numbers (CRN): the Bernoulli input of stimulated neuron with FlyWire id f in trial-seed t is driven by
  u[f, t, s] ~ U[0,1) from numpy PCG64(SeedSequence([salt, t, f])); an input event occurs at step s iff u < rate*dt.
  => identical trains for every condition sharing (t, f, rate), independent of which other neurons are stimulated or
  silenced and of network size; across rates the trains are NESTED (events at rate r1 < r2 are a subset of those at r2),
  i.e. exact thinning of the highest-rate train. Marginally each train is Bernoulli(rate*dt) per step, exactly the
  distribution of Brian2's PoissonInput(N=1) (binomial with n=1).
"""
import os, sys, math, time, json, argparse
import numpy as np, pandas as pd
import numba as nb
from numba import njit, prange

# ----------------------------------------------------------------------------------------------- constants (SI units)
# Same float expressions as Brian2 (value * unit scale), so the arithmetic mirrors the generated Cython code.
MS, MV = 1e-3, 1e-3
DT = 0.1 * MS
V_0 = -52 * MV; V_RST = -52 * MV; V_TH = -45 * MV
T_MBR = 20 * MS; TAU = 5 * MS
T_RFC = 2.2 * MS; T_DLY = 1.8 * MS
W_SYN = .275 * MV
W_POI = 68.75 * MV          # Brian2 code string 'v += poissoninput_binomial()*68.75 * mvolt' (= w_syn * f_poi, f_poi=250)


def timestep(t, dt):        # Brian2 core/functions.py timestep()
    return int((t + 1e-3 * dt) / dt)


RFC_STEPS = timestep(T_RFC, DT)                 # 22
DELAY_STEPS = int(T_DLY / DT + 0.5)             # 18  (spikequeue.h: (int)(real_delay/dt + 0.5))
# Brian2 'linear' stateupdater loop invariants (verbatim from generated code)
_l1 = (-DT) / TAU; L2 = math.exp(_l1); _l3 = TAU / (T_MBR - TAU); _l4 = DT / T_MBR; _l5 = DT / TAU; _l6 = (-DT) / T_MBR
L8 = V_0 - (V_0 * math.exp(_l6))
L9 = ((_l3 * ((-math.exp(_l4)) + math.exp(_l5))) * math.exp(_l6)) * math.exp(_l1)
L10 = math.exp(_l6)

SIM = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SIM, 'out')
REPO = os.path.dirname(SIM) + '/'
EXTERNAL = os.path.abspath(os.environ.get('NJ_EXTERNAL', REPO + '../external')) + '/'   # see README
DATA = EXTERNAL + 'Drosophila_brain_model/'
PATHS = {'v630': (DATA + '2023_03_23_completeness_630_final.csv', DATA + '2023_03_23_connectivity_630_final.parquet'),
         'v783': (DATA + 'Completeness_783.csv', DATA + 'Connectivity_783.parquet')}
IDS = REPO + 'feasibility/ids/'
MN9_L, MN9_R = 720575940660219265, 720575940645521262


# ----------------------------------------------------------------------------------------------- network container
class Net:
    """CSR network over a set of neurons. `gidx` = global (Brian2) indices, ascending; local index = position.
    leak[i] = neuron i has an excitatory (w>0) synapse onto a neuron NOT in this network (boundary flag)."""

    def __init__(self, ver, gidx, fid, indptr, post, w, leak):
        self.ver, self.gidx, self.fid = ver, gidx, fid
        self.indptr, self.post, self.w, self.leak = indptr, post, w, leak
        self.n = len(gidx)
        self.f2l = {int(f): i for i, f in enumerate(fid)}

    def loc(self, fids, strict=True):
        out = []
        for f in fids:
            f = int(f)
            if f in self.f2l: out.append(self.f2l[f])
            elif strict: raise KeyError(f'neuron {f} not in network ({self.n} neurons)')
        return np.array(out, dtype=np.int64)

    def nsyn(self):
        return int(self.indptr[-1])


_FULL = {}


def load_full(ver):
    """Full network exactly as model.create_model builds it (row order of completeness csv = Brian2 index)."""
    if ver in _FULL: return _FULL[ver]
    cache = os.path.join(OUT, f'fullnet_{ver}.npz')
    if os.path.exists(cache):
        z = np.load(cache)
        fid, indptr, post, wint = z['fid'], z['indptr'], z['post'], z['wint']
    else:
        pc, pn = PATHS[ver]
        comp = pd.read_csv(pc, index_col=0)
        con = pd.read_parquet(pn, columns=['Presynaptic_Index', 'Postsynaptic_Index', 'Excitatory x Connectivity'])
        pre = con['Presynaptic_Index'].values.astype(np.int64)
        assert np.all(np.diff(pre) >= 0), 'connectivity not sorted by presynaptic index'
        # keep file order within each presynaptic neuron (= Brian2 synapse creation order = spike queue order)
        n = len(comp)
        indptr = np.zeros(n + 1, np.int64); np.add.at(indptr, pre + 1, 1); indptr = np.cumsum(indptr)
        post = con['Postsynaptic_Index'].values.astype(np.int32)
        wint = con['Excitatory x Connectivity'].values.astype(np.int64)
        fid = comp.index.values.astype(np.int64)
        os.makedirs(OUT, exist_ok=True)
        np.savez(cache, fid=fid, indptr=indptr, post=post, wint=wint)
    w = wint * W_SYN        # as model.create_model: values * params['w_syn']  (int64 array * float -> float64)
    n = len(fid)
    net = Net(ver, np.arange(n, dtype=np.int64), fid, indptr, post, w, np.zeros(n, np.bool_))
    net.wint = wint
    _FULL[ver] = net
    return net


def subnet(full, gidx):
    """Exact restriction of the full network to neuron set gidx (global indices). Synapses whose pre and post are both in
    the set are kept, in the original order; leak flags excitatory synapses leaving the set."""
    gidx = np.unique(np.asarray(gidx, np.int64))
    inset = np.zeros(full.n, np.bool_); inset[gidx] = True
    g2l = -np.ones(full.n, np.int64); g2l[gidx] = np.arange(len(gidx))
    starts, ends = full.indptr[gidx], full.indptr[gidx + 1]
    sel = np.concatenate([np.arange(a, b) for a, b in zip(starts, ends)]) if len(gidx) else np.zeros(0, np.int64)
    cnt_pre = np.repeat(np.arange(len(gidx)), ends - starts)
    keep = inset[full.post[sel]]
    leak = np.zeros(len(gidx), np.bool_)
    out_exc = (~keep) & (full.w[sel] > 0)
    leak[np.unique(cnt_pre[out_exc])] = True
    sel_k = sel[keep]; pre_k = cnt_pre[keep]
    indptr = np.zeros(len(gidx) + 1, np.int64); np.add.at(indptr, pre_k + 1, 1); indptr = np.cumsum(indptr)
    net = Net(full.ver, gidx, full.fid[gidx], indptr, g2l[full.post[sel_k]].astype(np.int32), full.w[sel_k], leak)
    return net


# ----------------------------------------------------------------------------------------------- CRN stimulus
def crn_uniforms(trial_seeds, stim_fids, T, salt=0):
    """u[t_i, k, s] for trial seed trial_seeds[t_i] and stimulated FlyWire id stim_fids[k]."""
    u = np.empty((len(trial_seeds), len(stim_fids), T), np.float64)
    for a, t in enumerate(trial_seeds):
        for k, f in enumerate(stim_fids):
            u[a, k] = np.random.Generator(np.random.PCG64(np.random.SeedSequence([int(salt), int(t), int(f)]))).random(T)
    return u


# ----------------------------------------------------------------------------------------------- kernel
@njit(cache=True, fastmath=False, nogil=True)
def _sim_one(n, indptr, post, w, rfc, leak, stim_loc, stim_on, u, p_ev, sil_out, sil_in, T, D,
             rec_mask, rec_s, rec_i, counts, viol_idx):
    """One trial of one condition. Returns (n_recorded, n_violations, rec_overflow)."""
    v = np.full(n, V_0); g = np.zeros(n)
    last = np.full(n, -(1 << 40), np.int64)         # Brian2 lastspike = -1e4 s  -> never refractory initially
    notref = np.ones(n, np.bool_)
    buf = np.empty((D + 1, n), np.int32); bcnt = np.zeros(D + 1, np.int64)
    nst = stim_loc.shape[0]
    nrec = 0; nviol = 0; overflow = False
    cap = rec_s.shape[0]; vcap = viol_idx.shape[0]
    for s in range(T):
        slot = s % (D + 1)
        cnt = 0
        # 1+2: state update and threshold (per-neuron independent -> fused)
        for i in range(n):
            nr = (s - last[i]) >= rfc[i]
            if nr:
                g0 = g[i]
                g[i] = L2 * g0
                v[i] = L8 + ((L9 * g0) + (L10 * v[i]))
                if v[i] > V_TH:
                    buf[slot, cnt] = i; cnt += 1
                    last[i] = s; nr = False
                    counts[i] += 1
                    if rec_mask[i]:
                        if nrec < cap:
                            rec_s[nrec] = s; rec_i[nrec] = i; nrec += 1
                        else:
                            overflow = True
                    if leak[i] and not sil_out[i]:
                        if nviol < vcap: viol_idx[nviol] = i
                        nviol += 1
            notref[i] = nr
        bcnt[slot] = cnt
        # 3: synaptic delivery of spikes emitted at step s-D
        if s >= D:
            ds = (s - D) % (D + 1)
            for a in range(bcnt[ds]):
                p = buf[ds, a]
                if sil_out[p]: continue
                for k in range(indptr[p], indptr[p + 1]):
                    j = post[k]
                    if notref[j] and not sil_in[j]:
                        g[j] += w[k]
        # 4: Poisson input (Bernoulli per step, conditional on not_refractory)
        for k in range(nst):
            if stim_on[k] and u[k, s] < p_ev:
                i = stim_loc[k]
                if notref[i]:
                    v[i] += W_POI
        # 5: reset
        for a in range(cnt):
            i = buf[slot, a]
            v[i] = V_RST
            g[i] = 0.0
    return nrec, nviol, overflow


@njit(cache=True, parallel=True)
def _sim_many(n, indptr, post, w, rfc, leak, stim_loc, job_stim_on, u_all, job_trial, job_p,
              sil_ptr, sil_idx, inout, T, D, rec_mask, rec_s, rec_i, counts, nrec, nviol, viol_idx, overflow):
    nj = job_trial.shape[0]
    for j in prange(nj):
        sil_out = np.zeros(n, np.bool_); sil_in = np.zeros(n, np.bool_)
        for a in range(sil_ptr[j], sil_ptr[j + 1]):
            sil_out[sil_idx[a]] = True
            if inout: sil_in[sil_idx[a]] = True
        r = _sim_one(n, indptr, post, w, rfc, leak, stim_loc, job_stim_on[j], u_all[job_trial[j]], job_p[j],
                     sil_out, sil_in, T, D, rec_mask, rec_s[j], rec_i[j], counts[j], viol_idx[j])
        nrec[j] = r[0]; nviol[j] = r[1]; overflow[j] = r[2]


# ----------------------------------------------------------------------------------------------- driver
def run(net, stim_fids, jobs, trial_seeds=None, T=10000, salt=0, record=None, rec_cap=0, inout=False, threads=None,
        u=None):
    """Simulate a batch of jobs on `net`.
    stim_fids : FlyWire ids that MAY be stimulated (the CRN stream of each is keyed by its id).
    jobs      : list of dicts {rate: Hz, trial: trial seed, silence: [fids] (opt), stim: [fids] subset (opt, default all)}
    record    : None | 'all' | list of fids whose spike steps are recorded (up to rec_cap per job).
    Returns dict with counts (n_jobs, n) int32, nviol (n_jobs,), viol (n_jobs, 64) local idx, spikes (list of (step, fid)).
    """
    if threads: nb.set_num_threads(threads)
    if trial_seeds is None: trial_seeds = sorted({int(j['trial']) for j in jobs})
    tpos = {t: a for a, t in enumerate(trial_seeds)}
    stim_fids = [int(f) for f in stim_fids]
    stim_loc = net.loc(stim_fids)
    if u is None: u = crn_uniforms(trial_seeds, stim_fids, T, salt)
    rfc = np.full(net.n, RFC_STEPS, np.int64); rfc[stim_loc] = 0          # model.poi: rfc = 0 for Poisson targets
    nj = len(jobs)
    job_stim_on = np.ones((nj, len(stim_fids)), np.bool_)
    sil_ptr = np.zeros(nj + 1, np.int64); sil_list = []
    for a, jb in enumerate(jobs):
        if jb.get('stim') is not None:
            on = set(int(f) for f in jb['stim'])
            assert on <= set(stim_fids)
            job_stim_on[a] = [f in on for f in stim_fids]
        sl = net.loc(jb.get('silence', []) or [])
        sil_list.append(sl); sil_ptr[a + 1] = sil_ptr[a] + len(sl)
    sil_idx = np.concatenate(sil_list).astype(np.int64) if sil_ptr[-1] else np.zeros(1, np.int64)
    job_trial = np.array([tpos[int(jb['trial'])] for jb in jobs], np.int64)
    job_p = np.array([float(jb['rate']) * DT for jb in jobs])     # Brian2: binomial(1, p = rate*dt)
    rec_mask = np.zeros(net.n, np.bool_)
    if record == 'all': rec_mask[:] = True
    elif record is not None: rec_mask[net.loc(record)] = True
    cap = max(int(rec_cap), 1) if record is not None else 1
    rec_s = np.zeros((nj, cap), np.int32); rec_i = np.zeros((nj, cap), np.int32)
    counts = np.zeros((nj, net.n), np.int32)
    nrec = np.zeros(nj, np.int64); nviol = np.zeros(nj, np.int64); viol_idx = -np.ones((nj, 64), np.int64)
    overflow = np.zeros(nj, np.bool_)
    _sim_many(net.n, net.indptr, net.post, net.w, rfc, net.leak, stim_loc, job_stim_on, u, job_trial, job_p,
              sil_ptr, sil_idx, bool(inout), T, DELAY_STEPS, rec_mask, rec_s, rec_i, counts, nrec, nviol, viol_idx,
              overflow)
    if record is not None and overflow.any():
        raise RuntimeError('spike recording buffer overflow; increase rec_cap')
    spikes = [(rec_s[a, :nrec[a]].copy(), net.fid[rec_i[a, :nrec[a]]]) for a in range(nj)] if record is not None else None
    viol_fids = [net.fid[viol_idx[a][viol_idx[a] >= 0]] for a in range(nj)]
    return dict(counts=counts, nviol=nviol, viol_fids=viol_fids, spikes=spikes, fid=net.fid, gidx=net.gidx)


def sugar_right(ver):
    s = pd.read_csv(IDS + 'sugar_GRN_right.csv').flywire_id.tolist()
    comp = set(load_full(ver).fid.tolist())
    return [int(i) for i in s if i in comp]


# ----------------------------------------------------------------------------------------------- CLI
def _parse_trials(s):
    out = []
    for part in s.split(','):
        if '-' in part:
            a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='fastlif: batched exact-semantics Shiu et al. LIF simulator')
    ap.add_argument('--ver', default='v630', choices=['v630', 'v783'])
    ap.add_argument('--net', default='closure', help="'full' or 'closure' (sim/out/closure_<ver>.npz from reduce.py)")
    ap.add_argument('--rates', default='100', help='comma-separated Hz')
    ap.add_argument('--trials', default='0-7', help='trial seeds, e.g. 0-7 or 0,3,5')
    ap.add_argument('--conditions', default=None,
                    help="JSON file: list of {name, silence:[fids], stim:[fids] (opt)}; default = intact only")
    ap.add_argument('--salt', type=int, default=0)
    ap.add_argument('--inout', action='store_true', help='also drop input to silenced neurons (sensitivity only)')
    ap.add_argument('--threads', type=int, default=None)
    ap.add_argument('--record', default=None, help="'all' or comma-separated fids (spike steps saved)")
    ap.add_argument('--rec_cap', type=int, default=200000)
    ap.add_argument('--out', required=True, help='output .npz')
    a = ap.parse_args(argv)
    sys.path.insert(0, SIM)
    conds = json.load(open(a.conditions)) if a.conditions else [dict(name='intact', silence=[])]
    rates = [float(x) for x in a.rates.split(',')]; trials = _parse_trials(a.trials)
    stim = sugar_right(a.ver)
    jobs = [dict(cond=c['name'], silence=c.get('silence', []), stim=c.get('stim'), rate=r, trial=t)
            for c in conds for r in rates for t in trials]
    rec = None if a.record is None else ('all' if a.record == 'all' else [int(x) for x in a.record.split(',')])
    t0 = time.time()
    kw = dict(trial_seeds=trials, salt=a.salt, record=rec, rec_cap=a.rec_cap, inout=a.inout, threads=a.threads)
    if a.net == 'full':
        net = load_full(a.ver); res = run(net, stim, jobs, **kw); res['n_expansions'] = 0
    else:   # closure + runtime boundary check + automatic exact expansion (reduce.run_exact)
        import reduce
        net, res = reduce.run_exact(a.ver, stim, jobs, **kw)
    wall = time.time() - t0
    if res['nviol'].any():
        bad = [jobs[i]['cond'] for i in np.flatnonzero(res['nviol'])]
        print(f'BOUNDARY VIOLATION in {len(bad)} jobs (results for those jobs are NOT exact; run reduce.py expand):',
              sorted(set(bad))[:20], file=sys.stderr)
    save = dict(counts=res['counts'].astype(np.uint16), fid=res['fid'], nviol=res['nviol'],
                job_cond=np.array([j['cond'] for j in jobs]), job_rate=np.array([j['rate'] for j in jobs]),
                job_trial=np.array([j['trial'] for j in jobs]), salt=a.salt, inout=a.inout, ver=a.ver, net=a.net,
                n_expansions=res['n_expansions'])
    assert res['counts'].max() < 65535
    if rec is not None:
        save['spk_job'] = np.concatenate([np.full(len(s), i) for i, (s, f) in enumerate(res['spikes'])])
        save['spk_step'] = np.concatenate([s for s, f in res['spikes']]); save['spk_fid'] = np.concatenate([f for s, f in res['spikes']])
    np.savez_compressed(a.out, **save)
    print(f'{len(jobs)} jobs ({res["n_expansions"]} closure expansions) on {net.n} neurons / {net.nsyn()} synapses in {wall:.1f} s -> {a.out}')


if __name__ == '__main__':
    main()
