# G0 (trajectory-level semantics check): run the ORIGINAL Brian2 model objects (model.create_model, unmodified: same
# NeuronGroup/equations/threshold/reset/refractory/Synapses/delay/weights, codegen target as default) but replace the
# random PoissonInput by a deterministic input that applies EXACTLY the same code as PoissonInput
# ('v += 68.75*mV * X' in the 'synapses' slot, order 0, conditional on not_refractory), where X(t) is the Bernoulli
# train fastlif generates for the same (trial seed, neuron). Then compare spike trains spike-for-spike with fastlif.
# usage: g0_brian2_exact.py <ver> <rate> <trial_seed> [silence_fid]
import sys, time, json
sys.path.insert(0, '/home/user/external/Drosophila_brain_model')
sys.path.insert(0, '/home/user/fly_or_fail/sim')
import numpy as np
import model as M
from brian2 import Network, TimedArray, defaultclock, ms, mV, Hz, prefs
import fastlif as F

ver, rate, trial = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
slnc_f = [int(sys.argv[4])] if len(sys.argv) > 4 and sys.argv[4] != '0' else []
p = dict(M.default_params); p['r_poi'] = rate * Hz
# constants identity check (fastlif float constants == Brian2 quantities)
assert float(p['v_th']) == F.V_TH and float(p['v_0']) == F.V_0 and float(p['w_syn']) == F.W_SYN, 'constant mismatch'
assert float(p['t_mbr']) == F.T_MBR and float(p['tau']) == F.TAU and float(defaultclock.dt) == F.DT
pc, pn = F.PATHS[ver]
full = F.load_full(ver)
stim = F.sugar_right(ver)
T = 10000
u = F.crn_uniforms([trial], stim, T)[0]
ev = (u < rate * F.DT)                       # (n_stim, T)
t0 = time.time()
for k in range(len(stim)):                   # TimedArrays must be resolvable in the NeuronGroup's own namespace
    p[f'ta_{k}'] = TimedArray(ev[k].astype(float), dt=defaultclock.dt, name=f'ta_{k}')
neu, syn, mon = M.create_model(pc, pn, p)
objs = []
for k, f in enumerate(stim):
    i = int(full.f2l[f])
    neu[i].rfc = 0 * ms                      # as model.poi
    op = neu[i:i + 1].run_regularly(f'v += 68.75*mV * ta_{k}(t)', when='synapses', order=0, name=f'inj_{k}')
    objs.append(op)
M.silence([int(full.f2l[f]) for f in slnc_f], syn)
net = Network(neu, syn, mon, *objs)
net.run(0 * ms)
co = objs[0].codeobj if hasattr(objs[0], 'codeobj') else None
print('injection abstract code:', objs[0].abstract_code.strip())
print(net.scheduling_summary())
net.run(1000 * ms)
wall_b = time.time() - t0
bi = np.asarray(mon.i[:], np.int64); bt = np.asarray(mon.t[:] / defaultclock.dt + 0.5).astype(np.int64)
# fastlif, same input (event at step s iff u < rate*dt), full network
t0 = time.time()
r = F.run(full, stim, [dict(rate=rate, trial=trial, silence=slnc_f)], trial_seeds=[trial], record='all', rec_cap=10**6,
          threads=1)
wall_f = time.time() - t0
fs, ff = r['spikes'][0]; fi = np.array([full.f2l[int(x)] for x in ff], np.int64)
A = set(zip(bt.tolist(), bi.tolist())); B = set(zip(fs.tolist(), fi.tolist()))
cb = np.bincount(bi, minlength=full.n); cf = r['counts'][0]
res = dict(ver=ver, rate=rate, trial=trial, silence=slnc_f, brian2_spikes=len(A), fastlif_spikes=len(B),
           common=len(A & B), only_brian2=len(A - B), only_fastlif=len(B - A),
           identical_spike_trains=(A == B), counts_identical=bool(np.array_equal(cb, cf)),
           n_active=int((cb > 0).sum()), mn9_l=int(cb[full.f2l[F.MN9_L]]), wall_brian2_s=round(wall_b, 1),
           wall_fastlif_s=round(wall_f, 2))
if A != B:
    d = sorted((A - B) | (B - A))[:10]; res['first_diffs'] = [list(x) for x in d]
print('G0RESULT', json.dumps(res))
