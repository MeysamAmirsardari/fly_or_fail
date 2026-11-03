# Time the UNMODIFIED model.run_trial (as called by run_exp) in a fresh process, to compare with the phase-split version.
import time, sys
import simlib as S
ver = sys.argv[1]; n = int(sys.argv[2])
f2i = S.flyid2i_map(ver); exc = [f2i[i] for i in S.sugar_right(ver)]
pc, pn = S.PATHS[ver]
for k in range(n):
    t0 = time.perf_counter()
    spk = S.M.run_trial(exc, [], [], pc, pn, S.M.default_params)
    print('orig run_trial', k, 'wall s', round(time.perf_counter() - t0, 2), 'n_active', len(spk), 'n_spikes', sum(len(v) for v in spk.values()), 'peak_rss_mb', round(S.rss_mb()), flush=True)
