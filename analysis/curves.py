"""curves.py -- pre-registered curve estimation and per-neuron classification.

Implements PROJECT_DESIGN.md v1.0 (commit e051e08) Sec. 3, 5.3, 6.1, 6.2, 6.3 and the pointwise
inversion used by S6 (Sec. 7.3).  Every analysis choice that the pre-registration leaves open is a
module constant below and is listed in analysis/ANALYSIS_VALIDATION.md ("Implementation choices").

Conventions
-----------
* Rates are in Hz: rate = spike count / duration_s (duration_s from the conditions table; 1.0 s for
  fastlif T = 10000 steps of 0.1 ms).
* "Training" intact seeds are 0-29 (paired with the screen through common random numbers, CRN);
  "independent" intact seeds are 30-59 (absolute GOF only).  Sec. 5.3.
* A silencing condition is analysed on the frozen 10-level silencing grid.  The paired intact
  baseline on that grid (same seeds) must be in the screen file (see IO_CONTRACT.md).
* Arrays of per-seed rates have shape (n_seeds, n_lambda); rows are seeds sorted ascending.

No function here reads or writes simulator/structural files owned by other agents.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy import stats
from scipy.interpolate import PchipInterpolator
from scipy.optimize import least_squares

# ------------------------------------------------------------------------------------------ constants
VAR_FLOOR_COUNTS2 = 1.0          # variance floor = 1 count^2, i.e. (1/duration_s)^2 Hz^2 (choice C-2)
F_LO, F_HI, F_STEP = -2.0, 1.0, 0.001   # f search range and grid step for M_shift / M_gain (choice C-3)
F_GRID = np.round(np.arange(F_LO, F_HI + F_STEP / 2, F_STEP), 10)
N_FOLDS = 5
MODEL_ORDER = ('shift', 'gain', 'free')        # simplest first (one-SE rule, Sec. 6.3)
EFFECT_MIN_RATE = 5.0            # Hz, Sec. 6.1
EFFECT_MIN_N = 0.05              # |N_k| threshold, Sec. 6.1
EFFECT_BOOT = 2000               # seed-bootstrap resamples for the 6.1 CI (choice C-6)
INFO_BAND = (0.2, 0.8)           # Sec. 6.2
INFO_HIGH = 0.9                  # Sec. 6.2
NO_RECOVERY = 0.1                # Sec. 6.3 class table
GOF_ALPHA = 0.05
POINTWISE_BAND = (0.1, 0.9)      # Sec. 7.3 (S6)
TRAIN_SEEDS = tuple(range(0, 30))
INDEP_SEEDS = tuple(range(30, 60))
CLASSES = ('none', 'shift', 'gain', 'other', 'no-recovery', 'uninformative')


def var_floor(duration_s: float = 1.0) -> float:
    """Variance floor in Hz^2: the variance of one spike count, expressed as a rate."""
    return VAR_FLOOR_COUNTS2 / float(duration_s) ** 2


# ------------------------------------------------------------------------------------------ isotonic
def pava(y, w=None) -> np.ndarray:
    """Non-decreasing isotonic (least-squares) regression by pool-adjacent-violators."""
    y = np.asarray(y, float)
    w = np.ones_like(y) if w is None else np.asarray(w, float)
    if y.ndim != 1 or w.shape != y.shape:
        raise ValueError('pava expects 1-D y and matching weights')
    if np.any(~np.isfinite(y)) or np.any(w <= 0):
        raise ValueError('pava: non-finite values or non-positive weights')
    vals, wts, cnts = [], [], []
    for yi, wi in zip(y, w):
        vals.append(yi); wts.append(wi); cnts.append(1)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            ww = wts[-2] + wts[-1]
            v = (vals[-2] * wts[-2] + vals[-1] * wts[-1]) / ww
            c = cnts[-2] + cnts[-1]
            vals.pop(); wts.pop(); cnts.pop()
            vals[-1], wts[-1], cnts[-1] = v, ww, c
    return np.repeat(np.asarray(vals), cnts)


class MonotoneCurve:
    """O-hat: isotonic regression of the per-level seed means, then a PCHIP interpolant (Sec. 6.3).

    Evaluation outside [lam_min, lam_max] is CLAMPED to the end value and FLAGGED (choice C-1).
    O_max is the maximum of O-hat over the intact grid (= last isotonic value; choice C-4).
    """

    def __init__(self, lam, rates, duration_s: float = 1.0):
        lam = np.asarray(lam, float)
        rates = np.atleast_2d(np.asarray(rates, float))
        if lam.ndim != 1 or rates.shape[1] != lam.size:
            raise ValueError('rates must have shape (n_seeds, n_lambda)')
        if np.any(np.diff(lam) <= 0):
            raise ValueError('intact grid must be strictly increasing')
        if not np.all(np.isfinite(rates)):
            raise ValueError('non-finite intact rates')
        if rates.shape[0] < 2:
            raise ValueError('need >= 2 seeds for an intact curve')
        self.lam = lam
        self.n = rates.shape[0]
        self.mean = rates.mean(0)
        self.var = rates.var(0, ddof=1)
        self.iso = pava(self.mean)
        self._p = PchipInterpolator(lam, self.iso, extrapolate=False)
        self.lam_min, self.lam_max = float(lam[0]), float(lam[-1])
        self.O_max = float(self.iso[-1])
        self.O_max_raw = float(self.mean.max())
        self.duration_s = duration_s

    def __call__(self, x, return_flag: bool = False):
        x = np.asarray(x, float)
        flag = (x < self.lam_min) | (x > self.lam_max)
        y = self._p(np.clip(x, self.lam_min, self.lam_max))
        return (y, flag) if return_flag else y

    def var_at(self, x):
        """Per-seed intact variance at x (linear interpolation between grid levels; clamped)."""
        return np.interp(np.asarray(x, float), self.lam, self.var)

    def inverse(self, y, n_iter: int = 60):
        """Smallest x in [lam_min, lam_max] with O-hat(x) >= y (vectorised bisection; exact to ~1e-15 Hz
        relative after 60 halvings).  NaN where y is outside [O-hat(lam_min), O_max]."""
        y = np.asarray(y, float)
        lo = np.full(y.shape, self.lam_min)
        hi = np.full(y.shape, self.lam_max)
        bad = (y < self.iso[0]) | (y > self.O_max) | ~np.isfinite(y)
        for _ in range(n_iter):
            mid = 0.5 * (lo + hi)
            ge = self._p(mid) >= y
            hi = np.where(ge, mid, hi)
            lo = np.where(ge, lo, mid)
        out = hi.copy()
        out[bad] = np.nan
        return out

    @property
    def lam50(self) -> float:
        """Intensity at which O-hat reaches 0.5*O_max (Sec. 3)."""
        return float(self.inverse(np.array([0.5 * self.O_max]))[0])


def silencing_grid(lam50: float, n: int = 10, lam_cap: float = 400.0, decimals: int = 2):
    """Sec. 5.3: n levels log-spaced from 0.5*lam50 to min(8*lam50, 400 Hz).  Rounded to `decimals`
    so the frozen values are exactly representable in the contract.  Also returns the >200 Hz flag."""
    hi = min(8.0 * lam50, lam_cap)
    g = np.round(np.geomspace(0.5 * lam50, hi, n), decimals)
    if np.any(np.diff(g) <= 0):
        raise ValueError('rounded grid not strictly increasing')
    return g, g > 200.0


# ------------------------------------------------------------------------------------------ helpers
def seed_weights(Y, duration_s: float = 1.0):
    """Inverse empirical per-lambda variance with floor (Sec. 6.3 weights). Y: (n_seeds, L)."""
    v = np.maximum(np.asarray(Y, float).var(0, ddof=1), var_floor(duration_s))
    return 1.0 / v


def hill(lam, E, l50, n):
    """Monotone Hill curve E*lam^n/(lam^n + l50^n), equal to 0 at lam = 0."""
    lam = np.asarray(lam, float)
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
        r = np.where(lam > 0, (l50 / np.where(lam > 0, lam, 1.0)) ** n, np.inf)
        return E / (1.0 + r)


def _pred_table(curve: MonotoneCurve, lam, fgrid=F_GRID):
    x = (1.0 - fgrid)[:, None] * np.asarray(lam, float)[None, :]
    return curve(x)


def _parabolic_refine(fgrid, ssr, i):
    """Vertex of the parabola through (i-1, i, i+1); None if not interior / not convex."""
    if i <= 0 or i >= len(fgrid) - 1:
        return None
    y0, y1, y2 = ssr[i - 1], ssr[i], ssr[i + 1]
    den = y0 - 2 * y1 + y2
    if not den > 0:
        return None
    h = fgrid[1] - fgrid[0]
    return fgrid[i] + 0.5 * h * (y0 - y2) / den


@dataclass
class ShiftFit:
    f: np.ndarray            # (N,)
    ssr: np.ndarray          # (N,) weighted SSR of seed MEANS (x n gives per-seed SSR minus const)
    plateau: np.ndarray      # (N,) bool: minimiser not unique (flat SSR); f = upper end of plateau
    plateau_lo: np.ndarray   # (N,) lower end of the tied set
    at_bound: np.ndarray     # (N,) bool: f at F_LO or F_HI
    extrap: np.ndarray       # (N,) fraction of grid points whose (1-f)lam is outside the intact grid


def fit_shift_many(curve: MonotoneCurve, lam, ybar, W, fgrid=F_GRID) -> ShiftFit:
    """Weighted LS fit of M_shift for many conditions sharing one grid.

    Minimises sum_s sum_j W_j (y_sj - O-hat((1-f) lam_j))^2.  Because the prediction does not depend on
    the seed, this equals n * sum_j W_j (ybar_j - pred_j)^2 + const, so means and per-seed rates give the
    identical minimiser (tested).  Global grid search on F_GRID, then parabolic refinement accepted only
    if it lowers the exact SSR.  Ties (flat SSR, e.g. an all-zero silenced curve): f = largest tied
    value, flagged as a plateau.
    """
    lam = np.asarray(lam, float)
    ybar = np.atleast_2d(np.asarray(ybar, float))
    W = np.atleast_2d(np.asarray(W, float))
    P = _pred_table(curve, lam, fgrid)                       # (F, L)
    a = (W * ybar ** 2).sum(1)[:, None]
    S = a - 2.0 * (W * ybar) @ P.T + W @ (P ** 2).T          # (N, F)
    S = np.maximum(S, 0.0)
    N = ybar.shape[0]
    f = np.empty(N); ssr = np.empty(N); plateau = np.zeros(N, bool); plo = np.empty(N)
    for k in range(N):
        s = S[k]
        m = s.min()
        tied = np.flatnonzero(s <= m + 1e-10 * (1.0 + m))
        i = int(tied[-1])
        if len(tied) >= 3 and np.all(np.diff(tied) == 1):     # genuine flat stretch of the SSR
            plateau[k] = True
            f[k], ssr[k], plo[k] = fgrid[i], s[i], fgrid[tied[0]]
            continue
        if len(tied) > 1 and not (len(tied) == 2 and tied[1] - tied[0] == 1):
            plateau[k] = True      # disjoint exact ties: take the largest, flag
        fi, si = fgrid[i], s[i]
        fr = _parabolic_refine(fgrid, s, i)
        if fr is not None:
            pr = curve((1.0 - fr) * lam)
            sr = float((W[k] * (ybar[k] - pr) ** 2).sum())
            if sr < si:
                fi, si = fr, sr
        f[k], ssr[k], plo[k] = fi, si, fi if not plateau[k] else fgrid[tied[0]]
    at_bound = (f <= fgrid[0] + 1e-12) | (f >= fgrid[-1] - 1e-12)
    x = (1.0 - f)[:, None] * lam[None, :]
    extrap = ((x < curve.lam_min) | (x > curve.lam_max)).mean(1)
    return ShiftFit(f, ssr, plateau, plo, at_bound, extrap)


def fit_gain(curve: MonotoneCurve, lam, ybar, W, fgrid=F_GRID):
    """M_gain: gamma*O-hat((1-f)lam), gamma >= 0 profiled in closed form for each f."""
    lam = np.asarray(lam, float); ybar = np.asarray(ybar, float); W = np.asarray(W, float)
    P = _pred_table(curve, lam, fgrid)
    A = (W * ybar * P).sum(1); B = (W * P * P).sum(1); C = (W * ybar ** 2).sum()

    def prof(A, B):
        g = np.where(B > 0, np.maximum(A / np.where(B > 0, B, 1.0), 0.0), 1.0)
        return g, np.maximum(C - 2 * g * A + g * g * B, 0.0)

    g, s = prof(A, B)
    m = s.min()
    i = int(np.flatnonzero(s <= m + 1e-10 * (1.0 + m))[-1])
    fi, gi, si = fgrid[i], g[i], s[i]
    fr = _parabolic_refine(fgrid, s, i)
    if fr is not None:
        p = curve((1.0 - fr) * lam)
        gr, sr = prof(np.array([(W * ybar * p).sum()]), np.array([(W * p * p).sum()]))
        if sr[0] < si:
            fi, gi, si = fr, gr[0], sr[0]
    return float(fi), float(gi), float(si)


def fit_free(lam, ybar, W, scale_hint: float | None = None):
    """M_free: monotone Hill (E, l50, n) by weighted LS, multi-start, log-parameterised."""
    lam = np.asarray(lam, float); ybar = np.asarray(ybar, float); W = np.asarray(W, float)
    sw = np.sqrt(W)
    ymax = max(float(ybar.max()), 1e-3)
    top = 10.0 * max(ymax, scale_hint or 0.0, 1.0)
    lo = np.log([1e-3, lam[lam > 0].min() / 20.0, 0.2])
    hi = np.log([top, lam.max() * 20.0, 30.0])

    def res(t):
        return sw * (ybar - hill(lam, *np.exp(t)))

    half = 0.5 * ymax
    above = np.flatnonzero(ybar >= half)
    l50_0 = float(lam[above[0]]) if above.size else float(lam.max())
    best = None
    for E0 in (1.05 * ymax, 1.5 * ymax):
        for l0 in (l50_0, float(np.sqrt(lam[lam > 0].min() * lam.max()))):
            for n0 in (1.0, 2.5, 6.0):
                t0 = np.clip(np.log([E0, max(l0, 1e-6), n0]), lo + 1e-9, hi - 1e-9)
                r = least_squares(res, t0, bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=400)
                if best is None or r.cost < best.cost:
                    best = r
    E, l50, n = np.exp(best.x)
    return (float(E), float(l50), float(n)), float(2.0 * best.cost)


def predict(model, params, curve, lam):
    lam = np.asarray(lam, float)
    if model == 'shift':
        return curve((1.0 - params[0]) * lam)
    if model == 'gain':
        return params[1] * curve((1.0 - params[0]) * lam)
    if model == 'free':
        return hill(lam, *params)
    raise ValueError(model)


def fit_model(model, curve, lam, ybar, W):
    if model == 'shift':
        fs = fit_shift_many(curve, lam, ybar[None, :], W[None, :])
        return (float(fs.f[0]),), float(fs.ssr[0])
    if model == 'gain':
        f, g, s = fit_gain(curve, lam, ybar, W)
        return (f, g), s
    if model == 'free':
        return fit_free(lam, ybar, W, scale_hint=curve.O_max)
    raise ValueError(model)


# ------------------------------------------------------------------------------------------ CV / GOF
def cv_folds(seeds, n_folds: int = N_FOLDS):
    """Deterministic folds: fold(seed) = rank(seed) mod n_folds over the sorted unique seeds."""
    s = np.sort(np.unique(np.asarray(seeds)))
    return [s[np.arange(len(s)) % n_folds == i] for i in range(n_folds)]


def cv_select(lam, Ysil, sil_seeds, intact_lam, intact_rates, intact_seeds, duration_s=1.0,
              n_folds=N_FOLDS, models=MODEL_ORDER):
    """5-fold CV over seeds; one-SE rule, simpler model wins (Sec. 6.3).

    For each fold the held-out seeds are removed from BOTH the silenced data and the training intact
    curve (they share CRN input trains).  O-hat and the weights are re-estimated on the training
    seeds; held-out error = mean over held-out (seed, lambda) of W_j (y - pred_j)^2 with training
    weights W (identical weights for all models in a fold).
    """
    Ysil = np.asarray(Ysil, float); sil_seeds = np.asarray(sil_seeds)
    intact_rates = np.asarray(intact_rates, float); intact_seeds = np.asarray(intact_seeds)
    folds = cv_folds(sil_seeds, n_folds)
    err = np.full((len(models), n_folds), np.nan)
    for i, fs in enumerate(folds):
        te = np.isin(sil_seeds, fs); tr = ~te
        cur = MonotoneCurve(intact_lam, intact_rates[~np.isin(intact_seeds, fs)], duration_s)
        W = seed_weights(Ysil[tr], duration_s)
        yb = Ysil[tr].mean(0)
        for m, model in enumerate(models):
            params, _ = fit_model(model, cur, lam, yb, W)
            pred = predict(model, params, cur, lam)
            err[m, i] = float((W * (Ysil[te] - pred) ** 2).mean())
    mean = err.mean(1)
    se = err.std(1, ddof=1) / math.sqrt(n_folds)
    best = int(np.argmin(mean))
    thr = mean[best] + se[best]
    sel = next(m for m in range(len(models)) if mean[m] <= thr)
    return dict(selected=models[sel], cv_err=dict(zip(models, mean)), cv_se=dict(zip(models, se)),
                cv_best=models[best], fold_err=err)


def gof_shift(lam, Ysil, fhat, indep: MonotoneCurve, duration_s=1.0):
    """Absolute chi^2 GOF of M_shift against the INDEPENDENT intact curve (Sec. 6.3):
        chi2 = sum_lam (Obar_k(lam) - O-hat_ind((1-f)lam))^2 / (s_k^2(lam)/n_k + s_O^2/n_O),  df = L-1.
    s_O^2 is the per-seed variance of the independent intact seeds at the evaluation point (1-f)lam,
    linearly interpolated between intact grid levels (choice C-5).  Both variances are floored."""
    lam = np.asarray(lam, float); Ysil = np.asarray(Ysil, float)
    vf = var_floor(duration_s)
    x = (1.0 - fhat) * lam
    pred, flag = indep(x, return_flag=True)
    sk2 = np.maximum(Ysil.var(0, ddof=1), vf)
    so2 = np.maximum(indep.var_at(x), vf)
    denom = sk2 / Ysil.shape[0] + so2 / indep.n
    chi2 = float(((Ysil.mean(0) - pred) ** 2 / denom).sum())
    df = lam.size - 1
    return dict(chi2=chi2, df=df, p=float(stats.chi2.sf(chi2, df)), gof_extrap=int(flag.sum()))


# ------------------------------------------------------------------------------------------ gates
def effect_gate(Ysil, Yint, B=EFFECT_BOOT, rng=None, alpha=0.05):
    """Sec. 6.1.  Ysil, Yint: (n_seeds, L), rows paired by seed (CRN).  Effect-bearing iff at >= 1 grid
    lambda with intact mean O >= 5 Hz BOTH the 95% seed-bootstrap percentile CI of the paired mean
    difference excludes 0 AND |N_k| >= 0.05.  Seeds are resampled jointly across lambda."""
    Ysil = np.asarray(Ysil, float); Yint = np.asarray(Yint, float)
    if Ysil.shape != Yint.shape:
        raise ValueError('paired arrays must have equal shape')
    rng = np.random.default_rng(0) if rng is None else rng
    D = Ysil - Yint
    S = D.shape[0]
    idx = rng.integers(0, S, size=(B, S))
    boot = D[idx].mean(1)
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)], axis=0)
    ci_excl = (lo > 0) | (hi < 0)
    O = Yint.mean(0)
    with np.errstate(divide='ignore', invalid='ignore'):
        w = np.where(O > 0, Ysil.mean(0) / O, np.nan)
    Nk = 1.0 - w
    elig = O >= EFFECT_MIN_RATE
    hit = elig & ci_excl & (np.abs(np.nan_to_num(Nk)) >= EFFECT_MIN_N)
    return dict(effect=bool(hit.any()), hit=hit, ci_lo=lo, ci_hi=hi, dbar=D.mean(0), w=w, N=Nk,
                eligible=elig)


def informativeness(curve: MonotoneCurve, lam, fhat):
    """Sec. 6.2: >= 2 lambda with O-hat((1-f)lam) in [0.2, 0.8] O_max and >= 1 with >= 0.9 O_max."""
    p = curve((1.0 - fhat) * np.asarray(lam, float))
    rel = p / curve.O_max
    n_mid = int(((rel >= INFO_BAND[0]) & (rel <= INFO_BAND[1])).sum())
    n_high = int((rel >= INFO_HIGH).sum())
    return dict(informative=(n_mid >= 2 and n_high >= 1), n_mid=n_mid, n_high=n_high)


def no_recovery(curve: MonotoneCurve, Ysil):
    return bool(np.all(np.asarray(Ysil, float).mean(0) < NO_RECOVERY * curve.O_max))


def assign_class(effect, norec, informative, selected, gof_p):
    """Class precedence (choice C-7): none > no-recovery > uninformative > CV/GOF classes.
    no-recovery precedes uninformative because a no-recovery curve always fails Sec. 6.2."""
    if not effect:
        return 'none'
    if norec:
        return 'no-recovery'
    if not informative:
        return 'uninformative'
    if selected == 'shift':
        return 'shift' if gof_p >= GOF_ALPHA else 'other'
    if selected == 'gain':
        return 'gain'
    return 'other'


def pointwise_f(curve: MonotoneCurve, lam, ybar):
    """Sec. 7.3 pointwise inversion: f_k(lam) = 1 - O-hat^{-1}(Obar_k(lam))/lam where
    Obar_k in [0.1, 0.9] O_max; NaN elsewhere."""
    lam = np.asarray(lam, float); ybar = np.asarray(ybar, float)
    ok = (ybar >= POINTWISE_BAND[0] * curve.O_max) & (ybar <= POINTWISE_BAND[1] * curve.O_max)
    x = curve.inverse(np.where(ok, ybar, np.nan))
    return np.where(ok, 1.0 - x / lam, np.nan)


# ------------------------------------------------------------------------------------------ per condition
@dataclass
class IntactData:
    """The 81-level intact curve (all 60 seeds) for one input set / readout."""
    lam: np.ndarray
    rates: np.ndarray          # (n_seeds, L)
    seeds: np.ndarray
    duration_s: float = 1.0
    train: MonotoneCurve = field(init=False)
    indep: MonotoneCurve = field(init=False)

    def __post_init__(self):
        self.lam = np.asarray(self.lam, float); self.rates = np.asarray(self.rates, float)
        self.seeds = np.asarray(self.seeds)
        tr = np.isin(self.seeds, TRAIN_SEEDS); ind = np.isin(self.seeds, INDEP_SEEDS)
        if tr.sum() < 2 or ind.sum() < 2:
            raise ValueError('intact data must contain training (0-29) and independent (30-59) seeds')
        self.train = MonotoneCurve(self.lam, self.rates[tr], self.duration_s)
        self.indep = MonotoneCurve(self.lam, self.rates[ind], self.duration_s)

    def train_subset(self, keep_seeds):
        m = np.isin(self.seeds, TRAIN_SEEDS) & np.isin(self.seeds, keep_seeds)
        return MonotoneCurve(self.lam, self.rates[m], self.duration_s)

    @property
    def train_rates(self):
        m = np.isin(self.seeds, TRAIN_SEEDS)
        return self.rates[m], self.seeds[m]


def analyze_condition(lam, Ysil, Yint, seeds, intact: IntactData, rng=None, do_cv=True):
    """Full Sec. 6.1-6.3 pipeline for one silencing condition.

    lam: (L,) silencing grid; Ysil, Yint: (n_seeds, L) per-seed rates, paired rows; seeds: (n_seeds,).
    Returns a flat dict (one row of the per-condition results table)."""
    lam = np.asarray(lam, float); Ysil = np.asarray(Ysil, float); Yint = np.asarray(Yint, float)
    seeds = np.asarray(seeds)
    if not (Ysil.shape == Yint.shape == (seeds.size, lam.size)):
        raise ValueError('shape mismatch')
    dur = intact.duration_s
    cur = intact.train
    W = seed_weights(Ysil, dur)
    ybar = Ysil.mean(0)
    sf = fit_shift_many(cur, lam, ybar[None], W[None])
    fhat = float(sf.f[0])
    eg = effect_gate(Ysil, Yint, rng=rng)
    inf = informativeness(cur, lam, fhat)
    norec = no_recovery(cur, Ysil)
    gof = gof_shift(lam, Ysil, fhat, intact.indep, dur)
    out = dict(fhat=fhat, ssr_shift=float(sf.ssr[0]), f_plateau=bool(sf.plateau[0]),
               f_plateau_lo=float(sf.plateau_lo[0]), f_at_bound=bool(sf.at_bound[0]),
               f_extrap_frac=float(sf.extrap[0]), effect=eg['effect'], n_effect_hits=int(eg['hit'].sum()),
               informative=inf['informative'], n_mid=inf['n_mid'], n_high=inf['n_high'],
               no_recovery=norec, gof_chi2=gof['chi2'], gof_df=gof['df'], gof_p=gof['p'],
               gof_extrap=gof['gof_extrap'])
    fg, gg, sg = fit_gain(cur, lam, ybar, W)
    (E, l50, nh), sh = fit_free(lam, ybar, W, scale_hint=cur.O_max)
    out.update(f_gain=fg, gamma=gg, ssr_gain=sg, hill_E=E, hill_l50=l50, hill_n=nh, ssr_free=sh)
    if do_cv:
        tr_rates, tr_seeds = intact.train_rates
        cv = cv_select(lam, Ysil, seeds, intact.lam, tr_rates, tr_seeds, dur)
        out.update(selected=cv['selected'], cv_best=cv['cv_best'],
                   **{f'cv_err_{m}': cv['cv_err'][m] for m in MODEL_ORDER},
                   **{f'cv_se_{m}': cv['cv_se'][m] for m in MODEL_ORDER})
    else:
        out['selected'] = None
    out['cls'] = assign_class(eg['effect'], norec, inf['informative'], out['selected'], gof['p'])
    # split-half (odd vs even seeds), each half against the intact curve built from the same half
    for name, par in (('odd', 1), ('even', 0)):
        m = (seeds % 2) == par
        ch = intact.train_subset(seeds[m])
        fh = fit_shift_many(ch, lam, Ysil[m].mean(0)[None], seed_weights(Ysil[m], dur)[None])
        out[f'fhat_{name}'] = float(fh.f[0])
    out['f_pointwise'] = pointwise_f(cur, lam, ybar)
    out['w'] = eg['w']; out['N'] = eg['N']; out['O_k'] = ybar; out['O'] = Yint.mean(0)
    return out


# ------------------------------------------------------------------------------------------ seed bootstrap
def seed_bootstrap_fhat(lam, Ysil_all, sil_seeds, intact: IntactData, R=2000, rng=None, return_curves=False):
    """Seed-level bootstrap replicates of f-hat for MANY conditions at once (nested layer of P-A, S6).

    In replicate r one vector of seed ids is drawn with replacement from the training seeds and applied
    jointly to (i) every condition's silenced runs and (ii) the training intact curve (CRN coupling makes
    the seed the shared resampling unit).  O-hat_r, weights and f-hat_r are all re-estimated.
    Ysil_all: (N, n_seeds, L).  Returns (R, N) array (and the R curves if requested)."""
    rng = np.random.default_rng(12345) if rng is None else rng
    Ysil_all = np.asarray(Ysil_all, float)
    sil_seeds = np.asarray(sil_seeds)
    tr_rates, tr_seeds = intact.train_rates
    pos_int = {int(s): i for i, s in enumerate(tr_seeds)}
    if not set(int(s) for s in sil_seeds) <= set(pos_int):
        raise ValueError('every screen seed must be an intact training seed (CRN pairing)')
    S = sil_seeds.size
    out = np.empty((R, Ysil_all.shape[0])); curves = []
    vf = var_floor(intact.duration_s)
    for r in range(R):
        ix = rng.integers(0, S, S)
        ii = np.array([pos_int[int(s)] for s in sil_seeds[ix]])
        cur = MonotoneCurve(intact.lam, tr_rates[ii], intact.duration_s)
        Yr = Ysil_all[:, ix, :]
        W = 1.0 / np.maximum(Yr.var(1, ddof=1), vf)
        out[r] = fit_shift_many(cur, lam, Yr.mean(1), W).f
        if return_curves:
            curves.append((ix, cur))
    return (out, curves) if return_curves else out


# ------------------------------------------------------------------------------------------ I/O
COUNTS_COLUMNS = {'condition_id': 'string', 'input_set': 'string', 'lambda_hz': 'float64', 'seed': 'int64',
                  'mn9_primary_count': 'int64', 'mn9_secondary_count': 'int64'}
CONDITIONS_COLUMNS = ('condition_id', 'kind', 'silenced_ids', 'input_set', 'lambda_hz', 'duration_s',
                      'flywire_version', 'label')
KINDS = ('intact', 'single', 'type', 'pair', 'subset', 'control')
READOUT_COL = {'primary': 'mn9_primary_count', 'secondary': 'mn9_secondary_count'}


def validate_screen(counts, conditions):
    """Check a screen against IO_CONTRACT.md; raises ValueError listing every violation."""
    errs = []
    for c in COUNTS_COLUMNS:
        if c not in counts.columns:
            errs.append(f'counts missing column {c}')
    for c in CONDITIONS_COLUMNS:
        if c not in conditions.columns:
            errs.append(f'conditions missing column {c}')
    if errs:
        raise ValueError('; '.join(errs))
    if conditions['condition_id'].duplicated().any():
        errs.append('duplicate condition_id in conditions table')
    if counts.duplicated(['condition_id', 'input_set', 'lambda_hz', 'seed']).any():
        errs.append('duplicate (condition_id, input_set, lambda_hz, seed) rows')
    unk = set(counts['condition_id']) - set(conditions['condition_id'])
    if unk:
        errs.append(f'{len(unk)} condition_ids in counts not in conditions')
    bad_kind = set(conditions['kind']) - set(KINDS)
    if bad_kind:
        errs.append(f'unknown kinds {sorted(bad_kind)}')
    for c in ('mn9_primary_count', 'mn9_secondary_count'):
        v = counts[c].to_numpy()
        if not np.issubdtype(v.dtype, np.integer) or (v < 0).any():
            errs.append(f'{c} must be non-negative integers')
    if counts[['lambda_hz', 'seed']].isna().any().any():
        errs.append('NaN lambda/seed')
    # every non-intact condition must have a paired intact baseline on the same (input_set, lambda, seed)
    ckind = conditions.set_index('condition_id')['kind']
    k = counts['condition_id'].map(ckind)
    base = counts[k == 'intact'][['input_set', 'lambda_hz', 'seed']].drop_duplicates()
    need = counts[k != 'intact'][['input_set', 'lambda_hz', 'seed']].drop_duplicates()
    miss = need.merge(base, how='left', indicator=True)
    nmiss = int((miss['_merge'] == 'left_only').sum())
    if nmiss:
        errs.append(f'{nmiss} (input_set, lambda, seed) cells lack a paired intact baseline')
    # complete factorial per condition
    for (cid, iset), g in counts.groupby(['condition_id', 'input_set']):
        nl, ns = g['lambda_hz'].nunique(), g['seed'].nunique()
        if len(g) != nl * ns:
            errs.append(f'{cid}/{iset}: incomplete lambda x seed design ({len(g)} rows, {nl}x{ns})')
            break
    if errs:
        raise ValueError('; '.join(errs))
    return True


def condition_matrix(counts, condition_id, input_set, readout='primary', duration_s=1.0, lam=None):
    """Return (lam, seeds, Y) with Y (n_seeds, L) rates in Hz for one condition."""
    g = counts[(counts['condition_id'] == condition_id) & (counts['input_set'] == input_set)]
    tab = g.pivot(index='seed', columns='lambda_hz', values=READOUT_COL[readout]).sort_index()
    if lam is not None:
        tab = tab.reindex(columns=np.asarray(lam, float))
    if tab.isna().any().any():
        raise ValueError(f'{condition_id}: missing cells')
    return tab.columns.to_numpy(float), tab.index.to_numpy(), tab.to_numpy(float) / duration_s


def analyze_screen(counts, conditions, intact_counts, intact_conditions, input_set, readout='primary',
                   rng_seed=20261103, do_cv=True):
    """Run analyze_condition for every non-intact condition of `input_set`.  Returns a DataFrame."""
    import pandas as pd
    validate_screen(counts, conditions)
    validate_screen(intact_counts, intact_conditions)
    dur = float(conditions['duration_s'].iloc[0])
    if not np.allclose(conditions['duration_s'], dur) or not np.allclose(intact_conditions['duration_s'], dur):
        raise ValueError('mixed durations')
    icid = intact_conditions.loc[intact_conditions['kind'] == 'intact', 'condition_id']
    if len(icid) != 1:
        raise ValueError('intact-curve file must hold exactly one intact condition')
    ilam, iseeds, irates = condition_matrix(intact_counts, icid.iloc[0], input_set, readout, dur)
    intact = IntactData(ilam, irates, iseeds, dur)
    ck = conditions.set_index('condition_id')['kind']
    sub = counts[counts['input_set'] == input_set]
    base_ids = [c for c in sub['condition_id'].unique() if ck[c] == 'intact']
    if len(base_ids) != 1:
        raise ValueError('screen must hold exactly one intact (paired baseline) condition per input set')
    lam, seeds, Yint = condition_matrix(sub, base_ids[0], input_set, readout, dur)
    rows = []
    for i, cid in enumerate(sorted(c for c in sub['condition_id'].unique() if ck[c] != 'intact')):
        l2, s2, Y = condition_matrix(sub, cid, input_set, readout, dur, lam=lam)
        if not np.array_equal(s2, seeds):
            raise ValueError(f'{cid}: seeds differ from the intact baseline')
        r = analyze_condition(lam, Y, Yint, seeds, intact, rng=np.random.default_rng([rng_seed, i]), do_cv=do_cv)
        r['condition_id'] = cid
        rows.append(r)
    return pd.DataFrame(rows), intact, lam
