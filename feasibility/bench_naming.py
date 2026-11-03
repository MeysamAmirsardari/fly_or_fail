# Diagnose the 42 s/trial vs 5 s/trial discrepancy. In ONE process run n consecutive trials of the unmodified model.run_trial and record, per trial:
# wall time, auto-generated Brian2 names of objects created by the trial (PoissonInput / binomial function / subgroup counters), and the number of
# Cython extensions in ~/.cython/brian_extensions (growth = fresh compilation). usage: bench_naming.py <ver> <rate> <n>
import sys, time, os, glob, copy, re
import simlib as S
from brian2 import Hz, Network, ms
import brian2, gc
ver, rate, n = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
p = copy.deepcopy(S.M.default_params); p['r_poi'] = rate * Hz
f2i = S.flyid2i_map(ver); exc = [f2i[i] for i in S.sugar_right(ver)]; pc, pn = S.PATHS[ver]
cache = os.path.expanduser('~/.cython/brian_extensions/')
nfiles = lambda: len(glob.glob(cache + '*.so'))
for k in range(n):
    n0 = nfiles(); t0 = time.perf_counter()
    neu, syn, mon = S.M.create_model(pc, pn, p)
    pois, neu = S.M.poi(neu, exc, [], p)
    net = Network(neu, syn, mon, *pois)
    nm = [o.name for o in pois][:3]; bn = [n for n in pois[-1].variables if 'binomial' in n]
    net.run(p['t_run'])
    spk = S.M.get_spk_trn(mon); w = time.perf_counter() - t0
    print(f'trial {k}: wall {w:.1f}s | first PoissonInput names {nm} | last PoissonInput binomial-function name {bn} | new cython .so compiled this trial: {nfiles()-n0} | n_active {len(spk)}', flush=True)
    del neu, syn, mon, pois, net, spk; gc.collect()
