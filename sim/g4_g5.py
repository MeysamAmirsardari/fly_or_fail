# G4 (CRN sanity) and G5 (speed) for fastlif on the closure network.
# usage: g4_g5.py <ver> <threads>
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastlif as F, reduce as R

ver, threads = sys.argv[1], int(sys.argv[2])
full = F.load_full(ver); stim = F.sugar_right(ver)
net = R.load_closure(ver)
rng = np.random.default_rng(7)
act = np.flatnonzero(F.run(net, stim, [dict(rate=400, trial=0)], threads=threads)['counts'][0] > 0)
act_f = [int(net.fid[i]) for i in act]
out = {}
# ---------------- G4a: input trains depend only on (salt, trial, fid); independent of other neurons / batch / order
T = 10000
u1 = F.crn_uniforms([3, 5], stim, T)
u2 = F.crn_uniforms([5, 3], stim[::-1], T)                       # different order of trials and neurons
sub = stim[::2]
u3 = F.crn_uniforms([3], sub, T)                                  # recruitment-control style subset
out['G4a_trains_order_invariant'] = bool(np.array_equal(u1[0], u2[1][::-1]) and np.array_equal(u1[1], u2[0][::-1]))
out['G4a_trains_subset_invariant'] = bool(np.array_equal(u1[0][::2], u3[0]))
lam = [50, 100, 200, 400]
ev = [(u1 < r * F.DT) for r in lam]
out['G4a_nested_thinning'] = bool(all(np.all(ev[k] <= ev[k + 1]) for k in range(len(lam) - 1)))
out['G4a_event_rate_hz'] = {r: round(float(e.sum() / (e.shape[0] * e.shape[1]) / (T * F.DT)), 2) for r, e in zip(lam, ev)}
# ---------------- G4b: same seeds + conditions -> identical outputs, regardless of batch composition / order / threads
conds = [[]] + [[f] for f in rng.choice(act_f, 6, replace=False).tolist()]
jobs = [dict(rate=r, trial=t, silence=s) for s in conds for r in (100, 400) for t in (0, 1, 2)]
a = F.run(net, stim, jobs, trial_seeds=[0, 1, 2], record='all', rec_cap=60000, threads=threads)
perm = rng.permutation(len(jobs))
b = F.run(net, stim, [jobs[i] for i in perm], trial_seeds=[2, 0, 1], record='all', rec_cap=60000, threads=1)
same = np.array_equal(a['counts'][perm], b['counts']) and all(
    np.array_equal(a['spikes'][perm[k]][0], b['spikes'][k][0]) and np.array_equal(a['spikes'][perm[k]][1], b['spikes'][k][1])
    for k in range(len(jobs)))
out['G4b_repeat_identical_across_order_threads'] = bool(same)
# ---------------- G4c: realized GRN input events identical across conditions within a trial
# (record GRN spikes: a GRN spikes one step after each input event unless the event falls in its spike step)
st = F.run(net, stim, [dict(rate=100, trial=0, silence=s) for s in conds], trial_seeds=[0], record=stim, rec_cap=100000,
           threads=threads)
grn_same = all(np.array_equal(st['spikes'][0][0], st['spikes'][k][0]) and np.array_equal(st['spikes'][0][1], st['spikes'][k][1])
               for k in range(len(conds)))
gl = net.loc(stim)
# incoming synapses onto GRNs within the closure
inc = np.isin(net.post, gl).sum()
out['G4c_grn_spike_trains_identical_across_conditions'] = bool(grn_same)
out['G4c_synapses_onto_stimulated_grns_in_closure'] = int(inc)
print('G4RESULT', json.dumps(out), flush=True)

# ---------------- G5: amortized wall time per 1-s trial per condition
g5 = dict(threads=threads, closure_neurons=net.n, closure_synapses=net.nsyn())
for rate in (100, 400):
    sil = rng.choice(act_f, 64, replace=False).tolist()
    jb = [dict(rate=rate, trial=t, silence=[f]) for f in sil for t in range(8)]   # 512 jobs
    t0 = time.time(); r = F.run(net, stim, jb, trial_seeds=list(range(8)), threads=threads); w = time.time() - t0
    g5[f'closure_{rate}Hz_s_per_job'] = round(w / len(jb), 4)
    g5[f'closure_{rate}Hz_jobs'] = len(jb)
    g5[f'closure_{rate}Hz_violations'] = int((r['nviol'] > 0).sum())
jb = [dict(rate=200, trial=t) for t in range(2 * threads)]
t0 = time.time(); F.run(full, stim, jb, trial_seeds=list(range(2 * threads)), threads=threads)
g5['fullnet_200Hz_s_per_job'] = round((time.time() - t0) / len(jb), 3)
worst = max(g5['closure_100Hz_s_per_job'], g5['closure_400Hz_s_per_job'])
g5['projected_3200x8_min'] = round(3200 * 8 * worst / 60, 1)
g5['projected_480x8_min'] = round(480 * 8 * worst / 60, 1)
print('G5RESULT', json.dumps(g5), flush=True)
