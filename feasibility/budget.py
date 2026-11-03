# Compute budget for the MVP blocks of PROJECT_DESIGN §4, recomputed from MEASURED per-trial costs (inputs read from logs/ref/04_trial_timing.log numbers passed as args).
# usage: budget.py <s_per_trial_fresh_process> <s_per_trial_run_trial_only> [s_per_trial_store_restore]
import sys
a = float(sys.argv[1]); b = float(sys.argv[2]); c = float(sys.argv[3]) if len(sys.argv) > 3 else None
blocks = [('Intact curve O(lambda): 25 lambda x 30 trials', 25 * 30), ('Single-neuron curves: ~400 neurons x 8 lambda x 8 trials', 400 * 8 * 8),
          ('Pair pilot: 60 pairs x 8 lambda x 8 trials', 60 * 8 * 8), ('Robustness: ~1,500 conditions x 8 trials (design: 60-neuron subset)', 1500 * 8)]
tot = sum(n for _, n in blocks)
hdr = f'{"block":70s} {"trials":>7s} {"CPU-h @%.1fs"%a:>14s} {"CPU-h @%.1fs"%b:>14s}' + (f' {"CPU-h @%.1fs"%c:>14s}' if c else '')
print(hdr)
for nm, n in blocks: print(f'{nm:70s} {n:7d} {n*a/3600:14.1f} {n*b/3600:14.1f}' + (f' {n*c/3600:14.1f}' if c else ''))
print(f'{"TOTAL":70s} {tot:7d} {tot*a/3600:14.1f} {tot*b/3600:14.1f}' + (f' {tot*c/3600:14.1f}' if c else ''))
for w in (2, 3, 4):
    print(f'wall-clock with {w} workers: {tot*a/3600/w:.1f} h @{a}s, {tot*b/3600/w:.1f} h @{b}s' + (f', {tot*c/3600/w:.1f} h @{c}s' if c else ''))
print(f'throughput per worker: {3600/a:.0f} trials/h @{a}s; {3600/b:.0f} @{b}s' + (f'; {3600/c:.0f} @{c}s' if c else ''))
