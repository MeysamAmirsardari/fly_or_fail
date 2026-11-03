# Brian2 REFERENCE DATASET runner. Uses the authors' UNMODIFIED model.run_trial (create_model + poi + silence + Network.run
# per trial, exactly as model.run_exp does it), in one persistent process, with brian2.seed(seed) set before each trial.
# usage: ref_run.py <ver> <exp_name> <rate_hz> <n_trials> <silence_id|0> [seed_offset=0] [max_new_trials=all]
# (production uses max_new_trials=1, i.e. a FRESH PROCESS PER TRIAL, because Brian2 auto-names advance within a process and force re-compilation; see report)
# Output: out/ref/<ver>/<exp>.parquet (t, trial, flywire_id, exp_name; brotli, as in model.run_exp) + <exp>.meta.json
# Per-trial shards in out/ref/<ver>/_shards/<exp>/trial_XX.parquet allow resume. Trial t uses Brian2 seed = seed_offset + t.
import sys, os, json, time, gc, copy
import simlib as S
import numpy as np, pandas as pd, psutil, brian2
from brian2 import Hz
ver, name, rate, ntr, slid = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
seed_off = int(sys.argv[6]) if len(sys.argv) > 6 else 0
max_new = int(sys.argv[7]) if len(sys.argv) > 7 else 10**9; n_new = 0
root = f'/home/user/fly_or_fail/feasibility/out/ref/{ver}'
shard_dir = f'{root}/_shards/{name}'; os.makedirs(shard_dir, exist_ok=True)
p = copy.deepcopy(S.M.default_params); p['r_poi'] = rate * Hz
f2i = S.flyid2i_map(ver); i2f = {v: k for k, v in f2i.items()}
exc_ids = S.sugar_right(ver); exc = [f2i[i] for i in exc_ids]
slnc = [f2i[slid]] if slid else []
pc, pn = S.PATHS[ver]
print(f'ver {ver} exp {name} rate {rate} n_trials {ntr} n_exc {len(exc)} silence {slid or None} seed_off {seed_off}', flush=True)
proc = psutil.Process(); meta_tr = []
for t in range(ntr):
    sf = f'{shard_dir}/trial_{t:02d}.parquet'; mf = f'{shard_dir}/trial_{t:02d}.json'
    if os.path.exists(sf) and os.path.exists(mf):
        meta_tr.append(json.load(open(mf))); print('trial', t, 'resumed from shard', flush=True); continue
    if n_new >= max_new: break
    n_new += 1
    seed = seed_off + t
    brian2.seed(seed)
    t0 = time.perf_counter()
    spk = S.M.run_trial(exc, [], slnc, pc, pn, p)          # ORIGINAL code path
    wall = time.perf_counter() - t0
    df = S.M.construct_dataframe([spk], name, i2f); df['trial'] = t
    df.to_parquet(sf, compression='brotli')
    m = dict(trial=t, seed=seed, wall_s=round(wall, 2), n_active=len(spk), n_spikes=int(sum(len(v) for v in spk.values())),
             rss_mb=round(proc.memory_info().rss / 2**20), peak_rss_mb=round(S.rss_mb()))
    json.dump(m, open(mf, 'w')); meta_tr.append(m); print('trial', json.dumps(m), flush=True)
    del spk, df; gc.collect()
if len(meta_tr) < ntr:
    print('not all trials done yet:', len(meta_tr), '/', ntr, flush=True); sys.exit(0)
df = pd.concat([pd.read_parquet(f'{shard_dir}/trial_{t:02d}.parquet') for t in range(ntr)], ignore_index=True)
df['t'] = df['t'].astype(float)
out = f'{root}/{name}.parquet'; df.to_parquet(out, compression='brotli')
import importlib.metadata as im
meta = dict(version=ver, exp_name=name, rate_hz=rate, n_trials=ntr, sugar_grn_ids=exc_ids, silenced_ids=[slid] if slid else [],
            seed_rule='brian2.seed(seed_offset + trial) immediately before each run_trial', seed_offset=seed_off,
            seeds=[m['seed'] for m in meta_tr], params={k: str(v) for k, v in p.items() if k != 'eqs'},
            model_repo_head=os.popen('git -C /home/user/external/Drosophila_brain_model rev-parse HEAD').read().strip(),
            brian2=im.version('brian2'), numpy=im.version('numpy'), python=sys.version.split()[0],
            trials=meta_tr, n_spike_rows=len(df), finished=time.strftime('%Y-%m-%d %H:%M:%S'))
json.dump(meta, open(f'{root}/{name}.meta.json', 'w'), indent=1)
print('WROTE', out, 'rows', len(df), 'mean wall/trial', round(np.mean([m['wall_s'] for m in meta_tr]), 2), flush=True)
