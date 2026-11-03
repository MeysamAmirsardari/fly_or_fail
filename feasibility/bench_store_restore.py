# Benchmark/validation of "build once, store()/restore()" in ONE process (model code not modified; uses model.create_model / poi / silence / get_spk_trn).
# Checks (i) per-trial cost without re-building, (ii) that spike trains are IDENTICAL to the reference shards (fresh-process run_trial with the same Brian2 seed).
# usage: bench_store_restore.py <ver> <rate> <n> <ref_exp_name>
import sys, time, copy, gc
import simlib as S
import numpy as np, pandas as pd, brian2
from brian2 import Hz, Network
ver, rate, n, ref = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
p = copy.deepcopy(S.M.default_params); p['r_poi'] = rate * Hz
f2i = S.flyid2i_map(ver); i2f = {v: k for k, v in f2i.items()}; exc = [f2i[i] for i in S.sugar_right(ver)]; pc, pn = S.PATHS[ver]
t0 = time.perf_counter()
neu, syn, mon = S.M.create_model(pc, pn, p); pois, neu = S.M.poi(neu, exc, [], p); net = Network(neu, syn, mon, *pois)
net.run(0 * brian2.ms); net.store('init')
print(f'build+prepare once: {time.perf_counter()-t0:.1f} s', flush=True)
same = []
for k in range(n):
    t0 = time.perf_counter(); net.restore('init'); brian2.seed(k); t1 = time.perf_counter()
    net.run(p['t_run']); spk = S.M.get_spk_trn(mon); w = time.perf_counter() - t0
    df = S.M.construct_dataframe([spk], ref, i2f); df['trial'] = k
    r = pd.read_parquet(f'out/ref/{ver}/_shards/{ref}/trial_{k:02d}.parquet')
    a = df.drop(columns='exp_name').sort_values(['flywire_id', 't']).reset_index(drop=True); b = r.drop(columns='exp_name').sort_values(['flywire_id', 't']).reset_index(drop=True)
    eq = a.equals(b); same.append(eq)
    print(f'trial {k}: restore+run {w:.2f} s (restore {t1-t0:.2f} s) | n_spikes {len(df)} vs reference shard {len(r)} | identical to reference: {eq}', flush=True)
print('ALL identical to fresh-process reference:', all(same), '| peak RSS MB', round(S.rss_mb()))
