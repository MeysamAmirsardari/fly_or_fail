# ACTIVE SET and coarse I/O curve from the reference runs (out/ref/<ver>/sugarR_<λ>Hz.parquet).
import numpy as np, pandas as pd, glob, os, re, json
from scipy import stats
import simlib as S
MN9 = {'v630': {'MN9_L(...265)': S.MN9_L, 'MN9_R(...262)': S.MN9_R},
       'v783': {'MN9_L(...265)': 720575940660219265, 'MN9_partner(...523)': 720575940618238523}}
out = []
for ver in ['v630', 'v783']:
    GRN = set(S.sugar_right(ver)); n_neur = len(pd.read_csv(S.PATHS[ver][0], index_col=0))
    print(f'\n######## {ver} (neurons {n_neur}, driven sugar GRNs {len(GRN)})')
    files = sorted(glob.glob(f'out/ref/{ver}/sugarR_*Hz.parquet'), key=lambda f: float(re.search(r'_(\d+)Hz', f).group(1)))
    for f in files:
        lam = float(re.search(r'_(\d+)Hz', f).group(1)); meta = json.load(open(f.replace('.parquet', '.meta.json'))); ntr = meta['n_trials']
        df = pd.read_parquet(f)
        ct = pd.crosstab(df.flywire_id, df.trial).reindex(columns=range(ntr), fill_value=0)
        rate = ct.mean(1)   # t_run = 1 s -> Hz
        row = dict(ver=ver, lam=lam, n_trials=ntr, n_ge1spike=int((ct.sum(1) > 0).sum()), n_ge1Hz=int((rate >= 1).sum()),
                   n_ge1spike_first10=int((ct.iloc[:, :10].sum(1) > 0).sum()), n_ge1Hz_first10=int((ct.iloc[:, :10].mean(1) >= 1).sum()),
                   n_ge1Hz_excl_GRN=int((rate.drop(index=[i for i in GRN if i in rate.index]) >= 1).sum()),
                   spikes_per_trial=len(df) / ntr, grn_mean_rate=float(rate.reindex(list(GRN)).fillna(0).mean()))
        for nm, mid in MN9[ver].items():
            x = ct.loc[mid].values.astype(float) if mid in ct.index else np.zeros(ntr)
            m = x.mean(); ci = stats.t.ppf(0.975, ntr - 1) * x.std(ddof=1) / np.sqrt(ntr)
            row[nm] = m; row[nm + '_lo'] = m - ci; row[nm + '_hi'] = m + ci; row[nm + '_ntr_spiking'] = int((x > 0).sum())
        out.append(row)
        s = ' | '.join(f'{nm} {row[nm]:.2f} [{row[nm+"_lo"]:.2f},{row[nm+"_hi"]:.2f}] ({row[nm+"_ntr_spiking"]}/{ntr} trials >0)' for nm in MN9[ver])
        print(f'λ={lam:5.0f} Hz n_trials={ntr:2d} | neurons >=1 spike: {row["n_ge1spike"]} (first 10 trials: {row["n_ge1spike_first10"]}) | >=1 Hz: {row["n_ge1Hz"]} (first 10: {row["n_ge1Hz_first10"]}; excl. driven GRNs: {row["n_ge1Hz_excl_GRN"]}) | spikes/trial {row["spikes_per_trial"]:.0f} | GRN mean {row["grn_mean_rate"]:.1f} Hz | {s}')
R = pd.DataFrame(out); os.makedirs('out/ref/analysis', exist_ok=True); R.to_csv('out/ref/analysis/active_io_summary.csv', index=False)
print('\nwrote out/ref/analysis/active_io_summary.csv')
