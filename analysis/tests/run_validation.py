"""Monte Carlo validation of curves.py / stats.py on synthetic data with planted ground truth.

Writes analysis/out/validation_synthetic.json (all numbers quoted in ANALYSIS_VALIDATION.md).
Run (single core):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 venv/bin/python analysis/tests/run_validation.py [M]
"""
import json
import os
import sys
import time
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [ROOT, HERE]

import numpy as np
import pandas as pd

from analysis import curves as C
from analysis import stats as St
import synth as S

M = int(sys.argv[1]) if len(sys.argv) > 1 else 200
OUT = os.path.join(ROOT, 'analysis', 'out', 'validation_synthetic.json')
t_start = time.time()
res = dict(M=M, fano_target=S.FANO)


def log(*a):
    print(f'[{time.time() - t_start:7.1f}s]', *a, flush=True)


def scenarios(O):
    gated = lambda lam: O(lam) * (1 - 0.5 / (1 + np.exp(-(np.asarray(lam) - 150.0) / 15.0)))
    shallow = lambda lam: C.hill(lam, 85.0, 63.0 / 0.8, 1.2)
    return [
        ('none_f0_crn', dict(kind='shift', f=0.0, crn=1.0), 'none'),
        ('none_f0_indep', dict(kind='shift', f=0.0, crn=0.5), 'none'),
        ('shift_f0.05', dict(kind='shift', f=0.05), 'shift'),
        ('shift_f0.2', dict(kind='shift', f=0.2), 'shift'),
        ('shift_f0.5', dict(kind='shift', f=0.5), 'shift'),
        ('shift_f-0.2', dict(kind='shift', f=-0.2), 'shift'),
        ('uninf_f0.9', dict(kind='shift', f=0.9), 'uninformative'),
        ('uninf_satgrid_f0.6', dict(kind='shift', f=0.6, lam=np.round(np.geomspace(300, 400, 10), 2)),
         'uninformative'),
        ('norec_zero', dict(kind='zero', f=0.0), 'no-recovery'),
        ('gain_g0.85_f0.2', dict(kind='gain', f=0.2, gamma=0.85), 'gain'),
        ('gain_g0.7_f0.2', dict(kind='gain', f=0.2, gamma=0.7), 'gain'),
        ('gain_g0.5_f0.2', dict(kind='gain', f=0.2, gamma=0.5), 'gain'),
        ('other_shallow', dict(kind='other', other=shallow), 'other'),
        ('other_lamgated', dict(kind='other', other=gated), 'other'),
    ]


def run_curve_family(name, O):
    lam0 = S.default_grid(O)
    out = {}
    for sc, kw, truth in scenarios(O):
        rng = np.random.default_rng(zlib.crc32(f'{name}/{sc}'.encode()))
        lam = kw.get('lam', lam0)
        rows = []
        for r in range(M):
            lam_i, sd, rr = S.intact_curve_data(O, rng)
            I = C.IntactData(lam_i, rr, sd)
            Ys, Yi = S.screen_pair(O, lam, rng, kw['kind'], kw.get('f', 0.0), kw.get('gamma', 1.0),
                                   other=kw.get('other'), crn_rho=kw.get('crn', 0.5))
            a = C.analyze_condition(lam, Ys, Yi, S.SEEDS_TRAIN, I, rng=np.random.default_rng(r))
            rows.append({k: v for k, v in a.items() if not isinstance(v, np.ndarray)})
        d = pd.DataFrame(rows)
        f_true = kw.get('f', np.nan) if kw['kind'] in ('shift',) else np.nan
        e = d['fhat'] - f_true
        out[sc] = dict(
            truth=truth, n=M, accuracy=float((d['cls'] == truth).mean()),
            classes={c: float((d['cls'] == c).mean()) for c in C.CLASSES},
            cv_selected={m: float((d['selected'] == m).mean()) for m in C.MODEL_ORDER},
            effect_rate=float(d['effect'].mean()), informative_rate=float(d['informative'].mean()),
            gof_reject=float((d['gof_p'] < 0.05).mean()),
            f_true=None if np.isnan(f_true) else f_true,
            f_bias=None if np.isnan(f_true) else float(e.mean()),
            f_rmse=None if np.isnan(f_true) else float(np.sqrt((e ** 2).mean())),
            f_abs95=None if np.isnan(f_true) else float(np.quantile(np.abs(e), 0.95)),
            fhat_mean=float(d['fhat'].mean()),
            gamma_mean=float(d['gamma'].mean()) if kw['kind'] == 'gain' else None,
            f_gain_mean=float(d['f_gain'].mean()) if kw['kind'] == 'gain' else None,
            splithalf_sd=float((d['fhat_odd'] - d['fhat_even']).std()),
        )
        log(name, sc, 'acc=%.3f' % out[sc]['accuracy'], out[sc]['classes'], 'f_bias', out[sc]['f_bias'],
            'f_rmse', out[sc]['f_rmse'], 'gof_rej', out[sc]['gof_reject'])
    return out


def gof_size(O, n=2000):
    lam = S.default_grid(O)
    rng = np.random.default_rng(777)
    out = {}
    for f in (0.05, 0.2, 0.5, -0.2):
        p = []; inf = []
        for r in range(n):
            lam_i, sd, rr = S.intact_curve_data(O, rng)
            I = C.IntactData(lam_i, rr, sd)
            Ys, _ = S.screen_pair(O, lam, rng, 'shift', f)
            fh = C.fit_shift_many(I.train, lam, Ys.mean(0)[None], C.seed_weights(Ys)[None]).f[0]
            p.append(C.gof_shift(lam, Ys, fh, I.indep)['p'])
        p = np.array(p)
        out[str(f)] = dict(n=n, size=float(np.mean(p < 0.05)), size_01=float(np.mean(p < 0.01)),
                           ks_uniform_p=float(__import__('scipy').stats.kstest(p, 'uniform').pvalue))
        log('GOF size', f, out[str(f)])
    return out


def fano_check(O):
    rng = np.random.default_rng(5)
    lam = np.array([50.0, 100.0, 200.0])
    Y = S.counts_from_mean(O(lam)[None], rng.standard_normal((20000, 3)))
    return {str(l): float(Y[:, j].var() / Y[:, j].mean()) for j, l in enumerate(lam)}


def pa_calibration(n_sets=200, B=1000):
    rng = np.random.default_rng(99)

    def pop(sx, sc, G=200, per=2):
        u = rng.normal(size=G); g = np.repeat(np.arange(G), per)
        f = u[g] + 0.3 * rng.normal(size=G * per)
        xs = u[g] + sx * rng.normal(size=G * per)
        comps = {f'c{i}': u[g] + (sc if i == 0 else 2.5) * rng.normal(size=G * per) for i in range(8)}
        return f, xs, comps, g

    out = {}
    for lab, sx, sc in (('H0_equal', 0.6, 0.6), ('H1_moderate', 0.45, 0.75), ('H1_strong', 0.3, 1.0)):
        dec, deltas, williams = [], [], []
        for _ in range(n_sets):
            f, xs, comps, g = pop(sx, sc)
            r = St.grouped_bootstrap_delta_rho(xs, comps, f, g, B=B, seed=int(rng.integers(2 ** 31)))
            dec.append(r['decision']); deltas.append(r['delta'])
            w = St.dependent_corr_test(xs, comps[r['best']], f, n_eff=r['n_groups'])
            williams.append(w['williams_p_one'] < 0.05)
        out[lab] = dict(n_sets=n_sets, B=B, decision_rate=float(np.mean(dec)), mean_delta=float(np.mean(deltas)),
                        williams_one_sided_rate=float(np.mean(williams)))
        log('P-A', lab, out[lab])
    return out


def nested_end_to_end(N_types=100, per=2, R=300, B=300):
    """Synthetic screen: planted f per neuron from a type-level latent, simulated curves, full pipeline,
    seed-bootstrap replicates, nested grouped bootstrap.  Also times R = 2000 replicates for N = 400."""
    O = S.hill_curve(); lam = S.default_grid(O)
    rng = np.random.default_rng(2024)
    lam_i, sd, rr = S.intact_curve_data(O, rng)
    I = C.IntactData(lam_i, rr, sd)
    g = np.repeat(np.arange(N_types), per)
    u = rng.uniform(0.02, 0.6, N_types)
    f_true = np.clip(u[g] + 0.03 * rng.normal(size=g.size), 0.0, 0.8)
    Ys = np.stack([S.counts_from_mean(O((1 - f) * lam)[None], rng.standard_normal((30, lam.size))) for f in f_true])
    W = 1 / np.maximum(Ys.var(1, ddof=1), 1.0)
    fhat = C.fit_shift_many(I.train, lam, Ys.mean(1), W).f
    t0 = time.time()
    reps = C.seed_bootstrap_fhat(lam, Ys, S.SEEDS_TRAIN, I, R=R, rng=np.random.default_rng(1))
    t_rep = (time.time() - t0) / R
    xs = f_true + 0.08 * rng.normal(size=g.size)
    comps = {f'c{i}': f_true + 0.3 * rng.normal(size=g.size) for i in range(8)}
    a = St.grouped_bootstrap_delta_rho(xs, comps, fhat, g, B=B)
    b = St.grouped_bootstrap_delta_rho(xs, comps, fhat, g, fhat_reps=reps, B=B)
    sh = St.split_half_reliability(*[C.fit_shift_many(I.train_subset(np.arange(par, 30, 2)), lam,
                                                       Ys[:, par::2].mean(1), 1 / np.maximum(Ys[:, par::2].var(1, ddof=1), 1.0)).f
                                     for par in (1, 0)])
    # timing at production scale
    Ybig = np.concatenate([Ys, Ys])
    t0 = time.time()
    C.seed_bootstrap_fhat(lam, Ybig, S.SEEDS_TRAIN, I, R=50, rng=np.random.default_rng(2))
    t400 = (time.time() - t0) / 50
    t0 = time.time()
    St.grouped_bootstrap_delta_rho(np.concatenate([xs, xs]), {k: np.concatenate([v, v]) for k, v in comps.items()},
                                   np.concatenate([fhat, fhat]), np.concatenate([g, g + N_types]), B=200)
    tpa = (time.time() - t0) / 200
    out = dict(N=int(g.size), n_types=N_types, fhat_rmse=float(np.sqrt(np.mean((fhat - f_true) ** 2))),
               rep_sd_mean=float(reps.std(0, ddof=1).mean()), sec_per_rep_N200=t_rep,
               ci_without_nested=a['ci_two_sided'], ci_with_nested=b['ci_two_sided'],
               sd_without=float(a['boot'].std()), sd_with=float(b['boot'].std()),
               splithalf=sh,
               est_minutes_R2000_N400=2000 * t400 / 60, est_minutes_PA_B2000_N400=2000 * tpa / 60)
    log('nested end-to-end', out)
    return out


def full_condition_timing():
    O = S.hill_curve(); lam = S.default_grid(O)
    rng = np.random.default_rng(3)
    lam_i, sd, rr = S.intact_curve_data(O, rng)
    I = C.IntactData(lam_i, rr, sd)
    t0 = time.time()
    for r in range(20):
        Ys, Yi = S.screen_pair(O, lam, rng, 'shift', 0.3)
        C.analyze_condition(lam, Ys, Yi, S.SEEDS_TRAIN, I)
    return (time.time() - t0) / 20


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[2] == 'curves':
    # D-009 re-run: only the per-condition pipeline changed (effect gate, informativeness gate)
    OUT = os.path.join(ROOT, 'analysis', 'out', 'validation_synthetic_d009.json')
    res['note'] = 'D-009 re-run of the curve scenarios; GOF size, P-A and nested results unchanged (see validation_synthetic.json)'
    res['curves_hill'] = run_curve_family('hill', S.hill_curve())
    res['curves_two_route'] = run_curve_family('two_route', S.two_route_curve())
    res['runtime_s'] = time.time() - t_start
    with open(OUT, 'w') as fh:
        json.dump(res, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    log('wrote', OUT)
    sys.exit(0)

if __name__ == '__main__':
    res['fano_realised'] = fano_check(S.hill_curve())
    res['sec_per_condition'] = full_condition_timing()
    log('fano', res['fano_realised'], 'sec/condition', res['sec_per_condition'])
    res['gof_size_hill'] = gof_size(S.hill_curve(), n=10 * M)
    res['gof_size_two_route'] = gof_size(S.two_route_curve(), n=5 * M)
    res['curves_hill'] = run_curve_family('hill', S.hill_curve())
    res['curves_two_route'] = run_curve_family('two_route', S.two_route_curve())
    res['pa'] = pa_calibration(n_sets=M, B=1000 if M >= 100 else 100)
    res['nested'] = nested_end_to_end(R=300 if M >= 100 else 20, B=300 if M >= 100 else 20)
    res['runtime_s'] = time.time() - t_start
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as fh:
        json.dump(res, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    log('wrote', OUT)
