"""intact: INTACT (no silencing) dose-response curves with sim/fastlif on the exact closure network.

PROJECT_DESIGN v1.0 §5.3: lambda = 0, 5, ..., 400 Hz (81 levels) x seeds 0..59, CRN (fastlif salt 0).
NO silencing job is ever constructed here (asserted).

usage: python intact.py <ver> <input: shiu|pure> [threads]
output: analysis/out/intact_curve_<ver>_<input>.npz
"""
import sys, os, time, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sim'));sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

LAM = np.arange(0, 401, 5).astype(float)
SEEDS = list(range(60))


def run_curve(ver, inp, threads=2, lam=LAM, seeds=SEEDS, chunk=6, log=print):
    import fastlif as F, reduce as R
    full = F.load_full(ver)
    stim = C.INPUTS[inp](ver)
    stim_g = full.gidx[full.loc(stim)]
    clos0 = np.load(R.closure_path(ver))['gidx']
    C0 = np.union1d(np.union1d(clos0, stim_g), R.exc_out(full, stim_g))
    net = F.subnet(full, C0)
    u = F.crn_uniforms(seeds, stim, 10000, 0)
    parts = []; nexp = 0; t0 = time.time()
    for a in range(0, len(lam), chunk):
        lc = lam[a:a + chunk]
        jobs = [dict(rate=float(l), trial=int(t)) for l in lc for t in seeds]
        assert all('silence' not in j for j in jobs)                     # intact only
        net, res = R.run_exact(ver, stim, jobs, net=net, persist=False, log=log, trial_seeds=seeds, threads=threads, u=u)
        nexp += res['n_expansions']
        assert not res['nviol'].any()
        assert res['counts'].max() < 65535
        parts.append((net.gidx.copy(), res['counts'].astype(np.uint16), lc))
        del res
        log(f'[{ver}/{inp}] lam {lc[0]:.0f}-{lc[-1]:.0f} done, net {net.n}, {time.time()-t0:.0f}s')
    gidx = net.gidx
    counts = np.zeros((len(lam), len(seeds), len(gidx)), np.uint16)
    for (g, c, lc) in parts:
        pos = np.searchsorted(gidx, g); assert np.array_equal(gidx[pos], g)
        a = int(np.searchsorted(lam, lc[0]))
        assert c.max() < 65535
        counts[a:a + len(lc)][:, :, pos] = c.reshape(len(lc), len(seeds), len(g))
    fid = full.fid[gidx]
    return dict(lam=lam, seeds=np.array(seeds), counts=counts, fid=fid, gidx=gidx, stim=np.array(stim, np.int64),
                n_expansions=nexp, closure_start=clos0, wall=time.time() - t0)


def save_curve(ver, inp, r):
    fid = r['fid']; cnt = r['counts']
    mean_rates = cnt.mean(1).astype(np.float64)                         # (n_lam, n_neurons) Hz (1-s trials)
    ever = np.flatnonzero(cnt.reshape(-1, cnt.shape[2]).max(0) > 0)
    f2p = {int(f): i for i, f in enumerate(fid)}
    def readout(f):
        return cnt[:, :, f2p[f]].astype(np.float64) if f in f2p else np.zeros(cnt.shape[:2])   # outside closure: silent (exact)
    out = dict(lam=r['lam'], seeds=r['seeds'], fid=fid, gidx=r['gidx'], mean_rates=mean_rates,
               mn9_contra_id=C.MN9_CONTRA, mn9_ipsi_id=C.MN9_IPSI[ver],
               mn9_contra_rates=readout(C.MN9_CONTRA), mn9_ipsi_rates=readout(C.MN9_IPSI[ver]),
               active_fid=fid[ever], active_counts=cnt[:, :, ever], stim=r['stim'], n_expansions=r['n_expansions'],
               closure_start_gidx=r['closure_start'],
               meta=json.dumps(dict(ver=ver, input=inp, salt=0, T_s=1.0, wall_s=round(r['wall'], 1),
                                    fastlif_md5=C.md5(C.SIMDIR + 'fastlif.py'), reduce_md5=C.md5(C.SIMDIR + 'reduce.py'),
                                    created=time.strftime('%Y-%m-%d %H:%M:%S'),
                                    note='rates = spike counts in 1-s trials; mn9_*_rates shape (n_lam, n_seeds); '
                                         'active_counts shape (n_lam, n_seeds, n_active), active = >=1 spike anywhere')))
    p = C.OUT + f'intact_curve_{ver}_{inp}.npz'
    np.savez_compressed(p, **out)
    return p


if __name__ == '__main__':
    ver, inp = sys.argv[1], sys.argv[2]
    th = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    r = run_curve(ver, inp, threads=th, log=lambda s: print(s, flush=True))
    p = save_curve(ver, inp, r)
    print('saved', p, 'expansions', r['n_expansions'], 'wall', round(r['wall'], 1), flush=True)
