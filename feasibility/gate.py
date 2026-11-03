# REPRODUCTION GATE: our Brian2 reference runs (v630) vs the authors' stored outputs in results/example/.
# Criteria are FIXED HERE, before looking at the results (my choice; stated in the report):
#  G1  MN9 (both v630 IDs) x 5 conditions = 10 comparisons: Welch 95% CI of (ours - stored) per-trial rate. PASS if all 10 Bonferroni-adjusted
#      (alpha=0.05/10, i.e. 99.5% CI) intervals contain 0. (Unadjusted 95% CIs and relative differences also reported.)
#  G2  per-neuron mean-rate agreement over the union of neurons spiking in either dataset, excluding the 21 Poisson-driven GRNs:
#      Pearson r >= 0.95 AND Spearman rho >= 0.80 AND ours >= 5th percentile of the stored-vs-stored 15/15 trial-split reference, in all 5 conditions.
#  G3  active set (mean rate >= 1 Hz) Jaccard >= 0.85 AND >= 5th pct of the stored 15/15 split reference, in all 5 conditions.
# Gate = PASS iff G1, G2, G3 all pass.
import sys, numpy as np, pandas as pd
from scipy import stats
import simlib as S
R = '/home/user/external/Drosophila_brain_model/results/example/'
OURS = '/home/user/fly_or_fail/feasibility/out/ref/v630/'
SUF = sys.argv[1] if len(sys.argv) > 1 else ''     # '' = primary gate (seeds 0-19); '_rep2' = independent replicate (seeds 20-39), same criteria
conds = [('200 Hz', 'sugarR.parquet', 'sugarR_200Hz.parquet'), ('100 Hz', 'sugarR_100Hz.parquet', f'sugarR_100Hz{SUF}.parquet')] + \
        [(f'100 Hz silence {s}', f'sugarR-{s}.parquet', f'sugarR-{s}_100Hz{SUF}.parquet') for s in (720575940617937543, 720575940621754367, 720575940622695448)]
GRN = set(S.sugar_right('v630'))
def counts(df, ntr):
    assert df.trial.min() == 0 and df.trial.max() == ntr - 1, (df.trial.min(), df.trial.max(), ntr)
    ct = pd.crosstab(df.flywire_id, df.trial).reindex(columns=range(ntr), fill_value=0)
    return ct
def welch(a, b, alpha):
    m1, m2 = a.mean(), b.mean(); v1, v2 = a.var(ddof=1), b.var(ddof=1); n1, n2 = len(a), len(b)
    se = np.sqrt(v1 / n1 + v2 / n2); dfw = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    tc = stats.t.ppf(1 - alpha / 2, dfw); d = m1 - m2
    return d, d - tc * se, d + tc * se, dfw
def tci(a, alpha=0.05):
    m = a.mean(); se = a.std(ddof=1) / np.sqrt(len(a)); tc = stats.t.ppf(1 - alpha / 2, len(a) - 1); return m, m - tc * se, m + tc * se
def metrics(ca, cb, na, nb):
    """ca, cb: count matrices (neuron x trial). rates = mean count (t_run = 1 s)."""
    ra = ca.mean(axis=1); rb = cb.mean(axis=1); u = ra.index.union(rb.index)
    ra = ra.reindex(u, fill_value=0.0); rb = rb.reindex(u, fill_value=0.0)
    keep = ~u.isin(GRN); ra, rb = ra[keep], rb[keep]
    pr = stats.pearsonr(ra, rb)[0]; sr = stats.spearmanr(ra, rb)[0]
    A = set(ra.index[ra >= 1]); B = set(rb.index[rb >= 1]); jac = len(A & B) / len(A | B)
    return pr, sr, jac, len(A), len(B), len(A & B)
rng = np.random.default_rng(12345)
rows = []; MN = {'MN9_L(...265)': S.MN9_L, 'MN9_R(...262)': S.MN9_R}
print(f'GATE (suffix "{SUF}"): ours (v630, 20 trials) vs authors stored (30 trials)\n')
for name, fs, fo in conds:
    st = pd.read_parquet(R + fs); our = pd.read_parquet(OURS + fo)
    cs, co = counts(st, 30), counts(our, 20)
    print(f'=== {name}: stored {fs} ({len(st)} spike rows, exp_name={st.exp_name.iloc[0]}) vs ours {fo} ({len(our)} rows)')
    for mn, mid in MN.items():
        a = co.loc[mid].values.astype(float) if mid in co.index else np.zeros(20)
        b = cs.loc[mid].values.astype(float) if mid in cs.index else np.zeros(30)
        ma, la, ha = tci(a); mb, lb, hb = tci(b)
        d, dl, dh, dfw = welch(a, b, 0.05); _, dl2, dh2, _ = welch(a, b, 0.005)
        ok = dl2 <= 0 <= dh2
        print(f'  {mn}: ours {ma:.2f} Hz [95% CI {la:.2f}, {ha:.2f}] (sd {a.std(ddof=1):.2f}, n=20) | stored {mb:.2f} [{lb:.2f}, {hb:.2f}] (sd {b.std(ddof=1):.2f}, n=30) | diff {d:+.2f} [95% {dl:+.2f}, {dh:+.2f}] [99.5% {dl2:+.2f}, {dh2:+.2f}] rel {100*d/mb:+.1f}% -> G1 {"ok" if ok else "FAIL"}')
        rows.append(dict(cond=name, neuron=mn, ours=ma, stored=mb, G1=ok))
    pr, sr, jac, nA, nB, nI = metrics(co, cs, 20, 30)
    # reference: stored-vs-stored 15/15 trial splits
    ref = []
    for _ in range(1000):
        perm = rng.permutation(30); ref.append(metrics(cs.iloc[:, perm[:15]], cs.iloc[:, perm[15:]], 15, 15)[:3])
    ref = np.array(ref); p5 = np.percentile(ref, 5, axis=0); med = np.median(ref, axis=0)
    rk = [100 * (ref[:, j] < v).mean() for j, v in enumerate((pr, sr, jac))]
    g2 = (pr >= 0.95) and (sr >= 0.80) and (pr >= p5[0]) and (sr >= p5[1]); g3 = (jac >= 0.85) and (jac >= p5[2])
    print(f'  per-neuron (excl. 21 driven GRNs; union of spiking neurons n={len(set(co.index)|set(cs.index))}): Pearson r {pr:.4f} (ref 15/15 median {med[0]:.4f}, 5th pct {p5[0]:.4f}); Spearman {sr:.4f} (ref {med[1]:.4f}, {p5[1]:.4f}); percentile rank of ours within reference splits: r {rk[0]:.0f}, rho {rk[1]:.0f}, Jaccard {rk[2]:.0f} -> G2 {"ok" if g2 else "FAIL"}')
    print(f'  active set (>=1 Hz): ours {nA}, stored {nB}, intersection {nI}, Jaccard {jac:.4f} (ref median {med[2]:.4f}, 5th pct {p5[2]:.4f}) -> G3 {"ok" if g3 else "FAIL"}')
    # >=1 spike sets (like-for-like trial count: stored first 20 trials)
    s20 = set(cs.index[(cs.iloc[:, :20].sum(axis=1) > 0)]) - GRN; o20 = set(co.index[co.sum(axis=1) > 0]) - GRN
    print(f'  active set (>=1 spike in 20 trials, excl. GRNs): ours {len(o20)}, stored(first 20 trials) {len(s20)}, Jaccard {len(o20&s20)/len(o20|s20):.4f}; all-30-trial stored: {len(set(cs.index[cs.sum(axis=1)>0])-GRN)}')
    # per-neuron z diagnostic (conservative Poisson variance floor)
    u = co.index.union(cs.index).difference(list(GRN)); xa = co.reindex(u, fill_value=0); xb = cs.reindex(u, fill_value=0)
    va = np.maximum(xa.var(axis=1, ddof=1), (xa.mean(axis=1) + xb.mean(axis=1)) / 2); vb = np.maximum(xb.var(axis=1, ddof=1), (xa.mean(axis=1) + xb.mean(axis=1)) / 2)
    z = (xa.mean(axis=1) - xb.mean(axis=1)) / np.sqrt(va / 20 + vb / 30 + 1e-12)
    print(f'  diagnostic per-neuron z (variance floored at Poisson): |z|>3: {(z.abs()>3).sum()} of {len(z)} (expected ~{0.0027*len(z):.1f} if identical); max |z| {z.abs().max():.2f}')
    big = z.abs().sort_values(ascending=False).head(3)
    print('  top |z| neurons:', [(int(i), round(float(z[i]), 2), round(float(xa.loc[i].mean()), 2), round(float(xb.loc[i].mean()), 2)) for i in big.index])
    rows[-1].update(G2=g2, G3=g3); rows[-2].update(G2=g2, G3=g3)
df = pd.DataFrame(rows)
print('\nSUMMARY: G1 all', bool(df.G1.all()), '| G2 all', bool(df.G2.all()), '| G3 all', bool(df.G3.all()), '=> GATE', 'PASS' if df.G1.all() and df.G2.all() and df.G3.all() else 'FAIL')
