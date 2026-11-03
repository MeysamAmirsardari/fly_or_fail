# Supplementary: pool the primary (seeds 0-19) and replicate (seeds 20-39) reference runs -> 40 trials per condition vs stored 30. Same metrics as gate.py (no new criteria).
import numpy as np, pandas as pd
from scipy import stats
import simlib as S
R = '/home/user/external/Drosophila_brain_model/results/example/'; O = '/home/user/fly_or_fail/feasibility/out/ref/v630/'
GRN = set(S.sugar_right('v630'))
conds = [('200 Hz', 'sugarR.parquet', 'sugarR_200Hz')] + [('100 Hz', 'sugarR_100Hz.parquet', 'sugarR_100Hz')] + \
        [(f'100 Hz silence {s}', f'sugarR-{s}.parquet', f'sugarR-{s}_100Hz') for s in (720575940617937543, 720575940621754367, 720575940622695448)]
def ct(df, n): return pd.crosstab(df.flywire_id, df.trial).reindex(columns=range(n), fill_value=0)
for name, fs, fo in conds:
    cs = ct(pd.read_parquet(R + fs), 30)
    a = pd.read_parquet(O + fo + '.parquet'); b = pd.read_parquet(O + fo + '_rep2.parquet'); b = b.assign(trial=b.trial + 20)   # rep2 trials are numbered 0-19 in-file; seeds 20-39
    co = ct(pd.concat([a, b]), 40)
    ra, rb = co.mean(axis=1), cs.mean(axis=1); u = ra.index.union(rb.index); ra, rb = ra.reindex(u, fill_value=0), rb.reindex(u, fill_value=0)
    k = ~u.isin(GRN); ra, rb = ra[k], rb[k]
    A = set(ra.index[ra >= 1]); B = set(rb.index[rb >= 1])
    s = f'{name}: pooled 40 trials vs stored 30 | Pearson {stats.pearsonr(ra, rb)[0]:.4f} Spearman {stats.spearmanr(ra, rb)[0]:.4f} | active(>=1Hz) {len(A)} vs {len(B)} Jaccard {len(A&B)/len(A|B):.4f} |'
    for nm, mid in (('MN9_L', S.MN9_L), ('MN9_R', S.MN9_R)):
        x, y = co.loc[mid].values.astype(float), cs.loc[mid].values.astype(float)
        d = x.mean() - y.mean(); se = np.sqrt(x.var(ddof=1) / 40 + y.var(ddof=1) / 30)
        v1, v2 = x.var(ddof=1) / 40, y.var(ddof=1) / 30; dfw = (v1 + v2) ** 2 / (v1 ** 2 / 39 + v2 ** 2 / 29); tc = stats.t.ppf(0.975, dfw)
        s += f' {nm} ours {x.mean():.2f} stored {y.mean():.2f} diff {d:+.2f} [95% {d-tc*se:+.2f}, {d+tc*se:+.2f}] |'
    print(s)
