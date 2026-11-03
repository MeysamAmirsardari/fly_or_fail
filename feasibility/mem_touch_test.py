# Measure first-touch speed of fresh memory (VM may back guest RAM lazily): allocate+fill 1 GB chunks, then time re-fill of same chunks.
import numpy as np, time
chunks = []
for k in range(4):
    t = time.perf_counter(); a = np.ones(128 * 1024 * 1024, dtype=np.float64); dt = time.perf_counter() - t   # 1 GB
    chunks.append(a); print(f'chunk {k}: first touch 1GB {dt:.2f}s', flush=True)
t = time.perf_counter()
for a in chunks: a += 1
print(f'refill 4 GB (already touched): {time.perf_counter()-t:.2f}s')
