# Extra Brian2 reference trials via the authors' UNMODIFIED model.run_trial (same code path as model.run_exp),
# brian2.seed(seed) before each trial. Seeds disjoint from ENG's (0..19). Output: sim/out/brian2_extra/<ver>_<rate>Hz.parquet
# usage: brian2_extra.py <ver> <rate> <seed0> <n>
import sys, os, copy, time
sys.path.insert(0, '/home/user/fly_or_fail/feasibility')
import simlib as S, brian2, pandas as pd
from brian2 import Hz
ver, rate, s0, n = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
p = copy.deepcopy(S.M.default_params); p['r_poi'] = rate * Hz
f2i = S.flyid2i_map(ver); i2f = {v: k for k, v in f2i.items()}
exc = [f2i[i] for i in S.sugar_right(ver)]; pc, pn = S.PATHS[ver]
od = '/home/user/fly_or_fail/sim/out/brian2_extra'; os.makedirs(od, exist_ok=True)
sd = f'{od}/_shards_{ver}_{rate:g}Hz'; os.makedirs(sd, exist_ok=True)
for t in range(n):                      # per-trial shards (resume-safe; a killed process loses at most one trial)
    sf = f'{sd}/trial_{t:03d}.parquet'
    if os.path.exists(sf): continue
    brian2.seed(s0 + t); t0 = time.time()
    spk = S.M.run_trial(exc, [], [], pc, pn, p)
    d = S.M.construct_dataframe([spk], f'{ver}_{rate:g}Hz', i2f); d['trial'] = t
    d.to_parquet(sf + '.tmp.parquet'); os.replace(sf + '.tmp.parquet', sf)
    print('trial', t, 'seed', s0 + t, 'wall', round(time.time() - t0, 1), flush=True)
pd.concat([pd.read_parquet(f'{sd}/trial_{t:03d}.parquet') for t in range(n)], ignore_index=True).to_parquet(
    f'{od}/{ver}_{rate:g}Hz.parquet')
print('DONE', ver, rate)
