# Pre-touch N GB of RAM once so later timing benchmarks are not dominated by one-time first-touch cost of this VM (see logs/05_mem_touch_test.log)
import numpy as np, time, sys
n = int(sys.argv[1]); ch = []
t = time.perf_counter()
for k in range(n):
    ch.append(np.ones(128 * 1024 * 1024)); 
print(f'pre-touched {n} GB in {time.perf_counter()-t:.1f}s')
