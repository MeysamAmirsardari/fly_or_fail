# G3: reduced (closure) network vs FULL network inside fastlif: bit-identical spike trains for the same seeds.
# Part A: real closure; intact at 4 rates + >= 24 random silencing conditions (exc + inh singles, pairs, 5-sets,
#         top inhibitory neurons) at 100 and 400 Hz.  run_exact (with expansion) vs full network.
# Part B: deliberately TRUNCATED closure (stim + active only, no out-neighbours) -> boundary check must fire, and
#         the expanded result must still be bit-identical to the full network.
# usage: g3_reduction.py <ver> <threads>
import sys, json, time
import numpy as np
sys.path.insert(0, '/home/user/fly_or_fail/sim')
import fastlif as F, reduce as R

ver, threads = sys.argv[1], int(sys.argv[2])
full = F.load_full(ver); stim = F.sugar_right(ver)
rng = np.random.default_rng(12345)
# neuron sign = sign of its outgoing weights
act_res = F.run(full, stim, [dict(rate=400, trial=100 + t) for t in range(2)], threads=threads)
act = np.flatnonzero(act_res['counts'].sum(0) > 0)
sgn = np.array([np.sign(full.wint[full.indptr[i]:full.indptr[i + 1]]).mean() if full.indptr[i + 1] > full.indptr[i] else 0
                for i in act])
exc = act[sgn > 0]; inh = act[sgn < 0]
rate_inh = act_res['counts'].sum(0)[inh]
fidl = lambda ix: [int(full.fid[i]) for i in ix]
conds = [('intact', [])]
conds += [(f'exc1_{k}', fidl([i])) for k, i in enumerate(rng.choice(exc, 8, replace=False))]
conds += [(f'inh1_{k}', fidl([i])) for k, i in enumerate(rng.choice(inh, 8, replace=False))]
conds += [(f'topinh_{k}', fidl([i])) for k, i in enumerate(inh[np.argsort(-rate_inh)[:3]])]
conds += [('topinh_5set', fidl(inh[np.argsort(-rate_inh)[:5]]))]
conds += [(f'pair_{k}', fidl(rng.choice(act, 2, replace=False))) for k in range(4)]
conds += [(f'set5_{k}', fidl(rng.choice(act, 5, replace=False))) for k in range(2)]
conds += [('inh_all20', fidl(inh[np.argsort(-rate_inh)[:20]]))]
jobs = [dict(cond='intact', silence=[], rate=r, trial=t) for r in (50, 100, 200, 400) for t in (0, 1)]
jobs += [dict(cond=c, silence=s, rate=r, trial=t) for c, s in conds[1:] for r in (100, 400) for t in (2, 3)]
trials = sorted({j['trial'] for j in jobs})
print(f'{ver}: {len(conds) - 1} silencing conditions, {len(jobs)} jobs; active {len(act)} (exc {len(exc)}, inh {len(inh)})',
      flush=True)


def compare(tag, net, res, ref):
    pos = net.gidx                                           # closure local -> global
    cf = ref['counts']; cr = np.zeros_like(cf); cr[:, pos] = res['counts']
    ok_counts = np.array_equal(cf, cr)
    outside = np.ones(full.n, bool); outside[pos] = False
    out_spk = int(cf[:, outside].sum())
    ok_trains = all(np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) for a, b in zip(res['spikes'], ref['spikes']))
    n_spk = int(cf.sum())
    r = dict(test=tag, ver=ver, n_jobs=len(jobs), closure_final=int(net.n), expansions=int(res.get('n_expansions', 0)),
             counts_identical=bool(ok_counts), spike_trains_identical=bool(ok_trains), total_spikes=n_spk,
             spikes_outside_closure_in_full=out_spk, residual_violations=int((res['nviol'] > 0).sum()))
    print('G3RESULT', json.dumps(r), flush=True)
    return r


t0 = time.time()
ref = F.run(full, stim, jobs, trial_seeds=trials, record='all', rec_cap=60000, threads=threads)
t_full = time.time() - t0
print(f'full network: {len(jobs)} jobs in {t_full:.1f} s', flush=True)
# A: real closure (persisted expansions allowed)
t0 = time.time()
netA, resA = R.run_exact(ver, stim, jobs, trial_seeds=trials, record='all', rec_cap=60000, threads=threads)
t_red = time.time() - t0
print(f'closure: {len(jobs)} jobs in {t_red:.1f} s (incl. expansions)', flush=True)
compare('A_real_closure', netA, resA, ref)
# B: truncated closure, not persisted
C_trunc = np.union1d(full.gidx[full.loc(stim)], act)
netB0 = F.subnet(full, C_trunc)
print('truncated closure size', netB0.n, 'leaking', int(netB0.leak.sum()), flush=True)
netB, resB = R.run_exact(ver, stim, jobs, net=netB0, persist=False, trial_seeds=trials, record='all', rec_cap=60000,
                         threads=threads)
compare('B_truncated_closure_expanded', netB, resB, ref)
print(json.dumps(dict(speed_full_s_per_job=t_full / len(jobs), speed_closure_s_per_job=t_red / len(jobs), threads=threads)))
