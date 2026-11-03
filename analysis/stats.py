"""stats.py -- pre-registered statistics for PROJECT_DESIGN.md v1.0 (commit e051e08), Sec. 7.

P-A (grouped, nested bootstrap of delta-rho with the competitor max re-selected per resample),
the Hotelling-Williams / Steiger dependent-correlation sensitivity test, S1-S5, Holm, partial
Spearman, RQ1 per-lambda Spearman/AUPRC, RQ2 collapse fraction with a cell-type-clustered CI,
S6 summation with a seed bootstrap and trend test, and the Sec. 6.5 pair metrics.

Nested-bootstrap scheme for P-A / S1 / S2 (documented in ANALYSIS_VALIDATION.md, "Nested bootstrap"):
  level 1 (seeds):      R replicates of f-hat for ALL conditions, from curves.seed_bootstrap_fhat:
                        one seed draw per replicate shared by every condition AND the training
                        intact curve (CRN makes the seed the common unit), O-hat and weights refit.
  level 2 (cell types): B cluster resamples of cell-type groups.
  pairing:              resample b uses seed replicate r(b) = b mod R.  With R = B (default) every
                        cluster resample gets its own, independent seed replicate, which is exactly a
                        two-factor (cell type x seed) bootstrap; nothing is approximated except that
                        the structural predictors are held fixed (they are STRUCT's, computed from
                        separate intact runs).  R < B recycles seed replicates (reported).
"""
from __future__ import annotations

import itertools
import math
import warnings

import numpy as np
from scipy import stats

B_DEFAULT = 2000


# ------------------------------------------------------------------------------------------ ranks
def rank_avg(a, axis=-1):
    """Average ranks (ties -> mid-ranks) along axis."""
    return stats.rankdata(a, method='average', axis=axis)


def spearman(x, y):
    """Spearman rho as the Pearson correlation of average ranks (equals scipy.stats.spearmanr)."""
    rx, ry = rank_avg(np.asarray(x, float)), rank_avg(np.asarray(y, float))
    return _pearson_rows(rx[None, :], ry)[0]


def _pearson_rows(X, y):
    """Pearson correlation of each row of X (k, n) with y (n,).  NaN where a row is constant."""
    Xc = X - X.mean(-1, keepdims=True)
    yc = y - y.mean(-1, keepdims=True)
    num = (Xc * yc).sum(-1)
    den = np.sqrt((Xc ** 2).sum(-1) * (yc ** 2).sum(-1))
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where(den > 0, num / den, np.nan)


# ------------------------------------------------------------------------------------------ groups
def make_groups(cell_type, homolog=None):
    """Cluster units for the cell-type bootstrap (Sec. 7.1).  `cell_type`: per-neuron label or None/NaN.
    `homolog`: optional per-neuron label of the nearest annotated homolog (used only where cell_type is
    missing and the mapping is unambiguous -- STRUCT/ENG decide that and pass None otherwise).
    Returns (integer group codes, number of singletons)."""
    ct = np.asarray(cell_type, object)
    hm = np.full(ct.shape, None, object) if homolog is None else np.asarray(homolog, object)

    def missing(v):
        return v is None or (isinstance(v, float) and np.isnan(v)) or v == ''

    lab = []
    for i, (c, h) in enumerate(zip(ct, hm)):
        if not missing(c):
            lab.append(('ct', c))
        elif not missing(h):
            lab.append(('ct', h))
        else:
            lab.append(('single', i))
    uniq = {l: j for j, l in enumerate(dict.fromkeys(lab))}
    codes = np.array([uniq[l] for l in lab])
    n_single = int(sum(1 for l in uniq if l[0] == 'single'))
    return codes, n_single


def _group_index(groups):
    groups = np.asarray(groups)
    u, inv = np.unique(groups, return_inverse=True)
    members = [np.flatnonzero(inv == g) for g in range(len(u))]
    return members


def cluster_resample(members, rng):
    """One cluster (cell-type) bootstrap resample: draw G groups with replacement, return unit indices."""
    G = len(members)
    pick = rng.integers(0, G, G)
    return np.concatenate([members[g] for g in pick])


# ------------------------------------------------------------------------------------------ P-A, S1, S2
def delta_rho(x_star, competitors: dict, f):
    """Delta rho = rho_s(X*, f) - max_{X in family} rho_s(X, f), signed correlations (Sec. 7.1)."""
    rs = spearman(x_star, f)
    rc = {k: spearman(v, f) for k, v in competitors.items()}
    kbest = max(rc, key=lambda k: (rc[k], ))
    return dict(delta=rs - rc[kbest], rho_star=rs, rho_comp=rc, best=kbest)


def grouped_bootstrap_delta_rho(x_star, competitors: dict, fhat, groups, fhat_reps=None, B=B_DEFAULT,
                                seed=20261104, alpha=0.05, mask=None):
    """P-A / S1 / S2 machinery.

    x_star: (N,) focal predictor; competitors: {name: (N,)}; fhat: (N,) point estimates; groups: (N,)
    cluster labels; fhat_reps: optional (R, N) seed-bootstrap replicates (nested level); mask: optional
    (N,) bool subset (e.g. shift class only), applied before resampling.
    Returns point estimate, bootstrap distribution, one-sided 95% lower bound (5th percentile; the
    pre-registered decision), two-sided 95% percentile CI, one-sided bootstrap p = (1 + #{d_b <= 0})/(B+1),
    and how often each competitor was the re-selected max."""
    x_star = np.asarray(x_star, float); fhat = np.asarray(fhat, float); groups = np.asarray(groups)
    names = list(competitors)
    Xc = np.vstack([np.asarray(competitors[k], float) for k in names])
    if mask is not None:
        mask = np.asarray(mask, bool)
        x_star, fhat, groups, Xc = x_star[mask], fhat[mask], groups[mask], Xc[:, mask]
        if fhat_reps is not None:
            fhat_reps = np.asarray(fhat_reps)[:, mask]
    for arr, nm in ((x_star, 'x_star'), (fhat, 'fhat'), (Xc, 'competitors')):
        if np.isnan(arr).any():
            raise ValueError(f'NaN in {nm}')
    pt = delta_rho(x_star, dict(zip(names, Xc)), fhat)
    members = _group_index(groups)
    rng = np.random.default_rng(seed)
    R = 0 if fhat_reps is None else fhat_reps.shape[0]
    d = np.empty(B); sel = np.zeros(len(names), int); rs_b = np.empty(B); rc_b = np.empty(B)
    for b in range(B):
        idx = cluster_resample(members, rng)
        fb = (fhat if R == 0 else fhat_reps[b % R])[idx]
        ry = rank_avg(fb)
        r_all = _pearson_rows(rank_avg(np.vstack([x_star[idx][None, :], Xc[:, idx]]), axis=1), ry)
        rc = r_all[1:]
        j = int(np.nanargmax(rc))
        sel[j] += 1
        d[b] = r_all[0] - rc[j]; rs_b[b] = r_all[0]; rc_b[b] = rc[j]
    lo1 = float(np.percentile(d, 100 * alpha))
    lo2, hi2 = np.percentile(d, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return dict(delta=pt['delta'], rho_star=pt['rho_star'], rho_comp=pt['rho_comp'], best=pt['best'],
                boot=d, lower_one_sided=lo1, ci_two_sided=(float(lo2), float(hi2)),
                p_one_sided=float((1 + (d <= 0).sum()) / (B + 1)), decision=bool(lo1 > 0),
                selected_freq=dict(zip(names, sel / B)), n=int(fhat.size), n_groups=len(members),
                seed_reps=R, recycled=bool(0 < R < B))


def disattenuate(rho, reliability):
    """rho / sqrt(reliability of f-hat) (predictor treated as error-free); NaN if reliability <= 0."""
    return rho / math.sqrt(reliability) if reliability > 0 else float('nan')


def split_half_reliability(f_odd, f_even):
    """Spearman and Pearson split-half correlations and the Spearman-Brown full-length reliability."""
    r_s = spearman(f_odd, f_even)
    r_p = float(np.corrcoef(f_odd, f_even)[0, 1])
    sb = lambda r: 2 * r / (1 + r)
    return dict(r_spearman=r_s, r_pearson=r_p, rel_spearman_brown=sb(r_s), rel_pearson_sb=sb(r_p))


# ------------------------------------------------------------------------------------------ dependent r
def williams_t(r12, r13, r23, n):
    """Williams' (1959) t for H0: rho12 = rho13 (variable 1 shared), Steiger (1980) eq. 7.
    df = n - 3.  Returns (t, one-sided p for r12 > r13, two-sided p)."""
    detR = 1 - r12 ** 2 - r13 ** 2 - r23 ** 2 + 2 * r12 * r13 * r23
    rbar = 0.5 * (r12 + r13)
    t = (r12 - r13) * math.sqrt((n - 1) * (1 + r23)) / math.sqrt(
        2 * ((n - 1) / (n - 3)) * detR + rbar ** 2 * (1 - r23) ** 3)
    df = n - 3
    return t, float(stats.t.sf(t, df)), float(2 * stats.t.sf(abs(t), df))


def steiger_z(r12, r13, r23, n):
    """Steiger (1980) eq. 14 Z for dependent correlations with pooled rbar.  Returns (Z, p1, p2)."""
    z12, z13 = np.arctanh(r12), np.arctanh(r13)
    rbar = 0.5 * (r12 + r13)
    psi = r23 * (1 - 2 * rbar ** 2) - 0.5 * rbar ** 2 * (1 - 2 * rbar ** 2 - r23 ** 2)
    c = psi / (1 - rbar ** 2) ** 2
    Z = (z12 - z13) * math.sqrt(n - 3) / math.sqrt(2 - 2 * c)
    return float(Z), float(stats.norm.sf(Z)), float(2 * stats.norm.sf(abs(Z)))


def dependent_corr_test(x_star, x_comp, f, n_eff=None):
    """Sensitivity test of P-A: Spearman correlations plugged into Williams' t and Steiger's Z.
    n_eff defaults to the number of units; pass the number of cell-type groups to respect clustering."""
    r12, r13, r23 = spearman(x_star, f), spearman(x_comp, f), spearman(x_star, x_comp)
    n = len(f) if n_eff is None else int(n_eff)
    t, p1, p2 = williams_t(r12, r13, r23, n)
    z, zp1, zp2 = steiger_z(r12, r13, r23, n)
    return dict(r_star=r12, r_comp=r13, r_between=r23, n=n, williams_t=t, williams_p_one=p1,
                williams_p_two=p2, steiger_z=z, steiger_p_one=zp1, steiger_p_two=zp2)


# ------------------------------------------------------------------------------------------ S3
def s3_dominators(classes_of_dominators, min_n=5):
    """S3: proportion of dominators in class 'no-recovery' > 0.5, exact one-sided binomial.
    Run only if >= min_n dominators, else descriptive (p = None)."""
    c = list(classes_of_dominators)
    n = len(c); k = sum(1 for x in c if x == 'no-recovery')
    if n < min_n:
        return dict(n=n, k=k, run=False, p=None, prop=(k / n if n else float('nan')))
    p = float(stats.binomtest(k, n, 0.5, alternative='greater').pvalue)
    return dict(n=n, k=k, run=True, p=p, prop=k / n)


# ------------------------------------------------------------------------------------------ S4
def kendall_tau_b(x, y):
    """Kendall tau_b with ties in either variable (O(n^2); n is 7 here)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    n = len(x)
    C = D = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = np.sign(x[i] - x[j]), np.sign(y[i] - y[j])
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tx += 1
            elif dy == 0:
                ty += 1
            elif dx == dy:
                C += 1
            else:
                D += 1
    den = math.sqrt((C + D + tx) * (C + D + ty))
    return (C - D) / den if den > 0 else float('nan')


S4_TYPES = ('Rattle', 'Usnea', 'Zorro', 'Clavicle', 'G2N-1', 'FMIn', 'Phantom')
S4_TIERS = {'Rattle': 2, 'Usnea': 2, 'Zorro': 1, 'Clavicle': 1, 'G2N-1': 1, 'FMIn': 1, 'Phantom': 0}
S4_TIERS_SENS = {**S4_TIERS, 'G2N-1': 0.5, 'FMIn': 0.5}
S5_LAYER3 = ('Bract', 'Fdg', 'Roundup')


def s4_exact(f_by_type: dict, tiers: dict = S4_TIERS):
    """S4: tau_b(f, tier) with an exact permutation null over all n! assignments of the f values to types.
    p = #{perm: tau_b >= observed}/n! (ties at the observed value counted, i.e. the exact upper tail)."""
    names = list(tiers)
    f = np.array([f_by_type[k] for k in names], float)
    t = np.array([tiers[k] for k in names], float)
    obs = kendall_tau_b(f, t)
    null = np.array([kendall_tau_b(f[list(p)], t) for p in itertools.permutations(range(len(names)))])
    p = float(np.mean(null >= obs - 1e-12))
    return dict(tau_b=obs, p=p, n_perm=len(null), null=null)


def s4_top2(f_by_type: dict, top=('Rattle', 'Usnea')):
    """Top-2 exact test: indicator that the two largest f are exactly `top`; exact permutation p
    (= 1/21 when the indicator is 1 and the 7 values are distinct)."""
    names = list(f_by_type)
    f = np.array([f_by_type[k] for k in names], float)
    tset = {names.index(k) for k in top}

    def ind(vals):
        order = np.argsort(-vals, kind='stable')
        # strict: the two top values must exceed every other value
        third = vals[order[2]] if len(vals) > 2 else -np.inf
        return float(set(order[:2]) == tset and vals[order[1]] > third)

    obs = ind(f)
    null = np.array([ind(f[list(p)]) for p in itertools.permutations(range(len(names)))])
    return dict(indicator=obs, p=float(np.mean(null >= obs)))


# ------------------------------------------------------------------------------------------ S5
def wilcoxon_exact_greater(x, y):
    """One-sided exact Wilcoxon rank-sum (H1: x stochastically larger than y) by enumerating all
    C(n+m, n) allocations of the pooled mid-ranks.  Returns W = rank sum of x and exact p."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    pooled = np.concatenate([x, y])
    r = rank_avg(pooled)
    n = len(x)
    W = r[:n].sum()
    sums = np.array([r[list(c)].sum() for c in itertools.combinations(range(len(pooled)), n)])
    p = float(np.mean(sums >= W - 1e-9))
    return dict(W=float(W), p=p, n_alloc=len(sums))


def s5_layer(f_second: dict, f_layer3: dict):
    return wilcoxon_exact_greater(list(f_second.values()), list(f_layer3.values()))


# ------------------------------------------------------------------------------------------ Holm
def holm(pvals: dict, alpha=0.05):
    """Holm step-down.  None entries (tests not run, e.g. S3 with < 5 dominators) are left out of the
    family.  Returns {name: (adjusted p, reject)}."""
    items = [(k, p) for k, p in pvals.items() if p is not None]
    m = len(items)
    order = sorted(items, key=lambda kv: kv[1])
    adj, running = {}, 0.0
    for i, (k, p) in enumerate(order):
        running = max(running, min(1.0, (m - i) * p))
        adj[k] = running
    out = {k: (adj[k], adj[k] <= alpha) for k, _ in items}
    for k, p in pvals.items():
        if p is None:
            out[k] = (None, None)
    return out


# ------------------------------------------------------------------------------------------ partial rho
def partial_spearman(x, y, covariates):
    """Partial Spearman: rank-transform x, y and every covariate, residualise the ranks of x and y on
    the covariate ranks (OLS with intercept), correlate residuals.  t-test with df = n - 2 - k."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    Z = np.column_stack([rank_avg(np.asarray(c, float)) for c in covariates]) if len(covariates) else \
        np.empty((len(x), 0))
    Z = np.column_stack([np.ones(len(x)), Z])
    rx, ry = rank_avg(x), rank_avg(y)
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    r = float(np.corrcoef(ex, ey)[0, 1])
    df = len(x) - 2 - (Z.shape[1] - 1)
    t = r * math.sqrt(df / max(1e-300, 1 - r * r))
    return dict(r=r, df=df, p_two=float(2 * stats.t.sf(abs(t), df)))


# ------------------------------------------------------------------------------------------ RQ1
def average_precision(labels, scores):
    """AUPRC as average precision (step-wise; ties in scores broken pessimistically-neutral by grouping):
    AP = sum_k (R_k - R_{k-1}) P_k over distinct score thresholds, high score = predicted positive."""
    y = np.asarray(labels, bool); s = np.asarray(scores, float)
    if y.sum() == 0:
        return float('nan')
    order = np.argsort(-s, kind='mergesort')
    s, y = s[order], y[order]
    distinct = np.r_[np.flatnonzero(np.diff(s)), len(s) - 1]
    tp = np.cumsum(y)[distinct]
    fp = (distinct + 1) - tp
    prec = tp / (tp + fp)
    rec = tp / y.sum()
    return float(np.sum(np.diff(np.r_[0.0, rec]) * prec))


def rq1_per_lambda(N, predictors: dict, threshold=0.2):
    """RQ1: per grid lambda, Spearman(predictor, N_k(lambda)) and AUPRC for the label N_k >= 0.2.
    N: (K, L).  Rows with NaN N at a lambda are dropped at that lambda.  Returns a list of dicts."""
    N = np.asarray(N, float)
    out = []
    for name, x in predictors.items():
        x = np.asarray(x, float)
        for j in range(N.shape[1]):
            ok = np.isfinite(N[:, j]) & np.isfinite(x)
            lab = N[ok, j] >= threshold
            out.append(dict(predictor=name, j=j, n=int(ok.sum()), prevalence=float(lab.mean()),
                            rho=spearman(x[ok], N[ok, j]), auprc=average_precision(lab, x[ok])))
    return out


# ------------------------------------------------------------------------------------------ RQ2
def clustered_fraction(success, eligible, groups, B=B_DEFAULT, seed=7, alpha=0.05):
    """Fraction sum(success & eligible)/sum(eligible) with a cell-type cluster-bootstrap percentile CI
    (ratio estimator; resamples with no eligible unit are skipped and counted)."""
    s = np.asarray(success, bool); e = np.asarray(eligible, bool)
    members = _group_index(groups)
    rng = np.random.default_rng(seed)
    est = (s & e).sum() / e.sum() if e.sum() else float('nan')
    bs = []
    skipped = 0
    for _ in range(B):
        idx = cluster_resample(members, rng)
        den = e[idx].sum()
        if den == 0:
            skipped += 1
            continue
        bs.append((s[idx] & e[idx]).sum() / den)
    lo, hi = np.percentile(bs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return dict(est=float(est), ci=(float(lo), float(hi)), n_eligible=int(e.sum()), skipped=skipped)


def rq2_summary(cls, groups, is_grn=None, B=B_DEFAULT, seed=7):
    """Collapse fraction = #shift / #{shift, gain, other} (informative, effect-bearing, non-GRN;
    no-recovery is its own class and is excluded from the denominator -- choice C-8; the alternative
    including no-recovery is also returned); informative fraction = #{shift,gain,other}/#effect-bearing;
    class distribution.  Falsifier for RQ2: upper CI bound of the collapse fraction < 0.5."""
    cls = np.asarray(cls, object)
    keep = np.ones(len(cls), bool) if is_grn is None else ~np.asarray(is_grn, bool)
    inf_ = np.isin(cls, ['shift', 'gain', 'other']) & keep
    eff = np.isin(cls, ['shift', 'gain', 'other', 'no-recovery', 'uninformative']) & keep
    col = clustered_fraction(cls == 'shift', inf_, groups, B, seed)
    col_nr = clustered_fraction(cls == 'shift', inf_ | ((cls == 'no-recovery') & keep), groups, B, seed)
    info = clustered_fraction(inf_, eff, groups, B, seed)
    dist = {c: int(((cls == c) & keep).sum()) for c in ('none', 'shift', 'gain', 'other', 'no-recovery',
                                                         'uninformative')}
    return dict(collapse=col, collapse_incl_norecovery=col_nr, informative=info, classes=dist,
                falsified=bool(col['ci'][1] < 0.5))


# ------------------------------------------------------------------------------------------ S6
def s6_summation(lam, Ysil_C1, sil_seeds, intact, R=2000, seed=11, alpha=0.05):
    """S6: S(lam) = sum_{k in C1} f_k(lam) (pointwise inversion, Sec. 7.3) with a seed bootstrap (O-hat
    re-estimated per replicate, same seed draw for all conditions and the intact curve), plus a trend
    test: OLS slope of S on log(lam) over the lambdas where S is complete (every C1 member defined),
    with a bootstrap CI; 'decreasing' if the upper bound < 0.  Also reports the partial sum over
    defined terms and the number defined at each lambda."""
    from analysis.curves import MonotoneCurve, pointwise_f
    lam = np.asarray(lam, float); Y = np.asarray(Ysil_C1, float); sil_seeds = np.asarray(sil_seeds)
    tr_rates, tr_seeds = intact.train_rates
    pos = {int(s): i for i, s in enumerate(tr_seeds)}

    def one(cur, Yb):
        F = np.vstack([pointwise_f(cur, lam, Yb[k].mean(0)) for k in range(Yb.shape[0])])
        ndef = np.isfinite(F).sum(0)
        partial = np.nansum(F, 0)
        complete = np.where(ndef == F.shape[0], partial, np.nan)
        return complete, partial, ndef

    comp0, part0, ndef0 = one(intact.train, Y)
    loglam = np.log(lam)

    def slope(S):
        ok = np.isfinite(S)
        if ok.sum() < 3:
            return np.nan
        return float(np.polyfit(loglam[ok], S[ok], 1)[0])

    rng = np.random.default_rng(seed)
    S_b = np.empty((R, lam.size)); P_b = np.empty((R, lam.size)); sl_b = np.empty(R)
    ok_cols = np.isfinite(comp0)
    for r in range(R):
        ix = rng.integers(0, sil_seeds.size, sil_seeds.size)
        cur = MonotoneCurve(intact.lam, tr_rates[[pos[int(s)] for s in sil_seeds[ix]]], intact.duration_s)
        c, p, _ = one(cur, Y[:, ix, :])
        S_b[r], P_b[r] = c, p
        cc = np.where(ok_cols, c, np.nan)          # slope on the lambdas complete in the point estimate
        sl_b[r] = slope(cc)
    q = [100 * alpha / 2, 100 * (1 - alpha / 2)]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)      # all-NaN columns (lambda never complete)
        ci = np.nanpercentile(S_b, q, axis=0)
    sl0 = slope(comp0)
    slci = np.nanpercentile(sl_b, q) if np.isfinite(sl_b).any() else (np.nan, np.nan)
    tau = stats.kendalltau(lam[ok_cols], comp0[ok_cols]) if ok_cols.sum() >= 3 else None
    return dict(S=comp0, S_partial=part0, n_defined=ndef0, S_ci=ci, slope=sl0, slope_ci=tuple(slci),
                decreasing=bool(slci[1] < 0), kendall_tau=None if tau is None else float(tau.statistic),
                kendall_p=None if tau is None else float(tau.pvalue), frac_boot_incomplete=float(
                    np.mean(~np.isfinite(S_b[:, ok_cols]))) if ok_cols.any() else float('nan'))


# ------------------------------------------------------------------------------------------ pairs
def pair_predictions(curve, lam, fa, fb, f_and, f_ab_struct):
    """Sec. 6.5 predicted curves.  T5a: O-hat((1 - fa - fb + f_and) lam); T5b: O-hat((1 - f_ab) lam).
    Also the law-predicted singles and the predicted w and epsilon (Product neutrality) of T5a/T5b,
    with w = O-hat(.)/O-hat(lam)."""
    lam = np.asarray(lam, float)
    O0 = curve(lam)
    Oa, Ob = curve((1 - fa) * lam), curve((1 - fb) * lam)
    t5a = curve((1 - fa - fb + f_and) * lam)
    t5b = curve((1 - f_ab_struct) * lam)
    with np.errstate(divide='ignore', invalid='ignore'):
        wa, wb = Oa / O0, Ob / O0
        out = dict(O_T5a=t5a, O_T5b=t5b, w_T5a=t5a / O0, w_T5b=t5b / O0, w_a=wa, w_b=wb)
    out['eps_T5a'] = out['w_T5a'] - wa * wb
    out['eps_T5b'] = out['w_T5b'] - wa * wb
    return out


def snr_mask(Yint):
    """Evaluation mask of Sec. 6.5: intact mean O(lam) >= max(5 Hz, 3*SE), SE = s/sqrt(n) of the paired
    intact seeds at lam (choice C-9: SE of the intact mean, as literally written)."""
    Yint = np.asarray(Yint, float)
    O = Yint.mean(0)
    se = Yint.std(0, ddof=1) / math.sqrt(Yint.shape[0])
    return O >= np.maximum(5.0, 3 * se)


def observed_w_eps(Yab, Ya, Yb, Yint):
    """Observed w_ab, w_a, w_b and eps_ab = w_ab - w_a w_b from seed means, w = Obar_x/Obar_intact."""
    O = np.asarray(Yint, float).mean(0)
    with np.errstate(divide='ignore', invalid='ignore'):
        wab, wa, wb = (np.asarray(Y, float).mean(0) / O for Y in (Yab, Ya, Yb))
    return dict(w_ab=wab, w_a=wa, w_b=wb, eps=wab - wa * wb)


def rmse_masked(obs_list, pred_list, mask_list):
    """RMSE pooled over all (pair, lambda) cells inside the masks."""
    num = 0.0; n = 0
    for o, p, m in zip(obs_list, pred_list, mask_list):
        m = np.asarray(m, bool) & np.isfinite(o) & np.isfinite(p)
        num += float(((np.asarray(o)[m] - np.asarray(p)[m]) ** 2).sum()); n += int(m.sum())
    return math.sqrt(num / n) if n else float('nan')


def prediction_band(pred_point, pred_reps, Yobs, z=1.959963984540054):
    """95% pointwise prediction band for the OBSERVED seed-mean curve:
    pred +- z*sqrt(Var_boot(pred) + s_obs^2/n_obs) (choice C-10).  pred_reps: (R, L) seed-bootstrap
    replicates of the prediction (O-hat and f-hats re-estimated)."""
    Yobs = np.asarray(Yobs, float)
    v = np.var(np.asarray(pred_reps, float), axis=0, ddof=1) + Yobs.var(0, ddof=1) / Yobs.shape[0]
    h = z * np.sqrt(v)
    return pred_point - h, pred_point + h


def band_coverage(obs_means, bands, masks):
    """Fraction of pairs whose observed curve lies inside the band at EVERY masked lambda, and the
    pointwise coverage over all masked cells."""
    whole, cells, inside = [], 0, 0
    for o, (lo, hi), m in zip(obs_means, bands, masks):
        m = np.asarray(m, bool)
        ins = (o >= lo) & (o <= hi)
        whole.append(bool(ins[m].all()) if m.any() else np.nan)
        cells += int(m.sum()); inside += int(ins[m].sum())
    w = np.array([x for x in whole if x == x], float)
    return dict(frac_pairs_inside=float(w.mean()) if w.size else float('nan'),
                pointwise=inside / cells if cells else float('nan'), n_pairs=int(w.size))


def stratum_mean_overlap(f_and, strata):
    """Null of Sec. 6.5: replace each pair's overlap term by the mean of its stratum."""
    f_and = np.asarray(f_and, float); strata = np.asarray(strata, object)
    out = np.empty_like(f_and)
    for s in np.unique(strata):
        m = strata == s
        out[m] = f_and[m].mean()
    return out
