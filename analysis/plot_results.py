"""plot_results: overview figures of the v783 analysis (reads only analysis/out/; writes analysis/figures/).

usage: python plot_results.py            -> figures/fig_<name>.png (one per panel) and figures/overview.pdf
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE), HERE]
from analysis import curves as Cu, stats as St
import common as C

OUT = C.OUT
FIG = os.path.join(HERE, 'figures')
os.makedirs(FIG, exist_ok=True)

# reference categorical palette (fixed order); neutral grays for "none" and reference curves
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6'
INK, INK2, GRID, NONE = '#0b0b0b', '#52514e', '#e4e3df', '#b5b4ad'
CLS_COLOR = {'shift': BLUE, 'gain': ORANGE, 'other': AQUA, 'none': NONE}
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica Neue', 'Arial', 'DejaVu Sans'], 'font.size': 9,
    'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'axes.linewidth': 0.8, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
    'xtick.color': INK2, 'ytick.color': INK2, 'legend.frameon': False, 'figure.dpi': 150, 'savefig.dpi': 200,
    'savefig.bbox': 'tight', 'lines.linewidth': 2, 'axes.axisbelow': True})


def log_lam_axis(ax):
    ax.set_xscale('log'); ax.minorticks_off()
    ax.set_xticks([50, 100, 200, 400], ['50', '100', '200', '400'])

R = json.load(open(OUT + 'results_v783.json'))
fits = pd.read_parquet(OUT + 'fits_single_shiu.parquet')
LAM = np.array(json.load(open(OUT + 'fits_single_shiu_lambda.json'))['lambda_hz'])
P = pd.read_parquet(OUT + 'predictors_v783.parquet').set_index('fid')
sing = fits[fits.kind == 'single'].copy()
sing['fid'] = sing.silenced_ids.str[0]
X = P.loc[sing.fid]
TAG = '__shiu_contra'


def intact(inp):
    z = np.load(OUT + f'intact_curve_v783_{inp}.npz')
    return Cu.IntactData(z['lam'], z['mn9_contra_rates'].T, z['seeds'], 1.0)


def fig_intact(ax):
    for inp, col, lab in (('shiu', BLUE, 'S_shiu (20 GRNs)'), ('pure', ORANGE, 'S_pure (33 GRNs)')):
        I = intact(inp); tr = I.rates[np.isin(I.seeds, Cu.TRAIN_SEEDS)]
        m = tr.mean(0); se = tr.std(0, ddof=1) / np.sqrt(len(tr))
        ax.fill_between(I.lam, m - 1.96 * se, m + 1.96 * se, color=col, alpha=0.2, lw=0)
        ax.plot(I.lam, m, color=col, label=lab)
        ax.axvline(I.train.lam50, color=col, lw=0.8, ls=':')
    grid = json.load(open(OUT + 'frozen_grid_v783.json'))['shiu']['lambda_hz']
    ax.plot(grid, np.full(len(grid), -4), '|', color=INK2, ms=6, mew=1)
    ax.text(grid[0], -9, 'silencing grid (S_shiu)', fontsize=7, color=INK2)
    ax.set(xlabel='GRN input rate λ (Hz)', ylabel='MN9 rate (Hz)', title='Intact dose–response (contralateral MN9)',
           ylim=(-12, None))
    ax.legend(loc='upper left')


def fig_examples(axs):
    I = intact('shiu'); cur = I.train
    lamf = np.linspace(LAM[0], LAM[-1], 300)
    eff = sing[sing.effect]
    for ax, cls in zip(axs, ('shift', 'gain', 'other')):
        sub = eff[eff.cls == cls]
        row = sub.loc[sub.fhat.abs().idxmax()]
        ax.plot(lamf, cur(lamf), color=NONE, label='intact Ô(λ)')
        ax.plot(lamf, cur((1 - row.fhat) * lamf), color=CLS_COLOR[cls], lw=1.5, ls='--', label=f'shift fit, f̂ = {row.fhat:.2f}')
        if row.selected == 'gain':
            ax.plot(lamf, row.gamma * cur((1 - row.f_gain) * lamf), color=CLS_COLOR[cls], lw=1.5,
                    label=f'gain fit, f = {row.f_gain:.2f}, γ = {row.gamma:.2f}')
        elif row.selected == 'free':
            ax.plot(lamf, Cu.hill(lamf, row.hill_E, row.hill_l50, row.hill_n), color=CLS_COLOR[cls], lw=1.5, label='Hill fit')
        ax.plot(LAM, row.O_k, 'o', color=CLS_COLOR[cls], ms=5, mec='white', mew=0.8, label='silenced (mean)')
        ct = P.loc[row.fid, 'cell_type']
        log_lam_axis(ax)
        ax.set(xlabel='λ (Hz)', title=f'{cls}: {ct if isinstance(ct, str) else row.fid} (GOF p = {row.gof_p:.2g})')
        ax.legend(fontsize=7, loc='upper left')
    axs[0].set_ylabel('MN9 rate (Hz)')


def fig_pa(ax):
    x = X['fLIN_A' + TAG].to_numpy(float); f = sing.fhat.to_numpy()
    for cls in ('none', 'shift', 'gain', 'other'):
        m = (sing.cls == cls).to_numpy()
        ax.scatter(x[m], f[m], s=10 if cls == 'none' else 18, color=CLS_COLOR[cls], alpha=0.5 if cls == 'none' else 0.9,
                   lw=0.4, edgecolor='white', label=f'{cls} (n={m.sum()})', zorder=1 if cls == 'none' else 3)
    ax.set_xscale('symlog', linthresh=1e-3); ax.set_yscale('symlog', linthresh=1e-2)
    pa = R['P_A']
    ax.text(0.03, 0.97, f"ρ_s = {pa['rho_star']:.2f}\nΔρ vs best centrality = {pa['delta']:.2f}\n"
            f"one-sided 95% lower bound = {pa['lower_one_sided']:.3f}", transform=ax.transAxes, va='top', fontsize=8)
    ax.set(xlabel='structural estimate f^LIN-A (symlog)', ylabel='simulated f̂ (symlog)',
           title='Primary test: structure predicts f̂')
    ax.legend(loc='lower right', fontsize=7)


FAMILY = {'L0 (classical)': ['in_degree', 'out_degree', 'in_strength', 'out_strength', 'pagerank', 'betweenness',
                             'kcore_total', 'neg_hop_to_T__contra'],
          'L1 (structure only)': ['fLIN_S', 'fMF_S', 'walks_through_L5'],
          'L2 (activity-aware)': ['rate_lam50', 'fLIN_A', 'fLIN_A_r0', 'fMF_A', 'mincut_participation']}
FAM_COLOR = {'L0 (classical)': NONE, 'L1 (structure only)': AQUA, 'L2 (activity-aware)': BLUE}


def fig_rho(ax):
    rho = R['rho_fhat_all_predictors']; y = 0; ticks = []
    for fam, keys in FAMILY.items():
        for k in keys:
            ax.barh(y, rho[k], color=FAM_COLOR[fam], height=0.7)
            ticks.append((y, k.replace('__contra', ''))); y += 1
        y += 0.6
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7); ax.invert_yaxis()
    ax.grid(axis='y', visible=False)
    for fam, c in FAM_COLOR.items():
        ax.barh(np.nan, 0, color=c, label=fam)
    ax.legend(loc='lower right', fontsize=7)
    ax.set(xlabel='Spearman ρ with f̂ (573 neurons)', title='All predictors')


def fig_rq1(ax):
    rq = pd.read_csv(OUT + 'results_rq1_per_lambda.csv')
    show = [('fLIN_A', BLUE), ('fLIN_S', AQUA), ('out_strength', ORANGE), ('kcore_total', YELLOW), ('rate_lam50', MAGENTA)]
    for k, col in show:
        d = rq[rq.predictor == k].sort_values('lambda_hz')
        ax.plot(d.lambda_hz, d.rho, '-o', color=col, ms=4, mec='white', mew=0.6, label=k)
    ax.axhline(0, color=INK2, lw=0.8)
    log_lam_axis(ax)
    ax.set(xlabel='λ (Hz)', ylabel='Spearman ρ with N_k(λ)', title='RQ1: prediction across intensities')
    ax.legend(fontsize=7, loc='upper left', bbox_to_anchor=(1.0, 1.0))


def fig_types(ax):
    t = pd.DataFrame(R['types']).T
    tiers = dict(St.S4_TIERS, Bract=-1, Fdg=-1, Roundup=-1)
    lab = {2: 'tier 2\n(strongest)', 1: 'tier 1', 0: 'tier 0\n(no effect)', -1: 'downstream\n(no effect)'}
    for name, row in t.iterrows():
        x = {2: 0, 1: 1, 0: 2, -1: 3}[tiers[name]]
        ax.plot(x, row.fhat, 'o', color=CLS_COLOR.get(row.cls, NONE), ms=8, mec='white', mew=0.8)
        ax.annotate(name, (x, row.fhat), xytext=(7, -7 if name == 'Fdg' else (4 if name == 'Bract' else 0)), textcoords='offset points', va='center', fontsize=7, color=INK)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(range(4), [lab[k] for k in (2, 1, 0, -1)], fontsize=7); ax.set_xlim(-0.4, 3.9)
    s4 = R['S4']
    ax.set(ylabel='type-level f̂ (S_pure input)', title=f"External test: τ_b = {s4['tau_b']:.2f}, p = {s4['p']:.2f}")
    ax.grid(axis='x', visible=False)


def fig_classes(ax):
    cl = R['RQ2']['classes']; keys = ['shift', 'gain', 'other']
    ax.bar(keys, [cl[k] for k in keys], color=[CLS_COLOR[k] for k in keys], width=0.6)
    for i, k in enumerate(keys):
        ax.text(i, cl[k] + 0.6, str(cl[k]), ha='center', fontsize=8, color=INK)
    c = R['RQ2']['collapse']
    ax.set(ylabel='neurons', title=f"RQ2: classes of {c['n_eligible']} effect-bearing neurons\n"
           f"collapse fraction {c['est']:.2f} [{c['ci'][0]:.2f}, {c['ci'][1]:.2f}]; none = {cl['none']}")
    ax.grid(axis='x', visible=False)


PANELS = [('intact', fig_intact, (5, 3.4)), ('pa_scatter', fig_pa, (5, 4)), ('predictor_rho', fig_rho, (5, 4.6)),
          ('rq1_by_lambda', fig_rq1, (5, 3.4)), ('external_types', fig_types, (5, 3.8)), ('classes', fig_classes, (4, 3.2))]


def main():
    with PdfPages(os.path.join(FIG, 'overview.pdf')) as pdf:
        for name, fn, size in PANELS:
            fig, ax = plt.subplots(figsize=size); fn(ax)
            fig.savefig(os.path.join(FIG, f'fig_{name}.png')); pdf.savefig(fig); plt.close(fig)
        fig, axs = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True); fig_examples(axs)
        fig.suptitle('Example silencing curves (largest |f̂| per class)', y=1.03)
        fig.savefig(os.path.join(FIG, 'fig_examples.png')); pdf.savefig(fig); plt.close(fig)
    print('wrote', FIG)


if __name__ == '__main__':
    main()
