"""Unit and Monte Carlo tests for analysis/curves.py on SYNTHETIC data with known ground truth.

Run:  OMP_NUM_THREADS=1 /home/user/venv-fly/bin/python -m pytest -q analysis/tests/test_curves.py
The larger Monte Carlo numbers reported in ANALYSIS_VALIDATION.md come from run_validation.py.
"""
import numpy as np
import pandas as pd
import pytest
from scipy.optimize import isotonic_regression, minimize_scalar

from analysis import curves as C
import synth as S

O_HILL = S.hill_curve()
LAM = S.default_grid(O_HILL)


def noise_free_intact(O=O_HILL, n=60):
    lam = S.INTACT_LAM
    return C.IntactData(lam, np.tile(O(lam), (n, 1)) + 0.0, np.arange(n))


def noisy_intact(rng, O=O_HILL):
    lam, seeds, r = S.intact_curve_data(O, rng)
    return C.IntactData(lam, r, seeds)


# ------------------------------------------------------------------------------------------ PAVA / O-hat
def test_pava_matches_scipy():
    rng = np.random.default_rng(0)
    for _ in range(200):
        y = rng.normal(size=rng.integers(1, 40)).cumsum() * rng.choice([-1, 1]) + rng.normal(size=1)
        w = rng.uniform(0.2, 3, y.size)
        np.testing.assert_allclose(C.pava(y, w), isotonic_regression(y, weights=w).x, atol=1e-12)


def test_pava_monotone_and_identity():
    y = np.array([0., 1, 1, 2, 5])
    np.testing.assert_array_equal(C.pava(y), y)
    z = C.pava([3., 1, 2])
    assert np.all(np.diff(z) >= 0) and np.isclose(z.mean(), 2.0)


def test_curve_interpolates_monotone_data_and_clamps():
    lam = S.INTACT_LAM
    cur = C.MonotoneCurve(lam, np.tile(O_HILL(lam), (3, 1)))
    np.testing.assert_allclose(cur(lam), O_HILL(lam), atol=1e-10)          # through the knots
    x = np.linspace(0, 400, 4001)
    assert np.all(np.diff(cur(x)) >= -1e-12)                                 # PCHIP keeps monotonicity
    assert np.max(np.abs(cur(x) - O_HILL(x))) < 0.25                         # 5 Hz knots: < 0.3% of Emax
    y, flag = cur(np.array([-10.0, 0.0, 200.0, 400.0, 900.0]), return_flag=True)
    np.testing.assert_array_equal(flag, [True, False, False, False, True])
    assert y[0] == cur(0.0) and y[-1] == cur(400.0) == cur.O_max


def test_curve_inverse_and_lam50():
    cur = C.MonotoneCurve(S.INTACT_LAM, np.tile(O_HILL(S.INTACT_LAM), (2, 1)))
    x = np.array([20.0, 63.0, 101.3, 250.0])
    np.testing.assert_allclose(cur.inverse(cur(x)), x, atol=1e-8)
    from scipy.optimize import brentq
    true50 = brentq(lambda x: O_HILL(x) - 0.5 * O_HILL(400.0), 1, 400)       # O_max = O(400) on the grid
    assert abs(cur.lam50 - true50) < 0.05
    assert abs(cur(cur.lam50) - 0.5 * cur.O_max) < 1e-8
    assert np.isnan(cur.inverse(np.array([cur.O_max + 1]))[0])


def test_silencing_grid_rule():
    g, hi = C.silencing_grid(63.0)
    assert len(g) == 10 and g[0] == 31.5 and g[-1] == 400.0
    np.testing.assert_allclose(np.diff(np.log(g)), np.log(400 / 31.5) / 9, atol=1e-3)
    np.testing.assert_array_equal(hi, g > 200)
    g2, _ = C.silencing_grid(30.0)
    assert g2[-1] == 240.0                                                   # 8*lam50 < 400


# ------------------------------------------------------------------------------------------ fits, noise free
@pytest.mark.parametrize('f', [-0.3, 0.0, 0.05, 0.2, 0.5, 0.9])
def test_shift_fit_exact_noise_free(f):
    I = noise_free_intact()
    y = I.train((1 - f) * LAM)
    W = np.ones_like(LAM)
    fs = C.fit_shift_many(I.train, LAM, y[None], W[None])
    assert abs(fs.f[0] - f) < 1e-5 and not fs.plateau[0]


def test_shift_fit_means_equal_per_seed_and_brent():
    rng = np.random.default_rng(3)
    I = noisy_intact(rng)
    Ys, _ = S.screen_pair(O_HILL, LAM, rng, 'shift', 0.3)
    W = C.seed_weights(Ys)
    fs = C.fit_shift_many(I.train, LAM, Ys.mean(0)[None], W[None]).f[0]
    per_seed = lambda f: float((W * (Ys - I.train((1 - f) * LAM)) ** 2).sum())
    br = minimize_scalar(per_seed, bounds=(fs - 0.01, fs + 0.01), method='bounded',
                         options=dict(xatol=1e-9)).x
    assert abs(fs - br) < 2e-5
    grid = np.linspace(-0.5, 0.99, 3000)
    assert per_seed(fs) <= min(per_seed(g) for g in grid) + 1e-9


def test_zero_curve_plateau_upper_end():
    I = noise_free_intact()                       # Hill: O > 0 for every lam > 0 -> unique minimiser f = 1
    fs = C.fit_shift_many(I.train, LAM, np.zeros((1, LAM.size)), np.ones((1, LAM.size)))
    assert fs.f[0] == 1.0 and fs.at_bound[0] and not fs.plateau[0]
    thr = lambda lam: np.where(lam > 20, O_HILL(lam - 20), 0.0)     # exact zeros below 20 Hz (as in MN9)
    I2 = C.IntactData(S.INTACT_LAM, np.tile(thr(S.INTACT_LAM), (60, 1)), np.arange(60))
    fs = C.fit_shift_many(I2.train, LAM, np.zeros((1, LAM.size)), np.ones((1, LAM.size)))
    assert fs.plateau[0] and fs.f[0] == 1.0 and abs(fs.plateau_lo[0] - (1 - 20 / 400)) < 2e-3


def test_gain_and_free_noise_free():
    I = noise_free_intact()
    y = 0.6 * I.train(0.8 * LAM)
    f, g, s = C.fit_gain(I.train, LAM, y, np.ones_like(LAM))
    assert abs(f - 0.2) < 1e-4 and abs(g - 0.6) < 1e-4 and s < 1e-8
    yh = C.hill(LAM, 70.0, 90.0, 2.0)
    (E, l50, n), s = C.fit_free(LAM, yh, np.ones_like(LAM))
    np.testing.assert_allclose([E, l50, n], [70, 90, 2], rtol=1e-4)
    assert C.hill(0.0, 1, 1, 1) == 0.0


def test_gof_noise_free_zero_and_formula():
    I = noise_free_intact()
    Ys = np.tile(I.indep(0.7 * LAM), (30, 1)) + np.random.default_rng(1).normal(0, 1e-6, (30, LAM.size))
    g = C.gof_shift(LAM, Ys, 0.3, I.indep)
    assert g['chi2'] < 1e-6 and g['df'] == 9 and g['p'] > 0.999
    # hand formula with floors
    rng = np.random.default_rng(2)
    Ys = rng.normal(40, 5, (30, LAM.size))
    g = C.gof_shift(LAM, Ys, 0.1, I.indep)
    x = 0.9 * LAM
    den = np.maximum(Ys.var(0, ddof=1), 1) / 30 + np.maximum(np.interp(x, I.indep.lam, I.indep.var), 1) / 30
    assert np.isclose(g['chi2'], (((Ys.mean(0) - I.indep(x)) ** 2) / den).sum())


def test_pointwise_inversion_noise_free():
    I = noise_free_intact()
    for f in (0.1, 0.4):
        pf = C.pointwise_f(I.train, LAM, I.train((1 - f) * LAM))
        ok = np.isfinite(pf)
        assert ok.sum() >= 2
        np.testing.assert_allclose(pf[ok], f, atol=1e-8)
        rel = I.train((1 - f) * LAM) / I.train.O_max
        np.testing.assert_array_equal(ok, (rel >= 0.1) & (rel <= 0.9))


# ------------------------------------------------------------------------------------------ gates and classes
def test_effect_gate():
    rng = np.random.default_rng(5)
    Ys, Yi = S.screen_pair(O_HILL, LAM, rng, 'shift', 0.0, crn_rho=1.0)
    assert not C.effect_gate(Ys, Yi)['effect']                       # CRN-identical -> no effect
    Ys, Yi = S.screen_pair(O_HILL, LAM, rng, 'shift', 0.5)
    assert C.effect_gate(Ys, Yi)['effect']
    # a difference only where O < 5 Hz must not count
    Yi = np.full((30, 3), 3.0) + rng.normal(0, .1, (30, 3)); Ys = Yi * 0.5
    assert not C.effect_gate(Ys, Yi)['effect']
    # |N| < 0.05 must not count even if the CI excludes 0
    Yi = np.full((30, 3), 50.0) + rng.normal(0, .1, (30, 3)); Ys = Yi * 0.97
    eg = C.effect_gate(Ys, Yi)
    assert eg['ci_hi'].max() < 0 and not eg['effect']
    Ys = Yi * 0.94
    assert C.effect_gate(Ys, Yi)['effect']


def test_informativeness_hand_cases():
    I = noise_free_intact()
    assert C.informativeness(I.train, LAM, 0.2)['informative']
    assert C.informativeness(I.train, LAM, 0.5)['informative']
    assert not C.informativeness(I.train, LAM, 0.9)['informative']           # never reaches 0.9 O_max
    sat = np.geomspace(300, 400, 10)
    assert C.informativeness(I.train, sat, 0.6)['n_mid'] == 0                   # saturated grid


def test_class_precedence():
    assert C.assign_class(False, True, False, 'free', 0.0) == 'none'
    assert C.assign_class(True, True, False, 'shift', 1.0) == 'no-recovery'
    assert C.assign_class(True, False, False, 'shift', 1.0) == 'uninformative'
    assert C.assign_class(True, False, True, 'shift', 0.2) == 'shift'
    assert C.assign_class(True, False, True, 'shift', 0.01) == 'other'
    assert C.assign_class(True, False, True, 'gain', 0.01) == 'gain'
    assert C.assign_class(True, False, True, 'free', 0.9) == 'other'


def test_cv_folds_deterministic():
    f = C.cv_folds(np.arange(30)[::-1])
    assert [len(x) for x in f] == [6] * 5
    assert sorted(np.concatenate(f)) == list(range(30))
    np.testing.assert_array_equal(f[0], [0, 5, 10, 15, 20, 25])


# ------------------------------------------------------------------------------------------ Monte Carlo
def _mc(kind, f, gamma=1.0, reps=40, seed=0, lam=LAM, other=None, O=O_HILL, cv=True):
    rng = np.random.default_rng(seed)
    rows = []
    for r in range(reps):
        I = noisy_intact(rng, O)
        Ys, Yi = S.screen_pair(O, lam, rng, kind, f, gamma, other=other,
                               crn_rho=1.0 if (kind == 'shift' and f == 0) else 0.5)
        rows.append(C.analyze_condition(lam, Ys, Yi, S.SEEDS_TRAIN, I, rng=np.random.default_rng(r), do_cv=cv))
    return pd.DataFrame(rows)


@pytest.mark.parametrize('f,tol_bias,tol_rmse', [(0.05, 0.01, 0.03), (0.2, 0.01, 0.03), (0.5, 0.01, 0.02),
                                                 (0.9, 0.01, 0.02)])
def test_mc_f_recovery(f, tol_bias, tol_rmse):
    d = _mc('shift', f, reps=40, seed=int(f * 100), cv=False)
    err = d['fhat'] - f
    assert abs(err.mean()) < tol_bias, err.mean()
    assert np.sqrt((err ** 2).mean()) < tol_rmse


def test_mc_classes_shift_and_none():
    d = _mc('shift', 0.2, reps=30, seed=11)
    assert (d['cls'] == 'shift').mean() >= 0.8
    d0 = _mc('shift', 0.0, reps=15, seed=12, cv=False)
    assert (d0['cls'] == 'none').all()
    d9 = _mc('shift', 0.9, reps=10, seed=13, cv=False)
    assert (d9['cls'] == 'uninformative').all()
    dz = _mc('zero', 0.0, reps=5, seed=14, cv=False)
    assert (dz['cls'] == 'no-recovery').all()


def test_mc_gain_and_other_detected():
    d = _mc('gain', 0.2, gamma=0.6, reps=15, seed=21)
    assert (d['cls'] == 'gain').mean() >= 0.8
    other = lambda lam: C.hill(lam, 85.0, 63.0 / 0.8, 1.2)        # shallower slope, shifted lam50
    d = _mc('other', 0.0, reps=15, seed=22, other=other)
    assert (d['cls'] == 'other').mean() >= 0.8


def test_mc_uninformative_saturated_grid():
    sat = np.round(np.geomspace(300, 400, 10), 2)
    d = _mc('shift', 0.6, reps=10, seed=31, lam=sat, cv=False)
    assert (d.loc[d['effect'], 'cls'] == 'uninformative').all() and d['effect'].mean() >= 0.8


def test_mc_gof_size_roughly_nominal():
    rng = np.random.default_rng(41)
    p = []
    for r in range(150):
        I = noisy_intact(rng)
        f = (0.05, 0.2, 0.5)[r % 3]
        Ys, _ = S.screen_pair(O_HILL, LAM, rng, 'shift', f)
        fh = C.fit_shift_many(I.train, LAM, Ys.mean(0)[None], C.seed_weights(Ys)[None]).f[0]
        p.append(C.gof_shift(LAM, Ys, fh, I.indep)['p'])
    size = np.mean(np.array(p) < 0.05)
    assert 0.0 <= size <= 0.12, size        # binomial 99% band around 0.05 at n=150 is ~[0.01, 0.10]


def test_seed_bootstrap_se_calibrated():
    """Nested level of P-A: the seed-bootstrap SD of f-hat must match the true sampling SD."""
    rng = np.random.default_rng(51)
    fh, sds = [], []
    for r in range(40):
        I = noisy_intact(rng)
        Ys, _ = S.screen_pair(O_HILL, LAM, rng, 'shift', 0.3)
        fh.append(C.fit_shift_many(I.train, LAM, Ys.mean(0)[None], C.seed_weights(Ys)[None]).f[0])
        if r < 10:
            reps = C.seed_bootstrap_fhat(LAM, Ys[None], S.SEEDS_TRAIN, I, R=200, rng=np.random.default_rng(r))
            sds.append(reps[:, 0].std(ddof=1))
    ratio = np.mean(sds) / np.std(fh, ddof=1)
    assert 0.6 < ratio < 1.6, ratio


# ------------------------------------------------------------------------------------------ I/O contract
def _write_synthetic_screen(tmp_path, rng):
    lam = LAM
    rows, conds = [], []
    lam_i, seeds_i, r_i = S.intact_curve_data(O_HILL, rng)
    for s, row in zip(seeds_i, r_i):
        for l, c in zip(lam_i, row):
            rows.append(('intact_curve', 'S_shiu', l, s, int(c), int(c)))
    pd.DataFrame(rows, columns=list(C.COUNTS_COLUMNS)).to_parquet(tmp_path / 'ic.parquet')
    pd.DataFrame([dict(condition_id='intact_curve', kind='intact', silenced_ids=[], input_set='S_shiu',
                       lambda_hz=list(lam_i), duration_s=1.0, flywire_version='v783', label='intact')]
                 ).to_parquet(tmp_path / 'ic_conditions.parquet')
    rows = []
    truth = {'n1': 0.2, 'n2': 0.5}
    base = None
    for cid, f in [('intact', None), ('n1', 0.2), ('n2', 0.5)]:
        if f is None:
            mu = O_HILL(lam)
        else:
            mu = O_HILL((1 - f) * lam)
        Y = S.counts_from_mean(mu[None], rng.standard_normal((30, lam.size)))
        for s in range(30):
            for j, l in enumerate(lam):
                rows.append((cid, 'S_shiu', l, s, int(Y[s, j]), int(Y[s, j])))
        conds.append(dict(condition_id=cid, kind='intact' if f is None else 'single',
                          silenced_ids=[] if f is None else [int(1e17) + len(conds)], input_set='S_shiu',
                          lambda_hz=list(lam), duration_s=1.0, flywire_version='v783', label=cid))
    pd.DataFrame(rows, columns=list(C.COUNTS_COLUMNS)).to_parquet(tmp_path / 'sc.parquet')
    pd.DataFrame(conds).to_parquet(tmp_path / 'sc_conditions.parquet')
    return truth


def test_io_contract_roundtrip(tmp_path):
    truth = _write_synthetic_screen(tmp_path, np.random.default_rng(61))
    rd = lambda n: pd.read_parquet(tmp_path / n)
    res, intact, lam = C.analyze_screen(rd('sc.parquet'), rd('sc_conditions.parquet'), rd('ic.parquet'),
                                        rd('ic_conditions.parquet'), 'S_shiu', do_cv=False)
    for _, r in res.iterrows():
        assert abs(r['fhat'] - truth[r['condition_id']]) < 0.05
    bad = rd('sc.parquet')
    bad = bad[~((bad.condition_id == 'intact') & (bad.seed == 3))]
    with pytest.raises(ValueError):
        C.validate_screen(bad, rd('sc_conditions.parquet'))


def test_io_contract_doc_example_and_grid(tmp_path):
    counts = pd.DataFrame({'condition_id': ['intact', 'k_720575940600000001'] * 2,
                           'input_set': 'S_shiu', 'lambda_hz': [31.42, 31.42, 41.68, 41.68],
                           'seed': [0, 0, 0, 0], 'mn9_primary_count': [9, 7, 15, 12],
                           'mn9_secondary_count': [8, 7, 14, 11]})
    conds = pd.DataFrame([dict(condition_id='intact', kind='intact', silenced_ids=[], input_set='S_shiu',
                               lambda_hz=[31.42, 41.68], duration_s=1.0, flywire_version='v783', label='intact'),
                          dict(condition_id='k_720575940600000001', kind='single',
                               silenced_ids=[720575940600000001], input_set='S_shiu',
                               lambda_hz=[31.42, 41.68], duration_s=1.0, flywire_version='v783', label='CB1234')])
    counts.to_parquet(tmp_path / 'x.counts.parquet'); conds.to_parquet(tmp_path / 'x.conditions.parquet')
    assert C.validate_screen(pd.read_parquet(tmp_path / 'x.counts.parquet'),
                             pd.read_parquet(tmp_path / 'x.conditions.parquet'))
    bad = conds.copy(); bad.at[1, 'lambda_hz'] = [31.42]
    with pytest.raises(ValueError, match='lambda_hz'):
        C.validate_screen(counts, bad)
    # grid freezing from an intact-curve file
    _write_synthetic_screen(tmp_path, np.random.default_rng(62))
    g = C.grid_from_intact(pd.read_parquet(tmp_path / 'ic.parquet'), pd.read_parquet(tmp_path / 'ic_conditions.parquet'),
                           'S_shiu')
    assert len(g['lambda_hz']) == 10 and abs(g['lam50'] - 63) < 3 and g['lambda_hz'][-1] == 400.0
