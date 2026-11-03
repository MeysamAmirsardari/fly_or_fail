"""run_analysis: pre-registered analysis of the v783 screens (PROJECT_DESIGN v1.0 §6-7, D-009, D-010).

Wires the frozen inputs (intact curves, screens, structural predictors; analysis/out/FROZEN_MANIFEST.md5) into
curves.py and stats.py. No analysis choice is made here beyond those documented in the module constants of
curves.py / stats.py and the three items marked CHOICE below.

usage: python run_analysis.py fit [workers]     per-condition fits  -> out/fits_<screen>.parquet
       python run_analysis.py boot [workers]    seed-bootstrap f-hat replicates -> out/fhat_boot_single_shiu.npy
       python run_analysis.py stats             P-A, S1-S5 (Holm), RQ1, RQ2, S6, controls -> out/results_v783.json
"""
import sys, os, json, time
import numpy as np, pandas as pd
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [ROOT, HERE]
from analysis import curves as Cu, stats as St
import common as C

VER = 'v783'
OUT = C.OUT
B = St.B_DEFAULT
L0 = ['in_degree', 'out_degree', 'in_strength', 'out_strength', 'pagerank', 'betweenness', 'kcore_total',
      'neg_hop_to_T__contra']


def log(s):
    print(f'[{time.strftime("%H:%M:%S")}] {s}', flush=True)


def intact_data(inp, readout='contra'):
    z = np.load(OUT + f'intact_curve_{VER}_{inp}.npz')
    return Cu.IntactData(z['lam'], z[f'mn9_{readout}_rates'].T, z['seeds'], 1.0)


def screen(stem):
    return pd.read_parquet(OUT + f'{stem}.parquet'), pd.read_parquet(OUT + f'{stem}_conditions.parquet')


SCREENS = {'single_shiu': ('screen_single_shiu', 'S_shiu', 'shiu'),
           'types_pure': ('screen_types_pure', 'S_pure', 'pure')}


def _fit_one(args):
    lam, Y, Yint, seeds, inp, i, cid = args
    r = Cu.analyze_condition(lam, Y, Yint, seeds, intact_data(inp), rng=np.random.default_rng([20261103, i]))
    r['condition_id'] = cid
    return r


def fit(workers):
    for name, (stem, iset, inp) in SCREENS.items():
        counts, conds = screen(stem)
        Cu.validate_screen(counts, conds)
        ck = conds.set_index('condition_id')['kind']
        lam, seeds, Yint = Cu.condition_matrix(counts, 'intact', iset, 'primary')
        ids = sorted(c for c in conds.condition_id if ck[c] != 'intact')
        jobs = []
        for i, cid in enumerate(ids):
            _, s2, Y = Cu.condition_matrix(counts, cid, iset, 'primary', lam=lam)
            assert np.array_equal(s2, seeds)
            jobs.append((lam, Y, Yint, seeds, inp, i, cid))
        t0 = time.time()
        with Pool(workers) as p:
            rows = p.map(_fit_one, jobs, chunksize=4)
        df = pd.DataFrame(rows).merge(conds[['condition_id', 'kind', 'label', 'silenced_ids']], on='condition_id')
        for c in ('f_pointwise', 'w', 'N', 'O_k', 'O'):
            df[c] = df[c].apply(lambda a: [float(x) for x in a])
        df['silenced_ids'] = df['silenced_ids'].apply(lambda a: [int(x) for x in a])
        df.to_parquet(OUT + f'fits_{name}.parquet', index=False)
        json.dump(dict(lambda_hz=[float(x) for x in lam]), open(OUT + f'fits_{name}_lambda.json', 'w'))
        log(f'{name}: {len(df)} conditions fitted in {time.time() - t0:.0f}s')


def _boot_chunk(args):
    lam, Ysil, seeds, R, seed = args
    return Cu.seed_bootstrap_fhat(lam, Ysil, seeds, intact_data('shiu'), R=R, rng=np.random.default_rng(seed))


def boot(workers):
    counts, conds = screen('screen_single_shiu')
    lam, seeds, _ = Cu.condition_matrix(counts, 'intact', 'S_shiu', 'primary')
    ids = sorted(conds.condition_id[conds.kind == 'single'])
    Y = np.stack([Cu.condition_matrix(counts, c, 'S_shiu', 'primary', lam=lam)[2] for c in ids])
    per = int(np.ceil(B / workers))
    t0 = time.time()
    with Pool(workers) as p:
        parts = p.map(_boot_chunk, [(lam, Y, seeds, per, [20261105, w]) for w in range(workers)])
    reps = np.vstack(parts)[:B]
    np.save(OUT + 'fhat_boot_single_shiu.npy', reps)
    json.dump(dict(condition_ids=ids, R=int(reps.shape[0])), open(OUT + 'fhat_boot_single_shiu.json', 'w'))
    log(f'seed bootstrap: {reps.shape} in {time.time() - t0:.0f}s')


def _j(o):
    if isinstance(o, dict): return {str(k): _j(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_j(v) for v in o]
    if isinstance(o, np.ndarray): return _j(o.tolist())
    if isinstance(o, (np.floating, float)): return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o


def stats():
    res = {}
    fits = pd.read_parquet(OUT + 'fits_single_shiu.parquet')
    lam = np.array(json.load(open(OUT + 'fits_single_shiu_lambda.json'))['lambda_hz'])
    P = pd.read_parquet(OUT + f'predictors_{VER}.parquet').set_index('fid')
    sing = fits[fits.kind == 'single'].copy()
    sing['fid'] = sing.silenced_ids.str[0]
    sing = sing.sort_values('condition_id').reset_index(drop=True)
    boot_ids = json.load(open(OUT + 'fhat_boot_single_shiu.json'))['condition_ids']
    assert boot_ids == sing.condition_id.tolist()
    reps = np.load(OUT + 'fhat_boot_single_shiu.npy')
    X = P.loc[sing.fid]
    groups, n_single = St.make_groups(X.cell_type.values)
    fhat = sing.fhat.to_numpy()
    tag = '__shiu_contra'
    comp = {k: X[k].to_numpy(float) for k in L0}
    res['n_candidates'] = len(sing); res['n_groups'] = int(len(np.unique(groups))); res['n_singletons'] = n_single

    # ---------------- P-A (primary) and S1, S2
    PA = St.grouped_bootstrap_delta_rho(X['fLIN_A' + tag].to_numpy(float), comp, fhat, groups, reps)
    S1 = St.grouped_bootstrap_delta_rho(X['fLIN_A' + tag].to_numpy(float),
                                        {'rate_lam50': X['rate_lam50' + tag].to_numpy(float)}, fhat, groups, reps)
    S2 = St.grouped_bootstrap_delta_rho(X['fLIN_S' + tag].to_numpy(float), comp, fhat, groups, reps)
    strip = lambda d: {k: v for k, v in d.items() if k != 'boot'}
    res['P_A'] = strip(PA); res['S1'] = strip(S1); res['S2'] = strip(S2)
    res['P_A']['lower_2p5'] = float(np.percentile(PA['boot'], 2.5))          # D-009 item 3, also reported
    # sensitivity: dependent-correlation test against the selected competitor, shift-class subset, disattenuation
    res['P_A_williams'] = St.dependent_corr_test(X['fLIN_A' + tag].to_numpy(float), comp[PA['best']], fhat,
                                                 n_eff=res['n_groups'])
    shift = (sing.cls == 'shift').to_numpy()
    if shift.sum() >= 10:
        res['P_A_shift_only'] = strip(St.grouped_bootstrap_delta_rho(X['fLIN_A' + tag].to_numpy(float), comp,
                                                                     fhat, groups, reps, mask=shift))
    rel = St.split_half_reliability(sing.fhat_odd.to_numpy(), sing.fhat_even.to_numpy())
    res['reliability'] = rel
    res['P_A_disattenuated_rho_star'] = St.disattenuate(PA['rho_star'], rel['rel_spearman_brown'])

    # ---------------- S3: dominators (excitatory active graph at lam50; GRNs and T excluded by STRUCT)
    dom = X['dominator_active' + tag].astype(bool).to_numpy()
    res['S3'] = St.s3_dominators(sing.cls[dom].tolist())
    res['S3']['dominator_fids'] = sing.fid[dom].tolist()
    res['S3']['classes'] = sing.cls[dom].tolist()

    # ---------------- S4, S5: external types (S_pure input, whole-type silencing)
    tf = pd.read_parquet(OUT + 'fits_types_pure.parquet')
    tf = tf[tf.kind == 'type'].set_index('label')
    f_type = tf.fhat.to_dict()
    res['types'] = tf[['fhat', 'cls', 'effect', 'informative', 'selected', 'gof_p', 'no_recovery']].to_dict('index')
    s4 = St.s4_exact({k: f_type[k] for k in St.S4_TYPES})
    res['S4'] = {k: v for k, v in s4.items() if k != 'null'}
    res['S4_variants'] = dict(
        abs_f={k: v for k, v in St.s4_exact({k: abs(f_type[k]) for k in St.S4_TYPES}).items() if k != 'null'},
        sens_tiers={k: v for k, v in St.s4_exact({k: f_type[k] for k in St.S4_TYPES}, St.S4_TIERS_SENS).items() if k != 'null'},
        top2=St.s4_top2({k: f_type[k] for k in St.S4_TYPES}))
    res['S5'] = St.s5_layer({k: f_type[k] for k in St.S4_TYPES}, {k: f_type[k] for k in St.S5_LAYER3})

    # ---------------- Holm over S1-S5 (S3 leaves the family if < 5 dominators, D-009)
    pv = dict(S1=S1['p_one_sided'], S2=S2['p_one_sided'], S3=res['S3']['p'], S4=res['S4']['p'], S5=res['S5']['p'])
    res['holm'] = {k: dict(p_raw=pv[k], p_adj=v[0], reject=v[1]) for k, v in St.holm(pv).items()}

    # ---------------- RQ2: classes, collapse fraction
    res['RQ2'] = St.rq2_summary(sing.cls.to_numpy(), groups)

    # ---------------- RQ1: per-lambda Spearman / AUPRC of N_k(lambda)
    N = np.vstack(sing.N.to_numpy())
    preds = dict(comp, **{k: X[k + tag].to_numpy(float) for k in
                          ('fLIN_S', 'fMF_S', 'walks_through_L5', 'rate_lam50', 'fLIN_A', 'fLIN_A_r0', 'fMF_A',
                           'mincut_participation')})
    rq1 = pd.DataFrame(St.rq1_per_lambda(N, preds))
    rq1['lambda_hz'] = lam[rq1.j]
    rq1.to_csv(OUT + 'results_rq1_per_lambda.csv', index=False)
    res['RQ1_rho_at_lam'] = rq1.pivot(index='predictor', columns='lambda_hz', values='rho').round(3).to_dict('index')
    res['rho_fhat_all_predictors'] = {k: St.spearman(v, fhat) for k, v in preds.items()}
    # confound: partial Spearman of f^LIN-A with f-hat given hop distance and baseline rate
    res['partial_rho_fLIN_A'] = St.partial_spearman(X['fLIN_A' + tag].to_numpy(float), fhat,
                                                    [comp['neg_hop_to_T__contra'], X['rate_lam50' + tag].to_numpy(float)])

    # ---------------- S6: summation over C1 (direct postsynaptic partners of S; silent members contribute 0)
    counts, conds = screen('screen_single_shiu')
    hop1 = set(P.index[(P['hop_from_S_all__shiu'] == 1) & ~P['is_S__shiu']].astype(int))
    c1 = sing[sing.fid.isin(hop1)].condition_id.tolist()
    lam_s, seeds, _ = Cu.condition_matrix(counts, 'intact', 'S_shiu', 'primary')
    Y1 = np.stack([Cu.condition_matrix(counts, c, 'S_shiu', 'primary', lam=lam_s)[2] for c in c1])
    s6 = St.s6_summation(lam_s, Y1, seeds, intact_data('shiu'))
    res['S6'] = dict(n_C1_total=len(hop1), n_C1_active=len(c1), **{k: v for k, v in s6.items()})

    # ---------------- controls (D-010 for T)
    ctl = fits[fits.kind == 'control'].set_index('label')
    res['controls'] = dict(
        T=ctl.loc['T', ['fhat', 'cls', 'effect']].to_dict(),
        all_S_no_output=bool(np.max(np.vstack(ctl.loc['all_S', 'O_k'])) == 0),
        grn=ctl[ctl.index.str.startswith('grn:')][['fhat', 'cls']].assign(
            fLIN_S=[float(P.loc[int(l.split(':')[1]), 'fLIN_S' + tag]) for l in ctl.index if l.startswith('grn:')]
        ).to_dict('index'))
    res['controls']['grn_rho_fhat_fLIN_S'] = St.spearman(
        np.array([v['fhat'] for v in res['controls']['grn'].values()]),
        np.array([v['fLIN_S'] for v in res['controls']['grn'].values()]))
    json.dump(_j(res), open(OUT + f'results_{VER}.json', 'w'), indent=1)
    log('wrote results_v783.json')


if __name__ == '__main__':
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    step = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    {'fit': lambda: fit(w), 'boot': lambda: boot(w), 'stats': stats}[step]()
