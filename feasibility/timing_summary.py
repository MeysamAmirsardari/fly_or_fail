# Per-trial timing from the shard metadata of the reference runs. wall_s = time inside model.run_trial (create_model + poi + silence + run).
# 'process_gap_s' = mtime difference between consecutive trial shards of the same job = full cost of one trial incl. python/brian2 start-up
# (fresh-process runs only). Persistent-process shards (v630 sugarR_100Hz/sugarR_200Hz trials 0-13, from the aborted first attempt) are tagged.
import glob, json, os, numpy as np
rows = []
for d in sorted(glob.glob('out/ref/v*/_shards/*')):
    if '/_' in d.split('_shards/')[1][:1]: continue
    ver = d.split('/')[2]; exp = d.split('/')[-1]
    js = sorted(glob.glob(d + '/trial_*.json')); M = [json.load(open(j)) for j in js]; mt = [os.path.getmtime(j) for j in js]
    w = np.array([m['wall_s'] for m in M]); gaps = np.diff(mt)
    persist = (ver == 'v630' and exp in ('sugarR_100Hz', 'sugarR_200Hz'))
    fresh_idx = [i for i in range(len(M)) if not (persist and i <= 13)]
    wf = w[fresh_idx]
    print(f'{ver} {exp:42s} n={len(M):2d} run_trial wall_s: fresh-process trials n={len(wf):2d} median {np.median(wf):5.2f} mean {wf.mean():5.2f} max {wf.max():5.2f}' +
          (f' | persistent-process trials 0-13: median {np.median(w[:14]):.2f}, trials 0-9 mean {w[:10].mean():.2f}, trials 10-13 mean {w[10:14].mean():.2f}' if persist else '') +
          f' | trial0 {w[0]:.1f}')
    if not persist: rows.append((w[1:] if len(w) > 1 else w, gaps))
allw = np.concatenate([r[0] for r in rows]); allg = np.concatenate([r[1] for r in rows])
print(f'\nALL fresh-process jobs (excluding trial 0 of each job): run_trial wall_s n={len(allw)} median {np.median(allw):.2f} mean {allw.mean():.2f} p95 {np.percentile(allw,95):.2f}')
print(f'inter-shard gap (full per-trial cost incl. interpreter start-up, 2 concurrent workers): n={len(allg)} median {np.median(allg):.2f} mean {allg.mean():.2f} p95 {np.percentile(allg,95):.2f}')
pk = [json.load(open(j))['peak_rss_mb'] for j in glob.glob('out/ref/v*/_shards/*/trial_*.json')]
print('peak RSS (ru_maxrss) per process, MB: max', max(pk), 'median', int(np.median(pk)))

# --- Uncontended window: only trials whose shard finished before 01:49:00 UTC on 2026-11-03 (other agents' Brian2 jobs were first seen running from 01:49, see logs/ref/06_machine_load_snapshot.log
# and the load average 8.5 at 02:12/02:19). Later trials ran on an oversubscribed 4-core VM and are NOT used for cost estimates.
import calendar, time
cut = calendar.timegm(time.strptime('2026-11-03 01:49:00', '%Y-%m-%d %H:%M:%S'))
cw, cg = [], []
for d in sorted(glob.glob('out/ref/v*/_shards/*')):
    ver = d.split('/')[2]; exp = d.split('/')[-1]
    if exp.startswith('_') or exp.endswith('rep2'): continue
    if ver == 'v630' and exp in ('sugarR_100Hz', 'sugarR_200Hz'): lo = 14      # first 14 trials came from the persistent-process attempt
    else: lo = 1
    js = sorted(glob.glob(d + '/trial_*.json')); mt = [os.path.getmtime(j) for j in js]
    for i in range(max(lo, 1), len(js)):
        if mt[i] < cut:
            cw.append(json.load(open(js[i]))['wall_s']); cg.append(mt[i] - mt[i - 1])
cw, cg = np.array(cw), np.array(cg)
print(f"\nUNCONTENDED window (<01:49, fresh-process trials, trial 0 of each job excluded; n={len(cw)}): run_trial wall_s median {np.median(cw):.2f} mean {cw.mean():.2f} p95 {np.percentile(cw,95):.2f} | full per-trial cost incl. interpreter start-up (inter-shard gap, 2 concurrent workers) median {np.median(cg):.2f} mean {cg.mean():.2f} p95 {np.percentile(cg,95):.2f}")
