# Baseline reproduction using the authors' UNMODIFIED model.run_exp (n_proc=1). Outputs spikes to feasibility/out/<ver>/.
# usage: repro_run.py <ver> <name> <rate_hz> <n_trials> [silence_id]
import sys, copy, time
import simlib as S
from brian2 import Hz
ver, name, rate, ntr = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
slnc = [int(sys.argv[5])] if len(sys.argv) > 5 else []
p = copy.deepcopy(S.M.default_params); p['r_poi'] = rate * Hz; p['n_run'] = ntr
import os; os.makedirs(f'/home/user/fly_or_fail/feasibility/out/{ver}', exist_ok=True)
exc = S.sugar_right(ver)      # drops the sugar GRN(s) not present in the version (else run_exp raises KeyError)
print('ver', ver, 'exp', name, 'rate', rate, 'n_trials', ntr, 'n_exc', len(exc), 'silence', slnc, flush=True)
pc, pn = S.PATHS[ver]
t0 = time.time()
S.M.run_exp(exp_name=name, neu_exc=exc, neu_slnc=slnc, params=p, path_res=f'/home/user/fly_or_fail/feasibility/out/{ver}',
            path_comp=pc, path_con=pn, n_proc=1, force_overwrite=True)
print('total wall s', round(time.time() - t0, 1), 'peak_rss_mb', round(S.rss_mb()))
