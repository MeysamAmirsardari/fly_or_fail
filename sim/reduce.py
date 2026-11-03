"""reduce: EXACT network reduction for fastlif.

Closure set C (global Brian2 indices) is stored in sim/out/closure_<ver>.npz and only ever GROWS.

Exactness theorem (proof in docs/research/sim_validation.md, section 'Reduction'):
  Let C contain every stimulated neuron. Run the restriction of the model to C (synapses with pre and post in C,
  same order). If, during the run, no neuron that spikes and is not output-silenced has an excitatory (w>0) synapse
  onto a neuron outside C, then the restricted run is identical (same floating-point operations, hence bit-identical
  spike trains) to the full-network run with the same inputs, and every neuron outside C is silent in the full run.
  Sketch: outside C a neuron starts at (v_0, 0), receives no Poisson input and only w <= 0 synaptic input, so g <= 0
  and v <= v_0 + O(ulp) < v_th forever: it never spikes, hence never influences C. Within C every delivered input
  comes from spiking neurons, all of which lie in C, and is summed in the same order (pre ascending, file order).
The runtime BOUNDARY CHECK in the fastlif kernel flags any violation (spiking neuron with 'leak' flag); run_exact()
then adds the excitatory out-neighbours of the flagged neurons to C and re-runs the affected jobs until no job flags.
Results of non-flagged jobs are exact for ANY C, so earlier results remain valid after C grows (zero-padding).
"""
import os, sys, json, time, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastlif as F


def closure_path(ver):
    return os.path.join(F.OUT, f'closure_{ver}.npz')


def exc_out(full, gidx):
    """Global indices of excitatory (w>0) out-neighbours of neurons gidx in the full network."""
    gidx = np.asarray(gidx, np.int64)
    if len(gidx) == 0: return np.zeros(0, np.int64)
    sel = np.concatenate([np.arange(full.indptr[i], full.indptr[i + 1]) for i in gidx])
    return np.unique(full.post[sel][full.w[sel] > 0]).astype(np.int64)


def save_closure(ver, gidx, meta):
    p = closure_path(ver)
    if os.path.exists(p):                              # monotone: never drop neurons someone else added
        gidx = np.union1d(gidx, np.load(p)['gidx'])
    tmp = p + f'.tmp{os.getpid()}.npz'
    np.savez(tmp, gidx=np.asarray(gidx, np.int64), meta=json.dumps(meta))
    os.replace(tmp, p)
    return np.asarray(gidx, np.int64)


def load_closure(ver, gidx=None):
    full = F.load_full(ver)
    if gidx is None: gidx = np.load(closure_path(ver))['gidx']
    return F.subnet(full, gidx)


def build(ver, rates, trials, threads=2, extra_fids=()):
    """C0 = stimulated  U  active (spiking in any intact job, FULL network)  U  excitatory out-neighbours(active)."""
    full = F.load_full(ver)
    stim = F.sugar_right(ver)
    jobs = [dict(rate=r, trial=t) for r in rates for t in trials]
    t0 = time.time()
    res = F.run(full, stim, jobs, trial_seeds=list(trials), threads=threads)
    act = np.flatnonzero(res['counts'].sum(0) > 0)
    stim_g = full.gidx[full.loc(stim)]
    extra = full.gidx[full.loc(extra_fids)] if len(extra_fids) else np.zeros(0, np.int64)
    C = np.union1d(np.union1d(np.union1d(stim_g, act), exc_out(full, act)), extra)
    meta = dict(ver=ver, rates=list(rates), trials=list(trials), n_active=int(len(act)), n_closure=int(len(C)),
                built=time.strftime('%Y-%m-%d %H:%M:%S'), wall_s=round(time.time() - t0, 1))
    C = save_closure(ver, C, meta)
    print('closure', json.dumps(meta), 'saved size', len(C))
    return C, act, res


def run_exact(ver, stim, jobs, net=None, persist=True, max_iter=20, log=print, **kw):
    """Run jobs on the closure; expand C and re-run flagged jobs until no boundary violation remains.
    Returns (net, res) with res['counts'] aligned to net.gidx (final closure), res['n_expansions']."""
    full = F.load_full(ver)
    if net is None: net = load_closure(ver)
    res = F.run(net, stim, jobs, **kw)
    counts = res['counts']; n_exp = 0; spikes = res['spikes']
    todo = np.flatnonzero(res['nviol'] > 0)
    while len(todo):
        if n_exp >= max_iter: raise RuntimeError('closure expansion did not converge')
        # all spiking, non-output-silenced neurons with a leaking excitatory synapse, over flagged jobs
        bad = set()
        for j in todo:
            sil = set(net.loc(jobs[j].get('silence', []) or []).tolist())
            for i in np.flatnonzero((counts[j] > 0) & net.leak):
                if i not in sil: bad.add(int(net.gidx[i]))
        bad = np.array(sorted(bad), np.int64)
        newC = np.union1d(net.gidx, exc_out(full, bad))
        log(f'[reduce] boundary check fired in {len(todo)} job(s); {len(bad)} leaking spiking neuron(s); '
            f'closure {net.n} -> {len(newC)}')
        if persist: newC = save_closure(ver, newC, dict(expanded_from=net.n, reason='runtime boundary check',
                                                         time=time.strftime('%Y-%m-%d %H:%M:%S')))
        newnet = F.subnet(full, newC)
        # re-map old results into the new index space (zero-padding is exact for non-flagged jobs)
        pos = np.searchsorted(newnet.gidx, net.gidx)
        c2 = np.zeros((len(jobs), newnet.n), np.int32); c2[:, pos] = counts
        r2 = F.run(newnet, stim, [jobs[j] for j in todo], **kw)
        c2[todo] = r2['counts']
        res['nviol'][todo] = r2['nviol']
        if spikes is not None:
            for a, j in enumerate(todo): spikes[j] = r2['spikes'][a]
        counts = c2; net = newnet; n_exp += 1
        todo = todo[r2['nviol'] > 0]
    res.update(counts=counts, fid=net.fid, gidx=net.gidx, n_expansions=n_exp, spikes=spikes)
    return net, res


def main():
    ap = argparse.ArgumentParser(description='build the exact closure set for fastlif')
    ap.add_argument('cmd', choices=['build', 'info'])
    ap.add_argument('--ver', default='v630')
    ap.add_argument('--rates', default='50,100,200,300,400')
    ap.add_argument('--trials', default='0-7')
    ap.add_argument('--threads', type=int, default=2)
    a = ap.parse_args()
    if a.cmd == 'build':
        build(a.ver, [float(x) for x in a.rates.split(',')], F._parse_trials(a.trials), a.threads)
    net = load_closure(a.ver)
    z = np.load(closure_path(a.ver))
    print('closure', a.ver, 'neurons', net.n, 'synapses', net.nsyn(), 'leaking (boundary) neurons', int(net.leak.sum()),
          'meta', str(z['meta']))


if __name__ == '__main__':
    main()
