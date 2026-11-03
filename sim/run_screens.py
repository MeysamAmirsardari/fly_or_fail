"""run_screens: pre-registered silencing screens (PROJECT_DESIGN v1.0 S5-S6) with fastlif on v783.

Primary MN9 720575940660219265, secondary 720575940618238523; seeds 0-29; CRN salt 0 (same u as the intact curves).
Frozen lambda grids from analysis/out/frozen_grid_v783.json (read only).  Each fastlif call <= 1000 jobs.
Order: unit checks -> S_shiu (intact, controls, singles) -> S_pure (intact, whole types).
Writes analysis/out/screen_single_shiu.parquet, screen_types_pure.parquet and matching *_conditions.parquet.
Resumable via sim/out/screens_ckpt/. No analysis of results is done here beyond the 3 unit checks.
usage: python run_screens.py [threads]
"""
import sys, os, json, time, pickle, datetime
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'analysis'))
import fastlif as F, reduce as R, common as C, curves

VER = 'v783'; SEEDS = list(range(30)); SALT = 0; MAXJOBS = 1000
PRIMARY, SECONDARY = C.MN9_CONTRA, C.MN9_IPSI[VER]
assert (PRIMARY, SECONDARY) == (720575940660219265, 720575940618238523)
OUT = C.OUT; CK = HERE + '/out/screens_ckpt/'
THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 4
LOG = open(HERE + '/logs/run_screens.log', 'a')
def log(s):
    s = f'[{time.strftime("%H:%M:%S")}] {s}'; print(s, flush=True); LOG.write(s + '\n'); LOG.flush()

GRID = json.load(open(OUT + 'frozen_grid_v783.json'))
sha_grid = C.md5(OUT + 'frozen_grid_v783.json')
FULL = F.load_full(VER)


def start_net(stim):
    z = np.load(OUT + 'intact_curve_v783_shiu.npz')
    stim_g = FULL.gidx[FULL.loc(stim)]
    g = np.union1d(np.union1d(z['gidx'], np.load(R.closure_path(VER))['gidx']), np.union1d(stim_g, R.exc_out(FULL, stim_g)))
    return F.subnet(FULL, g)


def run_conditions(net, stim, u, conds, lam, tag):
    """conds: list of (cid, silence list). Returns net, {cid: array (L, S, 2) int}. Chunks of <= MAXJOBS jobs."""
    per = len(lam) * len(SEEDS); k = max(1, MAXJOBS // per); res = {}
    for a in range(0, len(conds), k):
        part = conds[a:a + k]
        jobs = [dict(rate=float(l), trial=t, silence=list(sil)) for _, sil in part for l in lam for t in SEEDS]
        assert len(jobs) <= MAXJOBS
        t0 = time.time()
        net, r = R.run_exact(VER, stim, jobs, net=net, persist=False, log=log, trial_seeds=SEEDS, threads=THREADS, u=u)
        assert not r['nviol'].any()
        pi, si = net.loc([PRIMARY])[0], net.loc([SECONDARY])[0]
        cnt = r['counts'][:, [pi, si]].astype(np.int64)
        for b, (cid, _) in enumerate(part):
            res[cid] = cnt[b * per:(b + 1) * per].reshape(len(lam), len(SEEDS), 2)
        log(f'{tag}: conds {a + len(part)}/{len(conds)} ({len(jobs)} jobs, {time.time() - t0:.0f}s, net {net.n}, exp {r["n_expansions"]})')
        del r
    return net, res


def run_cached(name, net, stim, u, conds, lam):
    p = CK + name + '.pkl'
    done = pickle.load(open(p, 'rb')) if os.path.exists(p) else {}
    todo = [c for c in conds if c[0] not in done]
    per = len(lam) * len(SEEDS); k = max(1, MAXJOBS // per)
    for a in range(0, len(todo), 30 * k):                       # checkpoint every ~30 calls
        net, res = run_conditions(net, stim, u, todo[a:a + 30 * k], lam, name)
        done.update(res); pickle.dump(done, open(p + '.tmp', 'wb')); os.replace(p + '.tmp', p)
    return net, done


def write(stem, input_set, lam, meta_rows, data, t_start):
    rows = []; lam = [float(x) for x in lam]
    for cid, *_ in meta_rows:
        d = data[cid]
        for i, l in enumerate(lam):
            for j, s in enumerate(SEEDS):
                rows.append((cid, input_set, l, s, int(d[i, j, 0]), int(d[i, j, 1])))
    counts = pd.DataFrame(rows, columns=['condition_id', 'input_set', 'lambda_hz', 'seed', 'mn9_primary_count', 'mn9_secondary_count'])
    counts = counts.astype({'seed': 'int64', 'mn9_primary_count': 'int64', 'mn9_secondary_count': 'int64', 'lambda_hz': 'float64'})
    conds = pd.DataFrame([dict(condition_id=cid, kind=kind, silenced_ids=[int(x) for x in sil], input_set=input_set,
                               lambda_hz=lam, duration_s=1.0, flywire_version=VER, label=label)
                          for cid, kind, sil, label in meta_rows])
    curves.validate_screen(counts, conds)
    counts.to_parquet(OUT + f'{stem}.parquet'); conds.to_parquet(OUT + f'{stem}_conditions.parquet')
    log(f'wrote {stem}.parquet ({len(counts)} rows, {len(conds)} conditions) + conditions; validate_screen OK')


def main():
    T0 = time.time(); checks = {}
    # ---------------- S_shiu
    stim = C.S_shiu(VER); assert len(stim) == 20
    z = np.load(OUT + 'intact_curve_v783_shiu.npz')
    assert set(int(x) for x in z['stim']) == set(stim)
    S = set(stim); excl = S | {PRIMARY, SECONDARY}
    cand = sorted(int(f) for f in z['active_fid'] if int(f) not in excl)
    log(f'S_shiu: |S|={len(stim)} active={len(z["active_fid"])} candidates={len(cand)}; grid sha {sha_grid}')
    lam = GRID['shiu']['lambda_hz']
    net = start_net(stim); u = F.crn_uniforms(SEEDS, stim, 10000, SALT)
    meta = [('intact', 'intact', [], 'intact'), ('ctl_T', 'control', [PRIMARY], 'T'),
            ('ctl_T_ipsi', 'control', [SECONDARY], 'T_ipsi'), ('ctl_all_S', 'control', stim, 'all_S')]
    meta += [(f'ctl_grn_{g}', 'control', [g], f'grn:{g}') for g in stim]
    meta += [(f'k_{k}', 'single', [k], str(k)) for k in cand]
    assert len({m[0] for m in meta}) == len(meta)
    # unit check (c): outgoing-weight zeroing is exact (run BEFORE the screen)
    checks['outgoing_zeroing'] = unit_zeroing(net, stim, u, cand)
    net, data = run_cached('shiu', net, stim, u, [(m[0], m[2]) for m in meta], lam)
    # unit checks (a), (b)
    I = data['intact']; l_all = data['ctl_all_S']
    checks['silence_MN9_primary_unchanged'] = bool(np.array_equal(data['ctl_T'][..., 0], I[..., 0]))
    checks['silence_MN9_secondary_unchanged'] = bool(np.array_equal(data['ctl_T_ipsi'][..., 1], I[..., 1]))
    checks['silence_all_S_zero'] = bool(l_all.max() == 0)
    for k, v in checks.items(): log(f'UNIT CHECK {k}: {"PASS" if v else "FAIL"}')
    write('screen_single_shiu', 'S_shiu', lam, meta, data, T0)
    # ---------------- S_pure
    stimp = C.S_pure(VER); lamp = GRID['pure']['lambda_hz']
    ids = pd.read_csv(OUT + 'S_pure_ids.csv'); ids = ids[ids.in_v783]
    assert set(ids.flywire_id) == set(stimp), 'S_pure ids mismatch with S_pure_ids.csv'
    log(f'S_pure: |S|={len(stimp)}')
    members = C.ext_type_members(VER)
    log('Zorro: not a key in sez_neurons.pickle; STRUCT mapping in analysis/common.py (cell_type CB0192, seed id '
        f'{C.ZORRO_SEED_ID} from Jacobs 2024), not in analysis/out; used it')
    metap = [('intact', 'intact', [], 'intact')]
    for name in C.EXT_TYPES:
        m = members[name]['present']; log(f'type {name}: {len(members[name]["all"])} ids, {len(m)} present in {VER}')
        metap.append((f'type_{name}', 'type', m, name))
    for _, _, m, name in metap[1:]: assert len(m) > 0, name
    netp = start_net(stimp); up = F.crn_uniforms(SEEDS, stimp, 10000, SALT)
    allm = sorted({i for _, _, m, _ in metap for i in m})
    netp = F.subnet(FULL, np.union1d(netp.gidx, FULL.gidx[FULL.loc(allm)]))
    netp, datap = run_cached('pure', netp, stimp, up, [(m[0], m[2]) for m in metap], lamp)
    write('screen_types_pure', 'S_pure', lamp, metap, datap, T0)
    log(f'DONE total wall {time.time() - T0:.0f}s; conditions shiu {len(meta)} pure {len(metap)}; checks {checks}')


def unit_zeroing(net, stim, u, cand):
    """silence(k) must equal running a network whose k-row weights are literally set to 0, and the number of weights
    zeroed must equal k's out-degree in the full network. 3 candidates, 2 lambdas x 4 seeds."""
    rng = np.random.default_rng(1); ok = True
    outdeg = np.diff(FULL.indptr)
    top = max(cand, key=lambda f: outdeg[FULL.loc([f])[0]])
    picks = [top] + [int(x) for x in rng.choice(cand, 2, replace=False)]
    lam = [GRID['shiu']['lambda_hz'][3], GRID['shiu']['lambda_hz'][9]]; seeds = SEEDS[:4]
    for k in picks:
        l = net.loc([k])[0]
        nz_net = int(net.indptr[l + 1] - net.indptr[l])
        # out-degree inside the closure net must equal the full out-degree restricted to net members
        gi = FULL.loc([k])[0]; tgt = FULL.post[FULL.indptr[gi]:FULL.indptr[gi + 1]]
        in_net = np.isin(tgt, net.gidx).sum()
        ok &= (nz_net == in_net)
        net2 = F.Net(net.ver, net.gidx, net.fid, net.indptr, net.post, net.w.copy(), net.leak)
        net2.w[net.indptr[l]:net.indptr[l + 1]] = 0.0
        jobs_a = [dict(rate=float(x), trial=t, silence=[k]) for x in lam for t in seeds]
        jobs_b = [dict(rate=float(x), trial=t) for x in lam for t in seeds]
        ra = F.run(net, stim, jobs_a, trial_seeds=SEEDS, threads=THREADS, u=u)
        rb = F.run(net2, stim, jobs_b, trial_seeds=SEEDS, threads=THREADS, u=u)
        same = np.array_equal(ra['counts'], rb['counts']); ok &= same
        nzero = int((net2.w[net.indptr[l]:net.indptr[l + 1]] == 0).sum())
        log(f'zeroing check {k}: out-degree full {len(tgt)} in-closure {in_net} zeroed {nzero}; counts identical={same}')
        ok &= (nzero == nz_net)
    return bool(ok)


if __name__ == '__main__':
    main()
