"""Tests for analysis/stats.py on synthetic data with known ground truth.

Run:  OMP_NUM_THREADS=1 /home/user/venv-fly/bin/python -m pytest -q analysis/tests/test_stats.py
"""
import itertools
import math

import numpy as np
import pytest
from scipy import stats as sps

from analysis import curves as C
from analysis import stats as St
import synth as S

O_HILL = S.hill_curve()
LAM = S.default_grid(O_HILL)


# ------------------------------------------------------------------------------------------ basics
def test_spearman_and_tau_b_match_scipy():
    rng = np.random.default_rng(0)
    for _ in range(50):
        x = rng.integers(0, 5, 12).astype(float); y = rng.integers(0, 4, 12).astype(float)
        if np.ptp(x) == 0 or np.ptp(y) == 0:
            continue
        assert np.isclose(St.spearman(x, y), sps.spearmanr(x, y).statistic)
        assert np.isclose(St.kendall_tau_b(x, y), sps.kendalltau(x, y).statistic)


def test_make_groups_singletons():
    codes, ns = St.make_groups(['A', 'A', None, 'B', np.nan, ''], homolog=[None, None, 'B', None, None, None])
    assert codes[0] == codes[1] and codes[2] == codes[3] and len(set(codes)) == 4 and ns == 2


# ------------------------------------------------------------------------------------------ S4 / S5 exact nulls
def test_s4_exact_chance_levels():
    f = dict(zip(St.S4_TYPES, [7., 6, 5, 4, 3, 2, 1]))          # distinct values; any order gives same null
    r = St.s4_exact(f)
    null = r['null']
    assert r['n_perm'] == 5040
    assert np.isclose(null.max(), 0.8164965809, atol=1e-9)         # sqrt(2/3)
    assert np.isclose(r['tau_b'], null.max()) and np.isclose(r['p'], 48 / 5040)   # = 1/105
    assert (null >= 0.6 - 1e-12).sum() == 144 and np.isclose(np.mean(null >= 0.6 - 1e-12), 0.0286, atol=5e-5)
    assert np.isclose(np.mean(null >= 0.5 - 1e-12), 0.0667, atol=5e-5)
    assert np.isclose(np.mean(null >= 0.7), 1 / 105)
    assert not (null > 0.8165).any()
    # p is exact and order-invariant: worst ordering gives p = 1
    worst = dict(zip(St.S4_TYPES, [1., 2, 3, 4, 5, 6, 7]))
    assert St.s4_exact(worst)['p'] == 1.0
    # signed f: an inhibitory Usnea (negative f) loses concordance
    f2 = dict(f, Usnea=-0.3)
    assert St.s4_exact(f2)['tau_b'] < r['tau_b']


def test_s4_top2_exact():
    f = dict(zip(St.S4_TYPES, [7., 6, 5, 4, 3, 2, 1]))
    r = St.s4_top2(f)
    assert r['indicator'] == 1 and np.isclose(r['p'], 1 / 21)
    f2 = dict(f, Usnea=0.5)
    assert St.s4_top2(f2)['indicator'] == 0 and St.s4_top2(f2)['p'] == 1.0


def test_s5_exact_wilcoxon():
    r = St.wilcoxon_exact_greater([10, 9, 8, 7, 6, 5, 4], [3, 2, 1])
    assert r['n_alloc'] == 120 and np.isclose(r['p'], 1 / 120)
    rng = np.random.default_rng(1)
    for _ in range(30):
        x, y = rng.normal(size=7), rng.normal(size=3)
        p = St.wilcoxon_exact_greater(x, y)['p']
        assert np.isclose(p, sps.mannwhitneyu(x, y, alternative='greater', method='exact').pvalue)
    # exact null over the 120 equally likely allocations: valid (P(p <= a) <= a at every attainable a)
    # and the attainable levels below 0.05 are 1/120, 2/120, 4/120 (the next is 7/120 = 0.058)
    vals = np.arange(10.0)
    ps = np.array([St.wilcoxon_exact_greater(vals[list(c)], np.delete(vals, list(c)))['p']
                   for c in itertools.combinations(range(10), 7)])
    for a in np.unique(ps):
        assert np.mean(ps <= a + 1e-12) <= a + 1e-12
    np.testing.assert_allclose(np.unique(ps)[:4] * 120, [1, 2, 4, 7])
    assert np.isclose(np.mean(ps <= 0.05), 4 / 120)


def test_s3_binomial():
    r = St.s3_dominators(['no-recovery'] * 5)
    assert r['run'] and np.isclose(r['p'], 1 / 32)
    r = St.s3_dominators(['no-recovery'] * 4)
    assert not r['run'] and r['p'] is None
    r = St.s3_dominators(['no-recovery'] * 6 + ['shift'] * 2)
    assert np.isclose(r['p'], sum(math.comb(8, k) for k in (6, 7, 8)) / 2 ** 8)


def test_holm_matches_statsmodels():
    from statsmodels.stats.multitest import multipletests
    p = {'S1': 0.01, 'S2': 0.04, 'S3': 0.03, 'S4': 0.0286, 'S5': 0.2}
    h = St.holm(p)
    rej, adj, _, _ = multipletests(list(p.values()), method='holm')
    for (k, _), a, rj in zip(p.items(), adj, rej):
        assert np.isclose(h[k][0], a) and h[k][1] == rj
    h2 = St.holm({**p, 'S3': None})
    rej, adj, _, _ = multipletests([0.01, 0.04, 0.0286, 0.2], method='holm')
    assert np.isclose(h2['S4'][0], adj[2]) and h2['S3'] == (None, None)


# ------------------------------------------------------------------------------------------ dependent r
def test_williams_steiger_size_and_symmetry():
    t, p1, p2 = St.williams_t(0.5, 0.3, 0.4, 100)
    t2, _, _ = St.williams_t(0.3, 0.5, 0.4, 100)
    assert np.isclose(t, -t2)
    z, _, _ = St.steiger_z(0.5, 0.3, 0.4, 100)
    assert abs(t - z) < 0.1                                                  # agree at moderate n
    rng = np.random.default_rng(2)
    cov = np.array([[1, .4, .4], [.4, 1, .5], [.4, .5, 1]])                 # rho12 = rho13 (H0)
    L = np.linalg.cholesky(cov)
    rej_w = rej_s = 0; M = 2000
    for _ in range(M):
        X = rng.standard_normal((150, 3)) @ L.T
        R = np.corrcoef(X.T)
        rej_w += St.williams_t(R[0, 1], R[0, 2], R[1, 2], 150)[2] < 0.05
        rej_s += St.steiger_z(R[0, 1], R[0, 2], R[1, 2], 150)[2] < 0.05
    assert abs(rej_w / M - 0.05) < 0.015 and abs(rej_s / M - 0.05) < 0.015


def test_partial_spearman():
    rng = np.random.default_rng(3)
    z = rng.normal(size=400)
    x = z + 0.5 * rng.normal(size=400); y = z + 0.5 * rng.normal(size=400)
    assert St.spearman(x, y) > 0.6
    assert abs(St.partial_spearman(x, y, [z])['r']) < 0.12
    assert np.isclose(St.partial_spearman(x, y, [])['r'], St.spearman(x, y))
    # one covariate: first-order partial-correlation formula on ranks
    rx, ry, rz = (sps.rankdata(v) for v in (x, y, z))
    rxy, rxz, ryz = (np.corrcoef(a, b)[0, 1] for a, b in ((rx, ry), (rx, rz), (ry, rz)))
    assert np.isclose(St.partial_spearman(x, y, [z])['r'],
                      (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2)))


def test_average_precision_matches_sklearn():
    from sklearn.metrics import average_precision_score
    rng = np.random.default_rng(4)
    for _ in range(50):
        y = rng.random(60) < 0.3
        s = np.round(rng.normal(size=60) + y, 1)                              # ties included
        if y.sum() == 0:
            continue
        assert np.isclose(St.average_precision(y, s), average_precision_score(y, s))


def test_rq1_per_lambda_planted():
    rng = np.random.default_rng(5)
    f = rng.uniform(0, 0.6, 300)
    N = np.column_stack([1 - O_HILL((1 - f) * l) / O_HILL(l) for l in LAM])
    good = f + 0.05 * rng.normal(size=300); bad = rng.normal(size=300)
    out = St.rq1_per_lambda(N, {'good': good, 'bad': bad})
    g = [o for o in out if o['predictor'] == 'good' and o['prevalence'] > 0]
    b = [o for o in out if o['predictor'] == 'bad' and o['prevalence'] > 0]
    assert min(o['rho'] for o in g) > 0.9 and max(abs(o['rho']) for o in b) < 0.2
    assert all(og['auprc'] > ob['auprc'] for og, ob in zip(g, b))


# ------------------------------------------------------------------------------------------ P-A machinery
def _population(rng, G=200, per=2, sx=0.6, sc=0.6, sw=0.3, n_comp=8):
    u = rng.normal(size=G)
    groups = np.repeat(np.arange(G), per)
    f = u[groups] + sw * rng.normal(size=G * per)
    xs = u[groups] + sx * rng.normal(size=G * per)
    comps = {f'c{i}': u[groups] + (sc if i == 0 else 2.5) * rng.normal(size=G * per) for i in range(n_comp)}
    return f, xs, comps, groups


def test_pa_reselects_max_and_identical_competitor_gives_zero():
    rng = np.random.default_rng(6)
    f, xs, comps, g = _population(rng)
    r = St.grouped_bootstrap_delta_rho(xs, {**comps, 'same': xs.copy()}, f, g, B=200)
    assert np.allclose(r['boot'], 0.0) or r['boot'].max() <= 1e-12          # max over a family containing X*
    assert not r['decision']
    r = St.grouped_bootstrap_delta_rho(xs, comps, f, g, B=300)
    assert r['selected_freq']['c0'] > 0.9 and r['best'] == 'c0'
    assert np.isclose(r['delta'], St.spearman(xs, f) - max(St.spearman(v, f) for v in comps.values()))


def test_pa_size_under_null_and_power():
    rng = np.random.default_rng(7)
    dec0 = []
    for _ in range(80):                                     # H0: X* and the best competitor equally good
        f, xs, comps, g = _population(rng, sx=0.6, sc=0.6)
        dec0.append(St.grouped_bootstrap_delta_rho(xs, comps, f, g, B=400, seed=int(rng.integers(1e9)))['decision'])
    dec1 = []
    for _ in range(40):                                     # H1: X* clearly better (true delta-rho ~ 0.2)
        f, xs, comps, g = _population(rng, sx=0.3, sc=1.0)
        dec1.append(St.grouped_bootstrap_delta_rho(xs, comps, f, g, B=400, seed=int(rng.integers(1e9)))['decision'])
    assert np.mean(dec0) <= 0.10, np.mean(dec0)
    assert np.mean(dec1) >= 0.8, np.mean(dec1)


def test_pa_clustering_widens_ci():
    rng = np.random.default_rng(8)
    f, xs, comps, g = _population(rng, G=150, per=1)
    rep = 4
    F, X, Cc = np.repeat(f, rep), np.repeat(xs, rep), {k: np.repeat(v, rep) for k, v in comps.items()}
    gg = np.repeat(g, rep)
    w_cl = np.subtract(*St.grouped_bootstrap_delta_rho(X, Cc, F, gg, B=400)['ci_two_sided'][::-1])
    w_iid = np.subtract(*St.grouped_bootstrap_delta_rho(X, Cc, F, np.arange(F.size), B=400)['ci_two_sided'][::-1])
    assert w_cl > 1.5 * w_iid                       # ~sqrt(4) = 2 expected


def test_pa_nested_reps_widen_ci():
    rng = np.random.default_rng(9)
    f, xs, comps, g = _population(rng)
    reps = f[None, :] + 0.5 * rng.normal(size=(300, f.size))
    a = St.grouped_bootstrap_delta_rho(xs, comps, f, g, B=300)
    b = St.grouped_bootstrap_delta_rho(xs, comps, f, g, fhat_reps=reps, B=300)
    assert b['boot'].std() > a['boot'].std() and b['seed_reps'] == 300 and not b['recycled']
    c = St.grouped_bootstrap_delta_rho(xs, comps, f, g, fhat_reps=reps[:50], B=300)
    assert c['recycled']


def test_disattenuation_and_split_half():
    rng = np.random.default_rng(10)
    t = rng.normal(size=2000)
    a, b = t + rng.normal(size=2000), t + rng.normal(size=2000)
    sh = St.split_half_reliability(a, b)
    assert abs(sh['r_pearson'] - 0.5) < 0.05 and abs(sh['rel_pearson_sb'] - 2 / 3) < 0.05
    assert np.isclose(St.disattenuate(0.4, 0.64), 0.5)


def test_clustered_fraction_coverage():
    rng = np.random.default_rng(11)
    hits = 0; M = 150
    for _ in range(M):
        G = 120
        pg = rng.uniform(0.4, 0.9, G)                       # heterogeneous group-level collapse rates
        sizes = rng.integers(1, 4, G)
        groups = np.repeat(np.arange(G), sizes)
        s = rng.random(groups.size) < pg[groups]
        r = St.clustered_fraction(s, np.ones_like(s), groups, B=400, seed=int(rng.integers(1e9)))
        true = 0.65                                         # superpopulation ratio E[p_g] (sizes independent)
        hits += r['ci'][0] <= true <= r['ci'][1]
    assert hits / M > 0.88


def test_rq2_summary():
    cls = np.array(['shift'] * 6 + ['gain', 'other', 'no-recovery', 'uninformative', 'none'] + ['shift'])
    grn = np.zeros(cls.size, bool); grn[-1] = True
    r = St.rq2_summary(cls, np.arange(cls.size), is_grn=grn, B=200)
    assert np.isclose(r['collapse']['est'], 6 / 8) and np.isclose(r['informative']['est'], 8 / 10)
    assert np.isclose(r['collapse_incl_norecovery']['est'], 6 / 9) and r['classes']['shift'] == 6


# ------------------------------------------------------------------------------------------ S6
def _c1_data(rng, fk_of_lam, K):
    Y = []
    for k in range(K):
        mu = O_HILL((1 - fk_of_lam(k, LAM)) * LAM)
        Y.append(S.counts_from_mean(mu[None], rng.standard_normal((30, LAM.size))))
    return np.array(Y)


def test_s6_conservative_and_decreasing():
    rng = np.random.default_rng(12)
    lam_i, sd, r = S.intact_curve_data(O_HILL, rng)
    I = C.IntactData(lam_i, r, sd)
    K = 4
    Y = _c1_data(rng, lambda k, lam: np.full(lam.shape, 0.25), K)      # sum f = 1, constant
    res = St.s6_summation(LAM, Y, S.SEEDS_TRAIN, I, R=200)
    ok = np.isfinite(res['S'])
    assert ok.sum() >= 3
    assert abs(np.mean(res['S'][ok]) - 1.0) < 0.1 and np.all(np.abs(res['S'][ok] - 1.0) < 0.35)
    cover = (res['S_ci'][0][ok] <= 1.0) & (1.0 <= res['S_ci'][1][ok])
    assert cover.mean() >= 0.8
    assert res['slope_ci'][0] < 0 < res['slope_ci'][1] and not res['decreasing']
    # planted redundancy: f_k(lam) = 0.25*(lam/lam0)^-0.5 -> sum decreasing with lam
    Y = _c1_data(rng, lambda k, lam: 0.25 * (lam / LAM[0]) ** -0.5, K)
    res = St.s6_summation(LAM, Y, S.SEEDS_TRAIN, I, R=200)
    assert res['decreasing'] and res['slope'] < 0


# ------------------------------------------------------------------------------------------ pairs
def test_pair_predictions_noise_free_identity():
    cur = C.MonotoneCurve(S.INTACT_LAM, np.tile(O_HILL(S.INTACT_LAM), (2, 1)))
    p = St.pair_predictions(cur, LAM, 0.2, 0.3, 0.05, 0.45)
    np.testing.assert_allclose(p['O_T5a'], cur(0.55 * LAM))
    np.testing.assert_allclose(p['O_T5b'], cur(0.55 * LAM))
    np.testing.assert_allclose(p['eps_T5a'], p['w_T5a'] - p['w_a'] * p['w_b'])
    # serial pair (f_and = min): T5a equals the larger single
    q = St.pair_predictions(cur, LAM, 0.2, 0.3, 0.2, 0.3)
    np.testing.assert_allclose(q['O_T5a'], cur(0.7 * LAM))


def test_pair_metrics_coverage_and_null():
    rng = np.random.default_rng(13)
    npairs = 24
    strata = np.array(['par'] * 12 + ['ser'] * 12)
    cover_cells, inside_cells = 0, 0
    obs_w, pred_w, null_w, masks, obs_m, bands = [], [], [], [], [], []
    fand_true = np.where(strata == 'par', rng.uniform(0, 0.15, npairs), rng.uniform(0.05, 0.2, npairs))
    fand_null = St.stratum_mean_overlap(fand_true, strata)
    for i in range(npairs):
        lam_i, sd, r = S.intact_curve_data(O_HILL, rng)
        I = C.IntactData(lam_i, r, sd)
        fa, fb = rng.uniform(0.1, 0.3, 2)
        fa = max(fa, fand_true[i]); fb = max(fb, fand_true[i])
        Ya = S.counts_from_mean(O_HILL((1 - fa) * LAM)[None], rng.standard_normal((30, LAM.size)))
        Yb = S.counts_from_mean(O_HILL((1 - fb) * LAM)[None], rng.standard_normal((30, LAM.size)))
        Yab = S.counts_from_mean(O_HILL((1 - fa - fb + fand_true[i]) * LAM)[None], rng.standard_normal((30, LAM.size)))
        Yi = S.counts_from_mean(O_HILL(LAM)[None], rng.standard_normal((30, LAM.size)))
        W = np.vstack([C.seed_weights(Ya), C.seed_weights(Yb)])
        fh = C.fit_shift_many(I.train, LAM, np.vstack([Ya.mean(0), Yb.mean(0)]), W).f
        reps, curves = C.seed_bootstrap_fhat(LAM, np.stack([Ya, Yb]), S.SEEDS_TRAIN, I, R=150,
                                             rng=np.random.default_rng(i), return_curves=True)
        pr = np.array([St.pair_predictions(cu, LAM, reps[r, 0], reps[r, 1], fand_true[i], 0)['O_T5a']
                       for r, (_, cu) in enumerate(curves)])
        p0 = St.pair_predictions(I.train, LAM, fh[0], fh[1], fand_true[i], 0)
        pn = St.pair_predictions(I.train, LAM, fh[0], fh[1], fand_null[i], 0)
        m = St.snr_mask(Yi)
        ob = St.observed_w_eps(Yab, Ya, Yb, Yi)
        obs_w.append(ob['w_ab']); pred_w.append(p0['w_T5a']); null_w.append(pn['w_T5a']); masks.append(m)
        obs_m.append(Yab.mean(0)); bands.append(St.prediction_band(p0['O_T5a'], pr, Yab))
    cov = St.band_coverage(obs_m, bands, masks)
    assert 0.88 <= cov['pointwise'] <= 0.995, cov
    assert St.rmse_masked(obs_w, pred_w, masks) < St.rmse_masked(obs_w, null_w, masks)
    assert St.rmse_masked(obs_w, pred_w, masks) < 0.05
