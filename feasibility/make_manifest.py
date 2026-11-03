# Manifest of the Brian2 reference dataset (out/ref/<ver>/<exp>.parquet): conditions, trials, seeds, rows, sha256. Written to out/ref/MANIFEST.csv
import glob, json, hashlib, os, pandas as pd
rows = []
for m in sorted(glob.glob('out/ref/v*/*.meta.json')):
    d = json.load(open(m)); f = m.replace('.meta.json', '.parquet')
    rows.append(dict(version=d['version'], exp_name=d['exp_name'], rate_hz=d['rate_hz'], n_trials=d['n_trials'], silenced_ids=';'.join(map(str, d['silenced_ids'])),
                     n_input_grns=len(d['sugar_grn_ids']), seed_first=d['seeds'][0], seed_last=d['seeds'][-1], n_spike_rows=d['n_spike_rows'],
                     file=f, bytes=os.path.getsize(f), sha256=hashlib.sha256(open(f, 'rb').read()).hexdigest(), finished=d['finished']))
pd.DataFrame(rows).to_csv('out/ref/MANIFEST.csv', index=False); print(pd.DataFrame(rows).drop(columns=['file', 'sha256', 'finished']).to_string())
