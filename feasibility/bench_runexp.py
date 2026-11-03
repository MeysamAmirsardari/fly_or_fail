# Benchmark: authors' UNMODIFIED model.run_exp (n_proc=1, as used in repro_run.py) for n trials in a fresh process, writing to scratch.
# usage: bench_runexp.py <ver> <rate> <n> <outdir> [silence_id]
import sys, copy, time, os
import simlib as S
from brian2 import Hz
ver, rate, n, outd = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
slnc = [int(sys.argv[5])] if len(sys.argv) > 5 else []
os.makedirs(outd, exist_ok=True)
p = copy.deepcopy(S.M.default_params); p['r_poi'] = rate * Hz; p['n_run'] = n
pc, pn = S.PATHS[ver]; t0 = time.time()
S.M.run_exp(exp_name='bench', neu_exc=S.sugar_right(ver), neu_slnc=slnc, params=p, path_res=outd, path_comp=pc, path_con=pn, n_proc=1, force_overwrite=True)
print('total wall s', round(time.time() - t0, 1), 'per trial', round((time.time() - t0) / n, 1), 'peak_rss_mb', round(S.rss_mb()))
