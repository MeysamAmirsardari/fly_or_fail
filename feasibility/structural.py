# Quick structural facts: hop distances sugar-GRN set -> MN9, k-hop downstream counts, and timing of one max-flow
# (node-disjoint paths via node splitting, unit node capacities) on path-restricted subgraphs. numpy/scipy/networkx only.
import sys, time, numpy as np, pandas as pd, scipy.sparse as sp, networkx as nx
from scipy.sparse.csgraph import breadth_first_order, shortest_path, maximum_flow
import simlib as S
ver = sys.argv[1]
comp = pd.read_csv(S.PATHS[ver][0], index_col=0); n = len(comp)
con = pd.read_parquet(S.PATHS[ver][1], columns=['Presynaptic_Index', 'Postsynaptic_Index', 'Connectivity', 'Excitatory'])
pre = con.Presynaptic_Index.values; post = con.Postsynaptic_Index.values
f2i = {j: i for i, j in enumerate(comp.index)}
src = [f2i[i] for i in S.sugar_right(ver)]
mn9 = {nm: f2i[i] for nm, i in [('MN9_L', S.MN9_L), ('MN9_R', S.MN9_R), ('MN9_partner_v783(...523)', 720575940618238523)] if i in f2i}
print(f'[{ver}] neurons {n} edges {len(con)} | sugar GRNs used {len(src)} | MN9 present: {list(mn9)}')

def A(mask=None):
    m = np.ones(len(pre), bool) if mask is None else mask
    return sp.csr_matrix((np.ones(m.sum(), np.int8), (pre[m], post[m])), shape=(n, n))
def hops(adj, seeds):
    """multi-source BFS hop distance (inf if unreachable)"""
    d = np.full(n, np.inf); d[seeds] = 0; frontier = np.array(seeds); k = 0; seen = np.zeros(n, bool); seen[seeds] = True
    while len(frontier):
        k += 1
        nxt = np.unique(adj[frontier].indices); nxt = nxt[~seen[nxt]]
        seen[nxt] = True; d[nxt] = k; frontier = nxt
    return d
res = {}
for label, mask in [('unsigned', None), ('excitatory-only', con.Excitatory.values > 0)]:
    t = time.perf_counter(); adj = A(mask); df = hops(adj, src); dt = time.perf_counter() - t
    print(f'--- {label}: BFS from sugar GRN set took {dt:.2f}s')
    for k in range(1, 7):
        cum = int(((df >= 1) & (df <= k)).sum()); ex = int((df == k).sum())
        print(f'   downstream hops <= {k}: {cum} neurons (excluding the {len(src)} seeds); exactly {k}: {ex}; frac of brain {cum/n:.3f}')
    for nm, i in mn9.items(): print(f'   hop distance sugar-set -> {nm}: {df[i]}')
    res[label] = (adj, df)
# max-flow timing on subgraphs restricted to nodes on some walk of length <= L (d_f + d_b <= L), unsigned graph
adj, df = res['unsigned']
for nm, tgt in mn9.items():
    db = hops(adj.T.tocsr(), [tgt])
    dmin = df[tgt]
    print(f'=== max-flow {nm}: shortest hop {dmin}')
    for L in [int(dmin), int(dmin) + 1, int(dmin) + 2]:
        keep = np.where(df + db <= L)[0]
        keep_set = np.zeros(n, bool); keep_set[keep] = True
        em = keep_set[pre] & keep_set[post]
        sub_pre, sub_post, w = pre[em], post[em], con.Connectivity.values[em]
        ids = {v: k for k, v in enumerate(keep)}; m = len(keep)
        # node-split graph for node-disjoint paths: v_in = 2k, v_out = 2k+1; S = 2m, T = 2m+1
        rows = [2 * ids[v] for v in keep]; cols = [2 * ids[v] + 1 for v in keep]; caps = [1] * m          # node capacity 1
        rows += [2 * ids[a] + 1 for a in sub_pre]; cols += [2 * ids[b] for b in sub_post]; caps += [m] * len(sub_pre)  # edges "infinite"
        caps[ids[tgt]] = m      # fix 2026-11-03: target node capacity must not be 1 (else flow value is trivially <= 1)
        S_, T_ = 2 * m, 2 * m + 1
        for s in src:
            if s in ids: rows.append(S_); cols.append(2 * ids[s]); caps.append(1)
        rows.append(2 * ids[tgt] + 1); cols.append(T_); caps.append(m)
        G = sp.csr_matrix((np.array(caps, dtype=np.int32), (rows, cols)), shape=(2 * m + 2, 2 * m + 2))
        t = time.perf_counter(); flow_sp = maximum_flow(G, S_, T_).flow_value; t_sp = time.perf_counter() - t
        # networkx version (same graph) for the timing record
        if len(sub_pre) < 300000:   # (fix 2026-11-03: python ints avoid numpy int32 overflow in networkx; skip networkx on very large subgraphs)
            Gx = nx.DiGraph(); co = G.tocoo(); Gx.add_weighted_edges_from(zip(co.row.tolist(), co.col.tolist(), co.data.tolist()), weight='capacity')
            t = time.perf_counter(); flow_nx = nx.maximum_flow_value(Gx, S_, T_); t_nx = time.perf_counter() - t
        else: flow_nx, t_nx = None, float('nan')
        print(f'   L={L}: subgraph nodes {m}, edges {len(sub_pre)}; node-disjoint paths: scipy={flow_sp} ({t_sp*1000:.1f} ms), networkx={flow_nx} ({t_nx*1000:.1f} ms)')
