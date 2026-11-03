# Inspect the authors' stored results in results/example/*.parquet
import glob, os, pandas as pd, numpy as np
import simlib as S
U = S.U
for p in sorted(glob.glob(S.D + 'results/example/*.parquet')):
    df = U.load_exps([p])
    name = os.path.basename(p)
    ntr = df.trial.nunique()
    print('=====', name, 'rows(spikes)', len(df), 'trials in file', ntr, 'trial ids', sorted(df.trial.unique())[:3], '...', df.trial.max(),
          'neurons spiking', df.flywire_id.nunique(), 'spikes/trial', round(len(df) / 30, 1), 't range', df.t.min(), df.t.max(), 'dtypes', dict(df.dtypes.astype(str)))
    r, s = U.get_rate(df, t_run=1.0, n_run=30)
    col = r.columns[0]
    print('  neurons with mean rate >=1Hz:', int((r[col] >= 1).sum()), ' >0:', int((r[col] > 0).sum()))
    print('  MN9_L rate', r[col].get(S.MN9_L, 0), 'std', s[col].get(S.MN9_L, 0), ' MN9_R rate', r[col].get(S.MN9_R, 0))
    sg = S.ids('sugar_GRN_right.csv')
    print('  sugar GRN mean rate (21):', r[col].reindex(sg).fillna(0).round(1).tolist())
