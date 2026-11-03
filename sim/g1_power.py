# High-power follow-up to G1 MN9 CI misses: N_my fastlif trials vs ALL independent Brian2 trial sets for (ver, 100 Hz).
# Per-neuron z = (mean_f - mean_b) / sqrt(se_f^2 + se_b^2) for neurons > 5 Hz; under H0 (same model) z ~ N(0,1)
# (marginally). Reports MN9, GRN rates, z distribution, and heterogeneity among the Brian2 sets themselves.
# usage: g1_power.py <ver> <rate> <n_my> <threads> <name=path:ntrials> ...
import sys, json, time
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, '/home/user/fly_or_fail/sim')
import fastlif as F, reduce as R

ver, rate, nmy, threads = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
sets = {}
for a in sys.argv[5:]:
    nm, rest = a.split('='); p, n = rest.rsplit(':', 1); n = int(n)
    d = pd.read_parquet(p, columns=['trial', 'flywire_id'])
    sets[nm] = d.groupby(['flywire_id', 'trial']).size().unstack(fill_value=0).reindex(columns=range(n), fill_value=0)
stim = F.sugar_right(ver)
t0 = time.time()
net, res = R.run_exact(ver, stim, [dict(rate=rate, trial=5000 + t) for t in range(nmy)], threads=threads)
my = pd.DataFrame(res['counts'].T, index=net.fid)
ids = my.index[my.sum(1) > 0]
for c in sets.values(): ids = ids.union(c.index)
B = pd.concat([c.reindex(ids, fill_value=0) for c in sets.values()], axis=1)
M = my.reindex(ids, fill_value=0)
mb, mf = B.mean(1), M.mean(1)
seb, sef = B.std(1, ddof=1) / np.sqrt(B.shape[1]), M.std(1, ddof=1) / np.sqrt(M.shape[1])
sel = (mb > 5) | (mf > 5)
z = ((mf - mb) / np.sqrt(seb ** 2 + sef ** 2))[sel]
out = dict(ver=ver, rate=rate, n_my=nmy, n_brian2=int(B.shape[1]), sets={k: int(v.shape[1]) for k, v in sets.items()},
           n_neurons=int(sel.sum()), z_mean=round(float(z.mean()), 3), z_sd=round(float(z.std()), 3),
           frac_abs_z_gt_1_96=round(float((z.abs() > 1.96).mean()), 3), frac_abs_z_gt_2_58=round(float((z.abs() > 2.58).mean()), 3),
           pearson_r=round(float(stats.pearsonr(mb[sel], mf[sel])[0]), 5),
           slope=round(float(np.polyfit(mb[sel], mf[sel], 1)[0]), 4),
           grn_rate_fastlif=round(float(M.reindex(stim).values.mean()), 3), grn_rate_brian2=round(float(B.reindex(stim).values.mean()), 3),
           wall_s=round(time.time() - t0, 1))
for nm, f in (('MN9_L', F.MN9_L), ('MN9_R', F.MN9_R)):
    if f not in ids: out[nm] = 'n/a'; continue
    per = {k: round(float(v.reindex([f], fill_value=0).iloc[0].mean()), 2) for k, v in sets.items()}
    groups = [v.reindex([f], fill_value=0).iloc[0].values for v in sets.values()]
    het = stats.f_oneway(*groups).pvalue if len(groups) > 1 else None
    b = B.loc[f].values; m = M.loc[f].values
    h = stats.t.ppf(.975, len(b) - 1) * b.std(ddof=1) / np.sqrt(len(b))
    out[nm] = dict(fastlif=round(m.mean(), 2), fastlif_se=round(m.std(ddof=1) / np.sqrt(len(m)), 2),
                   brian2_pooled=round(b.mean(), 2), ci95=[round(b.mean() - h, 2), round(b.mean() + h, 2)],
                   within_ci=bool(abs(m.mean() - b.mean()) <= h), welch_p=round(float(stats.ttest_ind(b, m, equal_var=False).pvalue), 4),
                   brian2_by_set=per, brian2_between_set_anova_p=None if het is None else round(float(het), 4),
                   z=round(float(z.get(f, np.nan)), 2))
# the most extreme neurons
zz = z.abs().sort_values(ascending=False)[:5]
out['top_abs_z'] = {str(int(k)): [round(float(z[k]), 2), round(float(mb[k]), 2), round(float(mf[k]), 2)] for k in zz.index}
print('G1POWER', json.dumps(out), flush=True)
