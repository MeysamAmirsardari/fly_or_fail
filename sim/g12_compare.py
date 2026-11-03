# G1/G2: statistical comparison of fastlif (closure network, run_exact) with Brian2 reference spike files.
# usage: g12_compare.py <gate> <ver> <rate> <ref.parquet> <n_ref_trials> <silence_fid|0> <n_my_trials> <threads> [seed0]
# Metrics: per-neuron mean-rate Pearson r and OLS slope (fastlif ~ brian2) over neurons with mean > 5 Hz in either;
#          MN9 (L and R) fastlif mean vs Brian2 mean +- 95% CI (t-based); Welch t-test p-value as extra info;
#          active-set agreement: every neuron with mean >= 1 Hz in one simulator spikes at least once in the other.
import sys, json, time
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, '/home/user/fly_or_fail/sim')
import fastlif as F, reduce as R

gate, ver, rate, refp, nref, slid, nmy, threads = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], \
    int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])
seed0 = int(sys.argv[9]) if len(sys.argv) > 9 else 1000
sil = [slid] if slid else []
df = pd.read_parquet(refp, columns=['t', 'trial', 'flywire_id'])
assert df.trial.nunique() <= nref and df.trial.max() < nref, 'trial count mismatch'
ref_cnt = df.groupby(['flywire_id', 'trial']).size().unstack(fill_value=0).reindex(columns=range(nref), fill_value=0)
stim = F.sugar_right(ver)
t0 = time.time()
jobs = [dict(rate=rate, trial=seed0 + t, silence=sil) for t in range(nmy)]
net, res = R.run_exact(ver, stim, jobs, threads=threads)
wall = time.time() - t0
my_cnt = pd.DataFrame(res['counts'].T, index=net.fid)          # neurons x trials
ids = ref_cnt.index.union(my_cnt.index[my_cnt.sum(1) > 0])
missing = [i for i in ref_cnt.index if i not in set(net.fid.tolist())]
rb = ref_cnt.reindex(ids, fill_value=0).mean(1); rf = my_cnt.reindex(ids, fill_value=0).mean(1)
sel = (rb > 5) | (rf > 5)
r = stats.pearsonr(rb[sel], rf[sel])[0]
slope, icpt = np.polyfit(rb[sel].values, rf[sel].values, 1)
out = dict(gate=gate, ver=ver, rate=rate, silence=sil, ref=refp.split('/')[-1], n_ref_trials=nref, n_my_trials=nmy,
           n_neurons_gt5Hz=int(sel.sum()), pearson_r=round(float(r), 5), slope=round(float(slope), 4),
           intercept_hz=round(float(icpt), 3), ref_spikers_missing_from_closure=len(missing),
           closure=int(net.n), expansions=int(res['n_expansions']), wall_s=round(wall, 1))
ok = (r >= 0.99) and (0.97 <= slope <= 1.03)
for nm, f in (('MN9_L', F.MN9_L), ('MN9_R', F.MN9_R)):
    b = ref_cnt.reindex([f], fill_value=0).iloc[0].values.astype(float); m = my_cnt.loc[f].values.astype(float)
    se = b.std(ddof=1) / np.sqrt(len(b)); h = stats.t.ppf(0.975, len(b) - 1) * se
    inci = bool(abs(m.mean() - b.mean()) <= h)
    out[nm] = dict(brian2_mean=round(b.mean(), 2), ci95=[round(b.mean() - h, 2), round(b.mean() + h, 2)],
                   fastlif_mean=round(m.mean(), 2), fastlif_se=round(m.std(ddof=1) / np.sqrt(len(m)), 2),
                   within_ci=inci, welch_p=round(float(stats.ttest_ind(b, m, equal_var=False).pvalue), 4))
    ok &= inci
actb = set(rb.index[rb > 0]); actf = set(rf.index[rf > 0])
viol_b = [int(i) for i in actb - actf if rb[i] >= 1]; viol_f = [int(i) for i in actf - actb if rf[i] >= 1]
out.update(n_active_brian2=len(actb), n_active_fastlif=len(actf), only_brian2=len(actb - actf),
           only_fastlif=len(actf - actb), only_brian2_ge1Hz=viol_b, only_fastlif_ge1Hz=viol_f,
           max_rate_only_brian2=round(float(max([rb[i] for i in actb - actf], default=0)), 3),
           max_rate_only_fastlif=round(float(max([rf[i] for i in actf - actb], default=0)), 3))
ok &= (not viol_b) and (not viol_f)
out['PASS'] = bool(ok)
print('G12RESULT', json.dumps(out), flush=True)
