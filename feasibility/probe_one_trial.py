# One timed trial per version (fresh process) to see phase split & peak RSS; run the first trial twice to separate compile cost.
import sys, json
import simlib as S
from brian2 import Hz, ms
ver = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
rate = float(sys.argv[3]) if len(sys.argv) > 3 else None
p = dict(S.M.default_params)
if rate: p['r_poi'] = rate * Hz
print('version', ver, 'r_poi', p['r_poi'], 't_run', p['t_run'])
f2i = S.flyid2i_map(ver); exc = S.sugar_right(ver)
print('n sugar R used', len(exc))
for k in range(n):
    spk, t = S.timed_trial(exc, [], [], ver, p, f2i)
    print('trial', k, json.dumps({a: round(b, 2) for a, b in t.items()}), 'n_active', len(spk), 'n_spikes', sum(len(v) for v in spk.values()), flush=True)
