"""Synthetic screen generator with KNOWN ground truth (planted f, planted gain loss, planted shape change,
planted noise).  Used only by the tests and by run_validation.py; never by the real analysis.

Noise model: per-seed spike count in a 1 s trial = max(0, round(mu + sd*z)), sd^2 = FANO*mu (Gaussian with
Fano ~ 0.65, as measured for MN9 [V-src]).  CRN pairing: the silenced condition's z at (seed, lambda) shares
a component with the paired intact baseline's z (correlation `crn_rho`); f = 0 with crn_rho = 1 gives
bit-identical counts, as CRN does in the simulator.
"""
import numpy as np

FANO = 0.65
INTACT_LAM = np.arange(0.0, 400.0 + 1e-9, 5.0)
SEEDS_TRAIN = np.arange(30)
SEEDS_ALL = np.arange(60)


def hill_curve(E=85.0, l50=63.0, n=3.0):
    def O(lam):
        lam = np.asarray(lam, float)
        with np.errstate(divide='ignore'):
            return np.where(lam > 0, E / (1.0 + (l50 / np.where(lam > 0, lam, 1.0)) ** n), 0.0)
    O.params = dict(kind='hill', E=E, l50=l50, n=n)
    return O


def two_route_curve(E1=55.0, l1=50.0, n1=4.0, E2=30.0, l2=140.0, n2=3.0):
    """A non-Hill intact curve (two thresholded routes) so that M_free does not nest M_shift."""
    def O(lam):
        lam = np.asarray(lam, float)
        with np.errstate(divide='ignore'):
            safe = np.where(lam > 0, lam, 1.0)
            return np.where(lam > 0, E1 / (1 + (l1 / safe) ** n1) + E2 / (1 + (l2 / safe) ** n2), 0.0)
    O.params = dict(kind='two_route')
    return O


def counts_from_mean(mu, z):
    mu = np.asarray(mu, float)
    return np.maximum(0.0, np.round(mu + np.sqrt(FANO * np.maximum(mu, 0.0)) * z))


def intact_curve_data(O, rng, lam=INTACT_LAM, seeds=SEEDS_ALL):
    z = rng.standard_normal((seeds.size, lam.size))
    return lam, seeds, counts_from_mean(O(lam)[None, :], z)


def silenced_mean(O, lam, kind='shift', f=0.0, gamma=1.0, other=None):
    lam = np.asarray(lam, float)
    if kind == 'shift':
        return O((1 - f) * lam)
    if kind == 'gain':
        return gamma * O((1 - f) * lam)
    if kind == 'other':          # shape change: a different Hill (shallower) through the same lam50 shift
        return other(lam)
    if kind == 'zero':
        return np.zeros_like(lam)
    raise ValueError(kind)


def screen_pair(O, lam, rng, kind='shift', f=0.0, gamma=1.0, other=None, crn_rho=0.5, seeds=SEEDS_TRAIN):
    """Paired (silenced, intact-baseline) per-seed rates on the silencing grid."""
    z0 = rng.standard_normal((seeds.size, lam.size))
    if kind == 'shift' and f == 0.0 and crn_rho >= 1.0:
        Yi = counts_from_mean(O(lam)[None, :], z0)
        return Yi.copy(), Yi
    z1 = crn_rho * z0 + np.sqrt(1 - crn_rho ** 2) * rng.standard_normal(z0.shape)
    Yi = counts_from_mean(O(lam)[None, :], z0)
    Ys = counts_from_mean(silenced_mean(O, lam, kind, f, gamma, other)[None, :], z1)
    return Ys, Yi


def default_grid(O):
    """Frozen-grid rule of Sec. 5.3 applied to the TRUE curve (the tests also exercise the estimated one)."""
    from analysis.curves import silencing_grid
    lam_d = np.linspace(0.01, 400, 400001)
    vals = O(lam_d)
    omax = O(INTACT_LAM).max()
    l50 = lam_d[np.argmax(vals >= 0.5 * omax)]
    return silencing_grid(l50)[0]
