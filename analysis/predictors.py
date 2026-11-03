"""predictors: STRUCTURAL PREDICTOR pipeline (STRUCT) for PROJECT_DESIGN v1.0 §6.4.

RULE: no perturbation (silencing) simulation outcome is used anywhere. Inputs are the connectome and INTACT fastlif
simulations only (analysis/intact.py).

Conventions
-----------
* Edge lists are (pre -> post). Matrices used for linear algebra are indexed [post, pre]  (W_ij: i post, j pre),
  exactly as in the model (g_i += W_ij on a spike of j).
* "Silencing k" = removing k's OUTGOING edges (model.py semantics). For max-flow and cut statistics this equals removing
  k's in- and out-edges for every k not in T; for k in T it leaves the readout intact (f_T = 0, design §8 control).
* S (input set) nodes are exogenous sources in every linear model: their rows (incoming edges) are set to zero and the
  stimulus enters as u_S (unit for f^LIN-S, measured GRN rates for f^LIN-A).

Main entry: python predictors.py <ver>     (writes analysis/out/predictors_<ver>.parquet + json summaries)
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '2')
import sys, json, time, itertools
import numpy as np, pandas as pd
import scipy.sparse as sp
import scipy.linalg as sla
from scipy.sparse.csgraph import maximum_flow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

TAU_S = 0.005          # s
W_SYN = 0.275          # mV per synapse
WALK_L = 5             # walk-length bound and corridor bound
LIN_ALPHA_FRAC = 0.9   # alpha = 0.9 / rho(W_hat)
RICH_CLUB_DEG = 37     # Lin et al. 2024 reported (UNVERIFIED) rich-club regime: total degree > 37
BETW_K = 1000          # sampled sources per replicate (10 batches of 100)
BETW_SEEDS = (20261103, 20261104)
INF_CAP = None         # set per graph


# =====================================================================================================================
# generic graph utilities
# =====================================================================================================================
def csr_out(n, pre, post, data=None, dtype=np.int64):
    """Adjacency M[u, v] = data (default 1) for edge u -> v."""
    d = np.ones(len(pre), dtype) if data is None else np.asarray(data, dtype)
    return sp.csr_matrix((d, (pre, post)), shape=(n, n))


def bfs_dist(adj_csr, seeds):
    """Multi-source BFS hop distance along adj_csr rows (u -> v for M[u, v] != 0). inf if unreachable."""
    n = adj_csr.shape[0]
    d = np.full(n, np.inf); seeds = np.asarray(seeds, np.int64)
    if len(seeds) == 0: return d
    d[seeds] = 0; seen = np.zeros(n, bool); seen[seeds] = True; fr = np.unique(seeds); k = 0
    indptr, ind = adj_csr.indptr, adj_csr.indices
    while len(fr):
        k += 1
        nb = np.unique(np.concatenate([ind[indptr[u]:indptr[u + 1]] for u in fr])) if len(fr) else np.zeros(0, np.int64)
        nb = nb[~seen[nb]]
        seen[nb] = True; d[nb] = k; fr = nb
    return d


def reachable(adj_csr, seeds, blocked=None):
    """boolean reachability from seeds along adj_csr rows; blocked nodes are never entered (nor expanded)."""
    n = adj_csr.shape[0]; seen = np.zeros(n, bool)
    if blocked is not None: seen[blocked] = True                      # treat as already visited (never expanded)
    fr = np.unique(np.asarray(seeds, np.int64)); fr = fr[~seen[fr]]; seen[fr] = True
    out = np.zeros(n, bool); out[fr] = True
    indptr, ind = adj_csr.indptr, adj_csr.indices
    while len(fr):
        nb = np.unique(np.concatenate([ind[indptr[u]:indptr[u + 1]] for u in fr]))
        nb = nb[~seen[nb]]; seen[nb] = True; out[nb] = True; fr = nb
    return out


def cut_nodes_by_path(adj_csr, S, T):
    """Single-vertex S->T cuts (T excluded) by direct reachability: every cut lies on EVERY S->T path, hence on one
    fixed shortest path P; each node of P (except T) is tested by BFS with that node removed. Exact; independent of
    both the dominator-tree and the max-flow computations."""
    S = np.asarray(S, np.int64); T = int(np.atleast_1d(T)[0])
    n = adj_csr.shape[0]
    par = -np.ones(n, np.int64); seen = np.zeros(n, bool); seen[S] = True; fr = np.unique(S)
    indptr, ind = adj_csr.indptr, adj_csr.indices
    while len(fr) and not seen[T]:
        nxt = []
        for u in fr:
            for v in ind[indptr[u]:indptr[u + 1]]:
                if not seen[v]: seen[v] = True; par[v] = u; nxt.append(v)
        fr = np.array(nxt, np.int64)
    if not seen[T]: return None
    path = []; v = par[T]
    while v >= 0: path.append(int(v)); v = par[v]
    return sorted(k for k in path if not reachable(adj_csr, S[S != k], blocked=[k])[T])


# =====================================================================================================================
# L1: walk counts through k
# =====================================================================================================================
def walk_counts_through(M, S, T, L, d_S=None, d_T=None, MT=None):
    """Exact counts of S->T WALKS of length 1..L (edges may repeat; multiplicity = #(start in S, end in T, sequence)).
    M: csr adjacency (int64) M[u, v] = 1 for u -> v (unweighted, unsigned).
    Returns (through, visits, total):
      visits[k]  = sum over walks of the number of times the walk is at k (positions 0..len)
                 = sum_{i+j<=L, i+j>=1} N_i(k) B_j(k),  N_i = #walks S->k of length i, B_j = #walks k->T of length j
      through[k] = number of walks visiting k AT LEAST ONCE = sum_i F_i(k) sum_{j<=L-i} B_j(k), with F the first-passage
                   counts from the renewal identity N_i = sum_m F_m C_{i-m}, C_t(k) = #closed walks k->k of length t.
      total      = number of S->T walks of length <= L (requires S and T disjoint)."""
    n = M.shape[0]
    S = np.asarray(S, np.int64); T = np.asarray(T, np.int64)
    assert len(np.intersect1d(S, T)) == 0
    MT = M.T.tocsr() if MT is None else MT
    N = np.zeros((L + 1, n), np.int64); B = np.zeros((L + 1, n), np.int64)
    v = np.zeros(n, np.int64); np.add.at(v, S, 1); N[0] = v
    for i in range(1, L + 1): N[i] = MT @ N[i - 1]
    v = np.zeros(n, np.int64); np.add.at(v, T, 1); B[0] = v
    for j in range(1, L + 1): B[j] = M @ B[j - 1]
    cumB = np.cumsum(B, 0)                               # cumB[j] = sum_{j'<=j} B_j'
    total = int(N[1:, T].sum())                          # walks ending in T of length 1..L
    visits = np.zeros(n, np.int64)
    for i in range(0, L + 1):
        jmax = L - i
        lo = 1 if i == 0 else 0                          # exclude the empty walk (length 0)
        if jmax >= lo:
            visits += N[i] * (cumB[jmax] - (cumB[lo - 1] if lo > 0 else 0))
    # closed-walk counts C_t(k) needed only for t <= L - dS(k) - dT(k)
    if d_S is None: d_S = np.full(n, np.inf); d_S[(N > 0).any(0)] = np.argmax(N > 0, 0)[(N > 0).any(0)]
    if d_T is None: d_T = np.full(n, np.inf); d_T[(B > 0).any(0)] = np.argmax(B > 0, 0)[(B > 0).any(0)]
    slack = L - d_S - d_T
    rel = np.flatnonzero(np.isfinite(slack) & (slack >= 0))
    through = np.zeros(n, np.int64)
    Csm = closed_walk_counts(M, rel, np.minimum(slack[rel], L).astype(int))
    for a, k in enumerate(rel):
        Ck = Csm[a]                                       # Ck[t], t = 0..tmax(k); C0 = 1
        F = np.zeros(L + 1, np.int64)
        for i in range(L + 1):
            s = N[i, k]
            for m in range(i):
                t = i - m
                if t < len(Ck) and F[m]: s -= F[m] * Ck[t]
            F[i] = s
        tot = 0
        for i in range(L + 1):
            if F[i] == 0: continue
            jmax = L - i; lo = 1 if i == 0 else 0
            if jmax >= lo:
                tot += F[i] * (cumB[jmax, k] - (cumB[lo - 1, k] if lo > 0 else 0))
        through[k] = tot
    return through, visits, total


def closed_walk_counts(M, nodes, tmax):
    """C[a][t] = (M^t)_{kk} for k = nodes[a], t = 0..tmax[a] (exact int64). Uses sparse frontier vectors."""
    out = []
    Mcsc = M.tocsc()
    for k, tm in zip(nodes, tmax):
        Ck = np.zeros(max(int(tm), 0) + 1, np.int64); Ck[0] = 1
        if tm >= 1:
            vec = sp.csr_matrix(M[k], dtype=np.int64)     # walks of length 1 from k (int64: no overflow)
            for t in range(1, int(tm) + 1):
                Ck[t] = int(vec[0, k]) if vec.nnz else 0
                if t < tm: vec = vec @ M
        out.append(Ck)
    return out


# =====================================================================================================================
# L1/L2: linear walk-sum transmission fractions (exact Sherman-Morrison / Woodbury)
# =====================================================================================================================
class LinModel:
    """Linear walk-sum model  x = A x + u  on a node set (local indices 0..n-1).
    A[i, j] = gain of edge j -> i (dense float64), rows of S forced to zero (sources), u supported on S.
    R = (I - A)^-1.  x = R u (node responses), y = R^T 1_T, ytil = A^T y = (1_T^T R A)^T.
    O = 1_T^T R u  (= 1_T^T R A u because S and T are disjoint and u lives on S).
    Silencing set K (removing columns K of A):  O_{-K} = O - ytil_K^T (R_KK)^-1 x_K   (Woodbury; I + E_K^T R A E_K = R_KK)
    Single k:  O_{-k} = O - ytil_k x_k / R_kk;   f_k = 1 - O_{-k}/O = ytil_k x_k / (R_kk O)."""

    def __init__(self, A, S, T, u_S=None):
        """A: dense ndarray or scipy sparse [post, pre]. Only the dense inverse R is held (n^2 floats)."""
        self.S = np.asarray(S, np.int64); self.T = np.asarray(T, np.int64)
        assert len(np.intersect1d(self.S, self.T)) == 0
        n = A.shape[0]; self.n = n
        rmask = np.ones(n); rmask[self.S] = 0.0
        if sp.issparse(A):
            A = sp.diags(rmask) @ sp.csr_matrix(A, dtype=np.float64)
            A.eliminate_zeros()
            M = np.zeros((n, n), order='F')
            Ac = A.tocoo(); M[Ac.row, Ac.col] = -Ac.data
        else:
            A = np.array(A, dtype=np.float64, copy=True); A[self.S, :] = 0.0
            M = np.asfortranarray(-A)
        self.A = A
        M[np.diag_indices(n)] += 1.0
        u = np.zeros(n); u[self.S] = 1.0 if u_S is None else np.asarray(u_S, float)
        self.u = u
        self.R = sla.inv(M, overwrite_a=True, check_finite=False)
        del M
        oneT = np.zeros(n); oneT[self.T] = 1.0
        self.x = self.R @ u
        self.y = self.R.T @ oneT
        self.ytil = np.asarray(A.T @ self.y).ravel()
        self.O = float(oneT @ self.x)
        self.diag = np.diag(self.R).copy()

    def f_single(self):
        return self.ytil * self.x / (self.diag * self.O)

    def O_minus(self, K):
        K = np.asarray(K, np.int64)
        if len(K) == 0: return self.O
        RKK = self.R[np.ix_(K, K)]
        return self.O - float(self.ytil[K] @ np.linalg.solve(RKK, self.x[K]))

    def f_set(self, K):
        return 1.0 - self.O_minus(K) / self.O

    def f_pair(self, a, b):
        """returns (f_a, f_b, f_ab, overlap f_{a^b} = f_a + f_b - f_ab)"""
        fa, fb, fab = self.f_set([a]), self.f_set([b]), self.f_set([a, b])
        return fa, fb, fab, fa + fb - fab

    def O_direct(self, K):
        """Direct recomputation (dense solve) with columns K removed: for verification only (small n)."""
        A2 = self.A.toarray() if sp.issparse(self.A) else self.A.copy()
        A2[:, np.asarray(K, np.int64)] = 0.0
        M = np.eye(self.n) - A2
        oneT = np.zeros(self.n); oneT[self.T] = 1.0
        return float(oneT @ np.linalg.solve(M, self.u))


def spectral_radius(Msp, seed=0):
    """Largest |eigenvalue| of a sparse (or dense) square matrix via ARPACK (two independent runs, cross-checked)."""
    from scipy.sparse.linalg import eigs
    n = Msp.shape[0]
    if n <= 600:
        return float(np.max(np.abs(np.linalg.eigvals(Msp.toarray() if sp.issparse(Msp) else Msp)))), 0.0
    Msp = sp.csr_matrix(Msp)
    rng = np.random.default_rng(seed)
    vals = []
    for r in range(2):
        ev = eigs(Msp, k=4, which='LM', v0=rng.random(n), tol=1e-12, maxiter=50000, ncv=40, return_eigenvectors=False)
        vals.append(float(np.max(np.abs(ev))))
    return vals[0], abs(vals[0] - vals[1])


def gmres_O(Asp, S, T, u_S, removed_cols=()):
    """Independent sparse iterative solve of (I - A') x = u with A' = A (S rows zeroed) minus columns removed_cols.
    Used to verify the dense Sherman-Morrison/Woodbury values on the real corridor."""
    from scipy.sparse.linalg import gmres, LinearOperator
    A = sp.csr_matrix(Asp, dtype=np.float64, copy=True)
    n = A.shape[0]
    rmask = np.ones(n); rmask[np.asarray(S, np.int64)] = 0.0
    cmask = np.ones(n); cmask[np.asarray(list(removed_cols), np.int64)] = 0.0
    A = sp.diags(rmask) @ A @ sp.diags(cmask)
    M = sp.identity(n, format='csr') - A
    u = np.zeros(n); u[np.asarray(S, np.int64)] = u_S
    x, info = gmres(M, u, rtol=1e-13, atol=0.0, restart=200, maxiter=2000)
    assert info == 0, f'gmres info {info}'
    return float(x[np.asarray(T, np.int64)].sum()), float(np.linalg.norm(M @ x - u) / np.linalg.norm(u))


# =====================================================================================================================
# max-flow fractions
# =====================================================================================================================
class FlowModel:
    """S->T max-flow on a directed graph (local node ids 0..n-1), integer capacities on edges (pre -> post).
    Super-source s* = n with infinite-capacity edges to S; super-sink t* = n+1 with infinite edges from T.
    Silencing k removes k's ORIGINAL out-edges (s*->k and k->t* kept).
    backend 'scipy' (int32 Dinic) or 'nx' (python ints, preflow-push)."""

    def __init__(self, n, pre, post, cap, S, T, backend='scipy'):
        self.n = n; self.S = np.asarray(S, np.int64); self.T = np.asarray(T, np.int64)
        assert len(np.intersect1d(self.S, self.T)) == 0
        pre = np.asarray(pre, np.int64); post = np.asarray(post, np.int64); cap = np.asarray(cap, np.int64)
        keep = (cap > 0) & (pre != post)
        self.pre, self.post, self.cap = pre[keep], post[keep], cap[keep]
        self.backend = backend
        self.INF = int(self.cap.sum()) + 1
        if backend == 'scipy': assert self.INF < 2 ** 31 - 1, 'capacities overflow int32; use backend nx'
        self.s, self.t = n, n + 1

    def _graph(self, removed=()):
        m = np.ones(len(self.pre), bool)
        if len(removed): m &= ~np.isin(self.pre, np.asarray(list(removed), np.int64))
        pre = np.concatenate([self.pre[m], np.full(len(self.S), self.s), self.T])
        post = np.concatenate([self.post[m], self.S, np.full(len(self.T), self.t)])
        cap = np.concatenate([self.cap[m], np.full(len(self.S) + len(self.T), self.INF)])
        return pre, post, cap

    def maxflow(self, removed=(), return_flow=False):
        pre, post, cap = self._graph(removed)
        if self.backend == 'scipy':
            G = sp.csr_matrix((cap.astype(np.int32), (pre, post)), shape=(self.n + 2, self.n + 2))
            r = maximum_flow(G, self.s, self.t, method='dinic')
            if not return_flow: return int(r.flow_value)
            F = r.flow.tocoo(); pos = F.data > 0
            thr = np.zeros(self.n + 2, np.int64); np.add.at(thr, F.row[pos], F.data[pos])
            return int(r.flow_value), thr[:self.n]
        import networkx as nx
        G = nx.DiGraph()
        G.add_nodes_from(range(self.n + 2))
        for a, b, c in zip(pre.tolist(), post.tolist(), cap.tolist()):
            G.add_edge(a, b, capacity=int(c))
        val, fd = nx.maximum_flow(G, self.s, self.t, flow_func=nx.algorithms.flow.preflow_push)
        if not return_flow: return int(val)
        thr = np.zeros(self.n, np.int64)
        for a in range(self.n):
            thr[a] = sum(v for v in fd[a].values() if v > 0)
        return int(val), thr

    def f_all(self, nodes=None):
        """f_k = 1 - MF(G minus out(k)) / MF(G) for every node (or `nodes`). Exact shortcut: if a maximum flow routes
        zero flow through k, that flow is feasible in G minus out(k), so f_k = 0; only nodes with positive throughput
        in the computed max flow are recomputed."""
        mf, thr = self.maxflow(return_flow=True)
        f = np.zeros(self.n)
        if mf == 0: return mf, np.full(self.n, np.nan), 0
        nodes = np.arange(self.n) if nodes is None else np.asarray(nodes)
        cand = [k for k in nodes if thr[k] > 0 and k not in set(self.T.tolist())]
        for k in cand:
            f[k] = 1.0 - self.maxflow(removed=[k]) / mf
        return mf, f, len(cand)

    def f_set(self, K):
        mf = self.maxflow()
        K = [k for k in K if k not in set(self.T.tolist())]
        return 1.0 - self.maxflow(removed=K) / mf if mf > 0 else np.nan


# =====================================================================================================================
# dominators / single-vertex cuts / minimum vertex cuts
# =====================================================================================================================
def dominators_of_T(n, pre, post, S, T, method='igraph'):
    """Strict dominators of the single target T w.r.t. a super-source over S (Lengauer-Tarjan in igraph, or networkx
    Cooper-Harvey-Kennedy). Returns sorted local ids (super-source and T excluded; S members included if any)."""
    T = int(np.atleast_1d(T)[0]) if np.ndim(T) else int(T)
    s = n
    if method == 'igraph':
        import igraph as ig
        g = ig.Graph(n=n + 1, directed=True)
        e = np.concatenate([np.column_stack([pre, post]), np.column_stack([np.full(len(S), s), S])]).astype(np.int64)
        g.add_edges(e)
        idom = g.dominator(s, mode='out')
        idom = [(-1 if (d is None or d != d) else int(d)) for d in idom]
        if idom[T] < 0 and T != s: return None                           # T unreachable
        out = []; v = idom[T]
        while v != s and v >= 0:
            out.append(v); v = idom[v]
        return sorted(out)
    import networkx as nx
    G = nx.DiGraph(); G.add_nodes_from(range(n + 1))
    G.add_edges_from(zip(np.asarray(pre).tolist(), np.asarray(post).tolist()))
    G.add_edges_from((s, int(x)) for x in S)
    if not nx.has_path(G, s, T): return None
    idom = nx.immediate_dominators(G, s)
    out = []; v = idom[T]
    while v != s:
        out.append(v); v = idom[v]
    return sorted(out)


class VertexCut:
    """Unit node capacities (node splitting); nodes in `uncut` (e.g. S and T) have 'infinite' capacity BIG.
    kappa = min number of cuttable vertices whose removal disconnects S from T (super-source over S, target T).
    kappa >= BIG means a path made only of uncuttable nodes exists (no finite vertex cut)."""

    def __init__(self, n, pre, post, S, T, uncut=()):
        self.n = n; self.S = np.asarray(S, np.int64); self.T = np.asarray(T, np.int64)
        self.pre = np.asarray(pre, np.int64); self.post = np.asarray(post, np.int64)
        self.uncut = np.zeros(n, bool); u = np.asarray(list(uncut), np.int64)
        if len(u): self.uncut[u] = True
        self.BIG = n + 10

    def _flow(self, removed=(), nodeflow=False):
        n = self.n; BIG = self.BIG
        alive = np.ones(n, bool); rm = np.asarray(list(removed), np.int64)
        if len(rm): alive[rm] = False
        m = alive[self.pre] & alive[self.post]
        a, b = self.pre[m], self.post[m]
        nodes = np.flatnonzero(alive)
        ncap = np.where(self.uncut[nodes], BIG, 1)
        s, t = 2 * n, 2 * n + 1
        S = self.S[alive[self.S]]; T = self.T[alive[self.T]]
        rows = np.concatenate([2 * nodes, 2 * a + 1, np.full(len(S), s), 2 * T + 1])
        cols = np.concatenate([2 * nodes + 1, 2 * b, 2 * S, np.full(len(T), t)])
        caps = np.concatenate([ncap, np.full(len(a), BIG), np.full(len(S), BIG), np.full(len(T), BIG)])
        assert (len(S) + 1) * BIG < 2 ** 31 and BIG < 2 ** 31
        G = sp.csr_matrix((caps.astype(np.int32), (rows, cols)), shape=(2 * n + 2, 2 * n + 2))
        r = maximum_flow(G, s, t, method='dinic')
        if not nodeflow: return int(r.flow_value)
        F = r.flow.tocoo()
        sel = (F.row % 2 == 0) & (F.col == F.row + 1) & (F.row < 2 * n) & (F.data > 0)
        through = np.zeros(n, np.int64); through[F.row[sel] // 2] = F.data[sel]
        return int(r.flow_value), through

    def kappa(self, removed=()):
        return self._flow(removed)

    def cut_nodes_single(self, exhaustive=False):
        """Cuttable nodes whose removal disconnects S from T. Exact shortcut (default): a node carrying zero flow in a
        maximum flow cannot be a cut (that flow survives its removal), so only positive-throughput nodes are tested.
        exhaustive=True tests every node (verification)."""
        k0, thr = self._flow(nodeflow=True)
        if k0 == 0: return []
        cand = range(self.n) if exhaustive else np.flatnonzero(thr > 0)
        return sorted(int(k) for k in cand if not self.uncut[k] and self.kappa([k]) == 0)

    def min_cut_members(self, exhaustive=False):
        """Exact: kappa and the set of cuttable nodes contained in SOME minimum vertex cut, i.e. kappa(G - v) = kappa - 1
        (only positive-throughput nodes can qualify unless exhaustive). Returns (kappa, sorted list)."""
        k0, thr = self._flow(nodeflow=True)
        if k0 == 0 or k0 >= self.BIG: return k0, []
        pool = range(self.n) if exhaustive else np.flatnonzero(thr > 0)
        return k0, sorted(int(v) for v in pool if not self.uncut[v] and self.kappa([v]) == k0 - 1)

    def all_min_cuts(self, cap=200000, exhaustive=False, time_budget=None):
        """Enumerate ALL minimum vertex cuts (cuttable nodes only). Exact branching: a set P is a subset of some minimum
        cut iff kappa(G - P) = kappa(G) - |P| (removing one vertex lowers kappa by at most 1); every min cut is reached
        through its sorted prefixes. Candidates = nodes with kappa(G - v) = kappa - 1 (which must carry flow in every
        max flow, so only positive-throughput nodes are tested unless exhaustive). Returns (kappa, cuts, complete)."""
        k0, thr = self._flow(nodeflow=True)
        if k0 >= self.BIG: return k0, [], False
        if k0 == 0: return 0, [], True
        pool = range(self.n) if exhaustive else np.flatnonzero(thr > 0)
        cand = [int(v) for v in pool if not self.uncut[v] and self.kappa([v]) == k0 - 1]
        cuts = []; state = dict(complete=True); t0 = time.time()

        def rec(P, start):
            if len(cuts) >= cap or (time_budget is not None and time.time() - t0 > time_budget):
                state['complete'] = False; return
            if len(P) == k0: cuts.append(tuple(P)); return
            for i in range(start, len(cand)):
                v = cand[i]
                if self.kappa(P + [v]) == k0 - len(P) - 1:
                    rec(P + [v], i + 1)
        rec([], 0)
        return k0, cuts, state['complete']


# =====================================================================================================================
# L0
# =====================================================================================================================
def igraph_from_edges(n, pre, post):
    import igraph as ig
    g = ig.Graph(n=n, directed=True)
    E = np.column_stack([pre, post]).astype(np.int64)
    for a in range(0, len(E), 2_000_000):                          # chunked to bound the python-conversion peak
        g.add_edges(E[a:a + 2_000_000])
    return g


def pagerank_power(n, pre, post, w, d=0.85, tol=1e-13, maxit=1000):
    """Reference PageRank (verification of igraph/PRPACK): weighted out-normalized transitions, dangling mass and
    teleport uniform. p = d (P^T p + dangling(p)/n) + (1 - d)/n."""
    out_s = np.bincount(pre, weights=w, minlength=n)
    P = sp.csr_matrix((w / out_s[pre], (post, pre)), shape=(n, n))
    dang = out_s == 0
    p = np.full(n, 1.0 / n)
    for it in range(maxit):
        p2 = d * (P @ p + p[dang].sum() / n) + (1 - d) / n
        if np.abs(p2 - p).sum() < tol: p = p2; break
        p = p2
    return p / p.sum(), it


def sampled_betweenness(g, n, k, seed, batches=10):
    """Brandes betweenness (unweighted, directed, endpoints excluded) restricted to a uniform random sample of k sources
    (without replacement), scaled by n/k: unbiased for B(v) = sum_{s != v != t} sigma_st(v)/sigma_st.
    Split into `batches` equal batches; returns (estimate, per-batch estimates (batches, n))."""
    rng = np.random.default_rng(seed)
    src = rng.choice(n, k, replace=False)
    per = []
    for b in np.array_split(src, batches):
        bb = np.asarray(g.betweenness(directed=True, sources=b.tolist()), float) * (n / len(b))
        per.append(bb)
    per = np.array(per)
    return per.mean(0), per


def lam50(lam, Omean):
    """lambda50: first upward crossing of 0.5*O_max by the MEAN curve (O_max = max over the grid), linear interpolation
    between the bracketing grid levels. Returns (lam50, O_max, index i with lam[i-1] < lam50 <= lam[i])."""
    Omax = float(np.max(Omean)); half = 0.5 * Omax
    i = int(np.argmax(Omean >= half))
    if i == 0: return float(lam[0]), Omax, 0
    l0, l1, o0, o1 = lam[i - 1], lam[i], Omean[i - 1], Omean[i]
    return float(l0 + (half - o0) * (l1 - l0) / (o1 - o0)), Omax, i


def interp_rates(lam, R, x):
    """linear interpolation of mean-rate matrix R (n_lam, n) at lambda = x."""
    i = int(np.searchsorted(lam, x))
    if i < len(lam) and lam[i] == x: return R[i].copy()
    w = (x - lam[i - 1]) / (lam[i] - lam[i - 1])
    return (1 - w) * R[i - 1] + w * R[i]


def empirical_gains(Wsub, r_a, r_b, active):
    """D_i = (r_i(b) - r_i(a)) / (mu_i(b) - mu_i(a)), mu = tau_s W r  (W in mV, rates in Hz -> mu in mV, D in Hz/mV).
    D_i = 0 for inactive i, and for |dmu| == 0 (counted). Wsub: sparse [post, pre] mV over the closure."""
    mu_a = TAU_S * (Wsub @ r_a); mu_b = TAU_S * (Wsub @ r_b)
    dmu = mu_b - mu_a; dr = r_b - r_a
    D = np.zeros(len(r_a)); ok = active & (dmu != 0)
    D[ok] = dr[ok] / dmu[ok]
    return D, dict(n_active=int(active.sum()), n_dmu_zero=int((active & (dmu == 0)).sum()),
                   n_neg=int((D < 0).sum()), n_pos=int((D > 0).sum()), mu_a=mu_a, mu_b=mu_b)


# =====================================================================================================================
# builders on the real connectome (reused by the driver and by the later pre-registered pair list)
# =====================================================================================================================
_G = {}


def csr_sorted(n, pre, post, dtype=np.int8):
    """CSR adjacency M[u, v] = 1 for u -> v, built directly from a pre-sorted edge list (no COO intermediates)."""
    assert np.all(np.diff(pre) >= 0)
    indptr = np.zeros(n + 1, np.int64); indptr[1:] = np.cumsum(np.bincount(pre, minlength=n))
    return sp.csr_matrix((np.ones(len(pre), dtype), np.asarray(post, np.int32), indptr), shape=(n, n))


def graph_mats(ver):
    """whole-brain matrices (cached): M_all/M_exc adjacency pre->post (int8 data; products with int64 vectors are
    int64), their transposes, in-strength."""
    if ver in _G: return _G[ver]
    g = C.load_graph(ver); n = g['n']
    exc = g['sign'] > 0
    d = dict(g=g, n=n, exc=exc, M_all=csr_sorted(n, g['pre'], g['post']),
             M_exc=csr_sorted(n, g['pre'][exc], g['post'][exc]),
             in_strength=np.bincount(g['post'], weights=g['nsyn'], minlength=n).astype(np.int64))
    d['MT_all'] = d['M_all'].T.tocsr(); d['MT_exc'] = d['M_exc'].T.tocsr()
    _G[ver] = d
    return d


def hop(ver, seeds, direction, graph):
    """hop distance from seeds ('from') or to seeds ('to') on the 'all' or 'exc' whole-brain graph."""
    d = graph_mats(ver)
    M = d['M_' + graph] if direction == 'from' else d['MT_' + graph]
    return bfs_dist(M, seeds)


def build_lin_s(ver, S, T, L=WALK_L):
    """f^LIN-S model on the corridor V_L = {v : d(S,v) + d(v,T) <= L} of the full signed graph.
    W_hat[i, j] = s_j n_ij / sum_j' n_ij'  (normalized by i's WHOLE-BRAIN total input synapse count), restricted to V_L,
    S rows zeroed; alpha = 0.9 / rho(W_hat_V); A = alpha W_hat_V; u = 1_S."""
    d = graph_mats(ver); g = d['g']
    dS = hop(ver, S, 'from', 'all'); dT = hop(ver, T, 'to', 'all')
    V = np.flatnonzero(dS + dT <= L)
    pos = -np.ones(d['n'], np.int64); pos[V] = np.arange(len(V))
    m = (pos[g['pre']] >= 0) & (pos[g['post']] >= 0)
    val = g['sign'][m].astype(np.float64) * g['nsyn'][m] / d['in_strength'][g['post'][m]]
    What = sp.csr_matrix((val, (pos[g['post'][m]], pos[g['pre'][m]])), shape=(len(V), len(V)))
    Sl, Tl = pos[S], pos[T]
    rmask = np.ones(len(V)); rmask[Sl] = 0.0
    What_used = (sp.diags(rmask) @ What).tocsr()
    rho, rho_dev = spectral_radius(What_used)
    alpha = LIN_ALPHA_FRAC / rho
    A = (alpha * What_used).tocsr()
    model = LinModel(A, Sl, Tl)
    info = dict(n_nodes=int(len(V)), n_edges=int(What.nnz), rho_What=rho, rho_check_absdiff=rho_dev, alpha=alpha, O=model.O)
    return model, V, A, info


def load_intact(ver, inp):
    z = np.load(C.OUT + f'intact_curve_{ver}_{inp}.npz', allow_pickle=False)
    return {k: z[k] for k in z.files}


def operating_point(ver, inp, ro, z=None):
    """lambda_ref = lambda50 of the readout's intact MEAN curve (60 seeds); rates at lambda_ref (linear interpolation of
    per-neuron mean rates); bracketing grid levels for the finite-difference gains."""
    z = load_intact(ver, inp) if z is None else z
    lam = z['lam']; key = 'mn9_contra_rates' if ro == 'contra' else 'mn9_ipsi_rates'
    Om = z[key].mean(1)
    if Om.max() <= 0: return None
    l50, Omax, i = lam50(lam, Om)
    r = interp_rates(lam, z['mean_rates'], l50)
    return dict(lam50=l50, Omax=Omax, i=i, lam_a=float(lam[i - 1]), lam_b=float(lam[i]), r=r,
                r_a=z['mean_rates'][i - 1], r_b=z['mean_rates'][i], fid=z['fid'], gidx=z['gidx'], Omean=Om, lam=lam)


def build_lin_a(ver, inp, ro, S, T, op=None, D_clip=False, extra_inactive=0, seed=0):
    """f^LIN-A: A_ij = tau_s D_i W_ij (W in mV = s n 0.275) on the active node set at lambda50 (r > 0) plus S and T;
    D from empirical_gains (finite difference between the grid levels bracketing lambda50); D_S = 0 (S rows zeroed:
    GRN rates are set by the stimulus); u_S = r_S(lambda50).  Returns (model, nodes_global, info)."""
    d = graph_mats(ver); g = d['g']
    op = operating_point(ver, inp, ro) if op is None else op
    cl = op['gidx']; N = len(cl)
    pos = -np.ones(d['n'], np.int64); pos[cl] = np.arange(N)
    m = (pos[g['pre']] >= 0) & (pos[g['post']] >= 0)
    W = sp.csr_matrix((g['sign'][m].astype(np.float64) * g['nsyn'][m] * W_SYN, (pos[g['post'][m]], pos[g['pre'][m]])), shape=(N, N))
    active = op['r'] > 0
    D, ginfo = empirical_gains(W, op['r_a'], op['r_b'], active)
    Sg = np.asarray(S); Tg = np.asarray(T)
    D[pos[Sg]] = 0.0
    if D_clip: D = np.maximum(D, 0.0)
    nodes_l = np.union1d(np.flatnonzero(active), np.union1d(pos[Sg], pos[Tg]))
    if extra_inactive:
        rng = np.random.default_rng(seed)
        inact = np.setdiff1d(np.arange(N), nodes_l)
        nodes_l = np.union1d(nodes_l, rng.choice(inact, min(extra_inactive, len(inact)), replace=False))
    Wl = W[nodes_l][:, nodes_l]
    A = sp.diags(TAU_S * D[nodes_l]) @ Wl
    lp = -np.ones(N, np.int64); lp[nodes_l] = np.arange(len(nodes_l))
    model = LinModel(A.toarray(), lp[pos[Sg]], lp[pos[Tg]], u_S=op['r'][pos[Sg]])
    ev = np.linalg.eigvals(model.A)
    rho = float(np.max(np.abs(ev))); max_re = float(np.max(ev.real))
    info = dict(n_nodes=int(len(nodes_l)), n_active=int(active.sum()), rho_A=rho, max_real_eig_A=max_re,
                linear_response_stable=bool(max_re < 1), walk_sum_converges=bool(rho < 1), n_D_neg=int((D < 0).sum()),
                n_D_pos=int((D > 0).sum()), n_dmu_zero=ginfo['n_dmu_zero'], O_lin=model.O,
                r0=op['r'][nodes_l], D=D[nodes_l])
    return model, cl[nodes_l], info


def build_mf_s(ver, S, T, L=WALK_L):
    """f^MF-S: excitatory corridor V^exc_L = {v : d_exc(S,v) + d_exc(v,T) <= L}; capacities n_ij (integer)."""
    d = graph_mats(ver); g = d['g']
    dS = hop(ver, S, 'from', 'exc'); dT = hop(ver, T, 'to', 'exc')
    V = np.flatnonzero(dS + dT <= L)
    pos = -np.ones(d['n'], np.int64); pos[V] = np.arange(len(V))
    m = d['exc'] & (pos[g['pre']] >= 0) & (pos[g['post']] >= 0)
    fm = FlowModel(len(V), pos[g['pre'][m]], pos[g['post'][m]], g['nsyn'][m], pos[S], pos[T], backend='scipy')
    return fm, V


def build_mf_a(ver, S, T, op, scale=1000):
    """f^MF-A: excitatory subgraph induced on (active at lambda50) + S + T; capacity n_ij * r_j(lambda50) in
    synapse*Hz, stored as round(scale * n_ij * r_j) integers (networkx backend, exact integer arithmetic)."""
    d = graph_mats(ver); g = d['g']
    cl = op['gidx']
    act_g = cl[op['r'] > 0]
    V = np.union1d(act_g, np.union1d(S, T))
    rg = np.zeros(d['n']); rg[cl] = op['r']
    pos = -np.ones(d['n'], np.int64); pos[V] = np.arange(len(V))
    m = d['exc'] & (pos[g['pre']] >= 0) & (pos[g['post']] >= 0)
    cap = np.rint(scale * g['nsyn'][m].astype(np.float64) * rg[g['pre'][m]]).astype(np.int64)
    fm = FlowModel(len(V), pos[g['pre'][m]], pos[g['post'][m]], cap, pos[S], pos[T], backend='nx')
    return fm, V, (pos[g['pre'][m]], pos[g['post'][m]])


def active_exc_graph(ver, S, T, gidx, r):
    """excitatory subgraph induced on (r > 0) + S + T; returns (V global ids, local pre, local post, local S, local T)."""
    d = graph_mats(ver); g = d['g']
    V = np.union1d(gidx[r > 0], np.union1d(S, T))
    pos = -np.ones(d['n'], np.int64); pos[V] = np.arange(len(V))
    m = d['exc'] & (pos[g['pre']] >= 0) & (pos[g['post']] >= 0)
    return V, pos[g['pre'][m]], pos[g['post'][m]], pos[S], pos[T]


def mincut_participation_over_grid(ver, S, T, Z, ro):
    """min-cut participation count of k = number of intact-grid levels lambda (with mean readout rate > 0) at which k
    belongs to SOME minimum S->T vertex cut of the excitatory active graph at lambda (S and T uncuttable; exact
    membership test kappa(G - k) = kappa - 1). Returns (whole-brain int array, {lambda: kappa})."""
    n = graph_mats(ver)['n']
    key = 'mn9_contra_rates' if ro == 'contra' else 'mn9_ipsi_rates'
    Om = Z[key].mean(1)
    cnt = np.zeros(n, np.int64); kap = {}
    for a, lam in enumerate(Z['lam']):
        if Om[a] <= 0: kap[float(lam)] = None; continue
        V, pre, post, Sl, Tl = active_exc_graph(ver, S, T, Z['gidx'], Z['mean_rates'][a])
        vc = VertexCut(len(V), pre, post, Sl, Tl, uncut=np.concatenate([Sl, Tl]))
        k0, memb = vc.min_cut_members()
        kap[float(lam)] = int(k0)
        cnt[V[memb]] += 1
    return cnt, kap


def pair_fractions(ver, inp, ro, pairs, estimators=('LIN-S', 'LIN-A')):
    """For a pre-registered list of (fid_a, fid_b): f_a, f_b, f_ab (exact rank-2 Woodbury) and overlap
    f_{a^b} = f_a + f_b - f_ab, for the LIN-S and/or LIN-A estimators. Neurons outside a model have f = 0 there."""
    g = C.load_graph(ver)
    S = C.idx_of(g, C.INPUTS[inp](ver)); T = C.idx_of(g, [C.READOUTS[ro](ver)])
    rows = []
    for est in estimators:
        if est == 'LIN-S': model, nodes, _, _ = build_lin_s(ver, S, T)
        else: model, nodes, _ = build_lin_a(ver, inp, ro, S, T)
        loc = pd.Series(np.arange(len(nodes)), index=nodes)
        for fa_, fb_ in pairs:
            ia, ib = C.idx_of(g, [fa_])[0], C.idx_of(g, [fb_])[0]
            K = [int(loc[i]) for i in (ia, ib) if i in loc.index]
            f_a = model.f_set([int(loc[ia])]) if ia in loc.index else 0.0
            f_b = model.f_set([int(loc[ib])]) if ib in loc.index else 0.0
            f_ab = model.f_set(K) if K else 0.0
            rows.append(dict(estimator=est, fid_a=fa_, fid_b=fb_, f_a=f_a, f_b=f_b, f_ab=f_ab, overlap=f_a + f_b - f_ab))
        del model
    return pd.DataFrame(rows)


# =====================================================================================================================
# driver
# =====================================================================================================================
def _log(msg, fh=None):
    s = time.strftime('%H:%M:%S ') + msg
    print(s, flush=True)
    if fh: fh.write(s + '\n'); fh.flush()


def _sel(arr_global, rows):
    return np.asarray(arr_global)[rows]


def l0_block(ver, rows, log):
    d = graph_mats(ver); g = d['g']; n = d['n']
    t0 = time.time(); res = {}; info = {}
    res['in_degree'] = np.bincount(g['post'], minlength=n)
    res['out_degree'] = np.bincount(g['pre'], minlength=n)
    res['in_strength'] = d['in_strength']
    res['out_strength'] = np.bincount(g['pre'], weights=g['nsyn'], minlength=n).astype(np.int64)
    res['total_degree'] = res['in_degree'] + res['out_degree']
    res['rich_club_deg37'] = res['total_degree'] > RICH_CLUB_DEG
    pr, it = pagerank_power(n, g['pre'], g['post'], g['nsyn'].astype(float))
    res['pagerank'] = pr; info['pagerank_power_iters'] = it
    log(f'L0 degrees/strength/pagerank done ({time.time()-t0:.0f}s)')
    # cross-check of the power-iteration PageRank against igraph/PRPACK on a 20k-node induced subgraph (a full-graph
    # igraph weight list would need ~0.5 GB of Python floats; the implementations are also unit-tested vs networkx)
    sub = np.sort(np.random.default_rng(0).choice(n, 20000, replace=False)); ps_ = -np.ones(n, np.int64); ps_[sub] = np.arange(len(sub))
    msk = (ps_[g['pre']] >= 0) & (ps_[g['post']] >= 0)
    a_, b_, w_ = ps_[g['pre'][msk]], ps_[g['post'][msk]], g['nsyn'][msk].astype(float)
    pr_s, _ = pagerank_power(len(sub), a_, b_, w_)
    pr_i = np.array(igraph_from_edges(len(sub), a_, b_).pagerank(weights=w_.tolist(), damping=0.85, directed=True))
    info['pagerank_igraph_vs_power_subgraph20k_maxabs'] = float(np.abs(pr_i - pr_s).max())
    info['pagerank_igraph_vs_power_subgraph20k_max_rel'] = float((np.abs(pr_i - pr_s) / pr_s).max())
    ig_g = igraph_from_edges(n, g['pre'], g['post'])
    res['kcore_total'] = np.array(ig_g.coreness(mode='all'))
    log(f'L0 igraph pagerank check + coreness done ({time.time()-t0:.0f}s)')
    reps = []
    for sd in BETW_SEEDS:
        tb = time.time()
        est, per = sampled_betweenness(ig_g, n, BETW_K, sd, batches=10)
        reps.append((est, per)); log(f'L0 betweenness replicate seed {sd}: {time.time()-tb:.0f}s')
    del ig_g
    b1, b2 = reps[0][0], reps[1][0]
    res['betweenness'] = 0.5 * (b1 + b2)
    res['betweenness_rep1'] = b1; res['betweenness_rep2'] = b2
    # SE of the combined estimator from the 20 batch estimates (each batch = 100 sources scaled by n/100)
    allb = np.vstack([reps[0][1], reps[1][1]])
    res['betweenness_se'] = allb.std(0, ddof=1) / np.sqrt(allb.shape[0])
    from scipy.stats import spearmanr
    rr = rows
    nz = (res['betweenness'][rr] > 0)
    info['betweenness'] = dict(k_per_replicate=BETW_K, batches=10, seeds=list(BETW_SEEDS), n=n,
                               spearman_rep1_rep2_rows=float(spearmanr(b1[rr], b2[rr])[0]),
                               spearman_rep1_rep2_all=float(spearmanr(b1, b2)[0]),
                               median_rel_se_rows_nonzero=float(np.median(res['betweenness_se'][rr][nz] / res['betweenness'][rr][nz])),
                               rel_var_rep_diff_rows=float(np.var((b1 - b2)[rr]) / max(np.var(res['betweenness'][rr]), 1e-300)))
    info['wall_s'] = round(time.time() - t0, 1)
    return res, info


def dominator_variants(ver, S, T_list, log):
    """dominators of each T (super-source over S) on the unsigned and excitatory whole-brain graphs (igraph LT);
    cross-checked by direct path/BFS removal tests (cut_nodes_by_path)."""
    import igraph as ig
    d = graph_mats(ver); g = d['g']; n = d['n']
    out = {}
    for gname, mask in (('all', np.ones(len(g['pre']), bool)), ('exc', d['exc'])):
        pre, post = g['pre'][mask], g['post'][mask]
        G = igraph_from_edges(n + 1, pre, post)
        G.add_edges(np.column_stack([np.full(len(S), n), S]))
        idom = G.dominator(n, mode='out'); del G
        idom = np.array([(-1 if (v is None or v != v) else int(v)) for v in idom])
        for T in T_list:
            v = idom[T]; dom = []
            if v < 0: out[(gname, T)] = dict(doms=None); continue
            while v != n and v >= 0: dom.append(int(v)); v = idom[v]
            pc = cut_nodes_by_path(d['M_' + gname], S, T)
            out[(gname, T)] = dict(doms=sorted(dom), path_bfs_crosscheck=pc, agree=sorted(dom) == pc)
            log(f'dominators {gname} T={T}: {sorted(dom)} (path/BFS cross-check agree={sorted(dom) == pc})')
    return out


def _mask(n, idx):
    m = np.zeros(n, bool)
    idx = np.asarray(list(idx), np.int64)
    if len(idx): m[idx] = True
    return m


def _jsonable(o):
    if isinstance(o, dict): return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_jsonable(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, np.ndarray): return _jsonable(o.tolist())
    return o


CACHE = C.OUT + 'cache/'


def stage_struct(ver, inputs, readouts, log):
    """Stage 1 (structure only; no simulation input): L0, hop distances, and per (input, readout): walk counts,
    whole-brain dominators, f^LIN-S, f^MF-S, corridor dominators, set-level type fractions. Whole-brain arrays are
    cached in out/cache/ so stage 2 can be re-run without recomputation."""
    import gc
    from scipy.stats import spearmanr
    os.makedirs(CACHE, exist_ok=True)
    d = graph_mats(ver); g = d['g']; n = d['n']
    ext = C.ext_type_members(ver)
    # ---- L0
    p0 = CACHE + f'l0_{ver}.npz'
    if os.path.exists(p0):
        z = np.load(p0); WB0 = {k: z[k] for k in z.files}; l0info = json.load(open(p0 + '.json'))
        log('L0 loaded from cache')
    else:
        WB0, l0info = l0_block(ver, np.arange(n), log)
        np.savez(p0, **WB0); json.dump(_jsonable(l0info), open(p0 + '.json', 'w'), indent=1)
    out = dict(WB=dict(WB0), info=dict(L0=l0info), tset={})
    WB = out['WB']
    hopT = {}
    for ro in readouts:
        Tg = C.idx_of(g, [C.READOUTS[ro](ver)])
        for gr in ('all', 'exc'):
            hopT[(ro, gr)] = hop(ver, Tg, 'to', gr); WB[f'hop_to_T_{gr}__{ro}'] = hopT[(ro, gr)]
        WB[f'neg_hop_to_T__{ro}'] = -hopT[(ro, 'all')]
    for inp in inputs:
        Sg = C.idx_of(g, C.INPUTS[inp](ver))
        for gr in ('all', 'exc'):
            WB[f'hop_from_S_{gr}__{inp}'] = hop(ver, Sg, 'from', gr)
    for inp in inputs:
        Sg = C.idx_of(g, C.INPUTS[inp](ver))
        dSa = WB[f'hop_from_S_all__{inp}']
        doms_full = None
        for ro in readouts:
            tag = f'{inp}_{ro}'; t1 = time.time()
            pc = CACHE + f'struct_{ver}_{tag}.npz'
            if os.path.exists(pc):
                z = np.load(pc); WB.update({k: z[k] for k in z.files}); js = json.load(open(pc + '.json'))
                out['info'][tag] = js['chk']; out['tset'][tag] = js['tset']; log(f'{tag}: stage-1 loaded from cache'); continue
            W1 = {}; chk = {}; tset = {}
            Tg = C.idx_of(g, [C.READOUTS[ro](ver)]); Ti = int(Tg[0])
            # ---------- walks
            th, vi, tot = walk_counts_through(d['M_all'], Sg, Tg, WALK_L, d_S=dSa, d_T=hopT[(ro, 'all')], MT=d['MT_all'])
            W1[f'walks_through_L5__{tag}'] = th; W1[f'walk_visits_L5__{tag}'] = vi
            chk['walks_total_L5'] = int(tot); chk['walks_through_S_sum'] = int(th[Sg].sum())
            chk['walks_through_T_equals_total'] = bool(th[Ti] == tot)
            log(f'{tag}: walks total {tot} ({time.time()-t1:.0f}s)')
            # ---------- dominators on whole-brain graphs
            if doms_full is None:
                doms_full = dominator_variants(ver, Sg, [int(C.idx_of(g, [C.READOUTS[r](ver)])[0]) for r in readouts], log)
            for gr in ('all', 'exc'):
                r_ = doms_full[(gr, Ti)]; doms = r_['doms'] or []
                W1[f'dominator_{gr}__{tag}'] = _mask(n, doms)
                chk[f'dominators_{gr}'] = dict(ids=[int(g['fid'][v]) for v in doms], mf_agree=r_.get('agree'),
                                               reachable=r_['doms'] is not None)
            # ---------- LIN-S
            t2 = time.time()
            model, V, Asp, linfo = build_lin_s(ver, Sg, Tg)
            f = model.f_single()
            fg = np.zeros(n); fg[V] = f; W1[f'fLIN_S__{tag}'] = fg
            xg = np.zeros(n); xg[V] = model.x; W1[f'LIN_S_x__{tag}'] = xg
            pos = pd.Series(np.arange(len(V)), index=V)
            Sl = pos[Sg].values
            linfo['f_S_all'] = model.f_set(Sl); linfo['sum_f_GRN'] = float(f[Sl].sum())
            linfo['f_T'] = float(f[pos[Ti]]); linfo['n_negative_f'] = int((f < 0).sum())
            gs = np.bincount(g['pre'], weights=g['nsyn'], minlength=n)[Sg]
            linfo['GRN_f'] = {int(g['fid'][s]): float(f[pos[s]]) for s in Sg}
            linfo['GRN_f_vs_outstrength_spearman'] = float(spearmanr(f[Sl], gs)[0])
            rng = np.random.default_rng(0)
            pick = list(np.argsort(-np.abs(f))[:8]) + list(rng.choice(len(V), 8, replace=False))
            O0, res0 = gmres_O(Asp, Sl, [pos[Ti]], 1.0)
            vr = dict(O_dense=model.O, O_gmres=O0, gmres_relres=res0, max_abs_f_diff=0.0, n_checked=0)
            for k in pick:
                Ok, _ = gmres_O(Asp, Sl, [pos[Ti]], 1.0, removed_cols=[k])
                vr['max_abs_f_diff'] = max(vr['max_abs_f_diff'], abs((1 - Ok / O0) - f[k])); vr['n_checked'] += 1
            Oab, _ = gmres_O(Asp, Sl, [pos[Ti]], 1.0, removed_cols=[pick[0], pick[1]])
            vr['pair_woodbury_vs_gmres_absdiff'] = abs((1 - Oab / O0) - model.f_set([pick[0], pick[1]]))
            OS, _ = gmres_O(Asp, Sl, [pos[Ti]], 1.0, removed_cols=list(Sl))
            vr['all_S_removed_O_gmres'] = OS
            for tname, mem in ext.items():
                K = [int(pos[i]) for i in C.idx_of(g, mem['present']) if i in pos.index]
                tset[tname] = dict(fLIN_S=model.f_set(K) if K else 0.0, n_in_LIN_S_corridor=len(K))
                if K:
                    Ok, _ = gmres_O(Asp, Sl, [pos[Ti]], 1.0, removed_cols=K)
                    vr[f'type_{tname}_woodbury_vs_gmres_absdiff'] = abs((1 - Ok / O0) - tset[tname]['fLIN_S'])
            linfo['verification'] = vr
            chk['LIN_S'] = linfo
            log(f'{tag}: LIN-S n={linfo["n_nodes"]} rho={linfo["rho_What"]:.6f} O={model.O:.4g} f_S={linfo["f_S_all"]:.15f} '
                f'sumGRN={linfo["sum_f_GRN"]:.15f} verify maxdiff={vr["max_abs_f_diff"]:.2e} ({time.time()-t2:.0f}s)')
            del model, Asp; gc.collect()
            # ---------- MF-S
            t3 = time.time()
            fm, Vx = build_mf_s(ver, Sg, Tg)
            mf, fmf, ncand = fm.f_all()
            fgm = np.zeros(n); fgm[Vx] = fmf; W1[f'fMF_S__{tag}'] = fgm
            posx = pd.Series(np.arange(len(Vx)), index=Vx)
            mfinfo = dict(n_nodes=int(len(Vx)), n_edges=int(len(fm.pre)), MF=mf, n_recomputed=ncand,
                          f_S_all=fm.f_set(list(posx[Sg].values)), f_T=float(fmf[posx[Ti]]),
                          GRN_f={int(g['fid'][s]): float(fmf[posx[s]]) for s in Sg if s in posx.index},
                          n_GRN_in_corridor=int(np.isin(Sg, Vx).sum()))
            mfinfo['sum_f_GRN'] = float(sum(mfinfo['GRN_f'].values()))
            fmx = FlowModel(fm.n, fm.pre, fm.post, fm.cap, fm.S, fm.T, backend='nx')
            top = np.argsort(-fmf)[:2]
            mfinfo['nx_check'] = dict(MF_nx=fmx.maxflow(), f_nx=[1 - fmx.maxflow([k]) / mf for k in top],
                                      f_scipy=[float(fmf[k]) for k in top])
            del fmx
            for tname, mem in ext.items():
                K = [int(posx[i]) for i in C.idx_of(g, mem['present']) if i in posx.index]
                tset[tname].update(fMF_S=(fm.f_set(K) if K else 0.0), n_in_MF_S_corridor=len(K))
            dc_ig = dominators_of_T(fm.n, fm.pre, fm.post, fm.S, int(fm.T[0]), 'igraph')
            dc_nx = dominators_of_T(fm.n, fm.pre, fm.post, fm.S, int(fm.T[0]), 'networkx')
            dc_mf = VertexCut(fm.n, fm.pre, fm.post, fm.S, fm.T, uncut=fm.T).cut_nodes_single()
            mfinfo['corridor_dominators'] = dict(igraph=[int(g['fid'][Vx[v]]) for v in (dc_ig or [])],
                                                 agree_igraph_networkx_mf=((dc_ig or []) == (dc_nx or []) == dc_mf))
            W1[f'dominator_exc_L5__{tag}'] = _mask(n, Vx[dc_ig or []])
            chk['MF_S'] = mfinfo
            log(f'{tag}: MF-S n={len(Vx)} MF={mf} recomputed={ncand} f_S={mfinfo["f_S_all"]} nx={mfinfo["nx_check"]} '
                f'corr.doms={mfinfo["corridor_dominators"]} ({time.time()-t3:.0f}s)')
            del fm; gc.collect()
            chk['stage1_wall_s'] = round(time.time() - t1, 1)
            np.savez(pc, **W1); json.dump(_jsonable(dict(chk=chk, tset=tset)), open(pc + '.json', 'w'), indent=1)
            WB.update(W1); out['info'][tag] = _jsonable(chk); out['tset'][tag] = _jsonable(tset)
    return out


def stage_activity(ver, inp, ro, Z, WB, tset, log):
    """Stage 2 (INTACT simulation + structure) for one (input, readout): r(lambda50), D, f^LIN-A (+ variants),
    f^MF-A, active dominators, min-cut participation, set-level type fractions."""
    import gc
    from scipy.stats import spearmanr
    d = graph_mats(ver); g = d['g']; n = d['n']; A = C.load_annotations()
    ext = C.ext_type_members(ver)
    tag = f'{inp}_{ro}'; t4 = time.time()
    Sg = C.idx_of(g, C.INPUTS[inp](ver)); Tg = C.idx_of(g, [C.READOUTS[ro](ver)]); Ti = int(Tg[0])
    op = operating_point(ver, inp, ro, Z)
    if op is None:
        log(f'{tag}: readout silent at every lambda -> no L2')
        for tname in ext: tset[tname].update(fLIN_A=np.nan, n_in_active_LIN=0, fMF_A=np.nan, n_in_active_MF=0)
        return None
    cl = op['gidx']; rg = np.zeros(n); rg[cl] = op['r']; WB[f'rate_lam50__{tag}'] = rg
    model, nodesA, ainfo = build_lin_a(ver, inp, ro, Sg, Tg, op=op)
    fa = model.f_single()
    fga = np.zeros(n); fga[nodesA] = fa; WB[f'fLIN_A__{tag}'] = fga
    r0 = ainfo['r0']
    fa_r0 = model.ytil * r0 / (model.diag * model.O)
    fgr = np.zeros(n); fgr[nodesA] = fa_r0; WB[f'fLIN_A_r0__{tag}'] = fgr
    Dg = np.zeros(n); Dg[nodesA] = ainfo['D']; WB[f'gain_D__{tag}'] = Dg
    posa = pd.Series(np.arange(len(nodesA)), index=nodesA)
    Sla = posa[Sg].values
    kk = np.random.default_rng(1).choice(len(nodesA), min(150, len(nodesA)), replace=False)
    dd = max(abs((1 - model.O_direct([k]) / model.O) - fa[k]) for k in kk)
    A_ = model.A; eq = 0.0
    A3 = A_.copy(); A3[:, Sla] = 0
    dOS = np.linalg.solve(np.eye(model.n) - A3, model.u)[model.T].sum() - model.O
    for k in kk[:40]:
        A2 = A_.copy(); A2[:, k] = 0
        dO = -np.linalg.solve(np.eye(model.n) - A2, A_[:, k] * model.x[k])[model.T].sum()
        eq = max(eq, abs(dO / dOS - fa[k]))
    m2, n2, _ = build_lin_a(ver, inp, ro, Sg, Tg, op=op, extra_inactive=1500)
    f2 = m2.f_single(); p2 = pd.Series(np.arange(len(n2)), index=n2)
    pad_diff = float(np.abs(f2[p2[nodesA].values] - fa).max())
    pad_inact = float(np.abs(np.delete(f2, p2[nodesA].values)).max()); del m2
    mD, nD, _ = build_lin_a(ver, inp, ro, Sg, Tg, op=op, D_clip=True)
    fD = np.zeros(n); fD[nD] = mD.f_single(); WB[f'fLIN_A_Dpos__{tag}'] = fD
    # sensitivity: A rescaled to spectral radius 0.9 when rho(A) >= 1 (same convention as LIN-S); identical otherwise
    sc = min(1.0, LIN_ALPHA_FRAC / ainfo['rho_A'])
    mS = LinModel(model.A * sc, model.S, model.T, u_S=model.u[model.S])
    fsc = np.zeros(n); fsc[nodesA] = mS.f_single(); WB[f'fLIN_A_scaled__{tag}'] = fsc
    scaled_spearman = float(spearmanr(fa, fsc[nodesA])[0]); del mS
    ai = {k: v for k, v in ainfo.items() if k not in ('r0', 'D')}
    ai.update(lam50=op['lam50'], Omax=op['Omax'], lam_a=op['lam_a'], lam_b=op['lam_b'],
              f_S_all=model.f_set(list(Sla)), sum_f_GRN=float(fa[Sla].sum()), f_T=float(fa[posa[Ti]]),
              n_negative_f=int((fa < 0).sum()),
              GRN_f={int(g['fid'][s]): float(fa[posa[s]]) for s in Sg},
              GRN_rate_over_lambda50=float(np.mean(op['r'][np.searchsorted(cl, Sg)]) / op['lam50']),
              verify_SM_vs_direct_maxabs=float(dd), verify_linear_response_identity_maxabs=float(eq),
              verify_padding_inactive_active_maxabs=pad_diff, verify_padding_inactive_f_maxabs=pad_inact,
              spearman_fLINA_vs_fLINA_r0=float(spearmanr(fa, fa_r0)[0]),
              scaled_variant_factor=sc, spearman_fLINA_vs_scaled=scaled_spearman,
              spearman_fLINA_vs_Dpos=float(spearmanr(fa, fD[nodesA])[0]),
              spearman_x_vs_r0_active=float(spearmanr(model.x, r0)[0]),
              rho_A_Dpos=float(np.max(np.abs(np.linalg.eigvals(mD.A)))),
              D_quantiles_active=[float(q) for q in np.quantile(ainfo['D'][ainfo['D'] != 0], [0, .05, .5, .95, 1])] if (ainfo['D'] != 0).any() else None)
    for tname, mem in ext.items():
        K = [int(posa[i]) for i in C.idx_of(g, mem['present']) if i in posa.index]
        fv = model.f_set(K) if K else 0.0
        if K: ai[f'type_{tname}_woodbury_vs_direct'] = abs(fv - (1 - model.O_direct(K) / model.O))
        tset[tname].update(fLIN_A=fv, n_in_active_LIN=len(K))
    del model, mD; gc.collect()
    log(f'{tag}: lam50={op["lam50"]:.3f} Omax={op["Omax"]:.2f} LIN-A n={ainfo["n_nodes"]} rho={ainfo["rho_A"]:.4f} maxRe={ainfo["max_real_eig_A"]:.4f} '
        f'f_S={ai["f_S_all"]:.15f} SMdiff={dd:.1e} eq={eq:.1e} pad={pad_diff:.1e}/{pad_inact:.1e} D<0:{ainfo["n_D_neg"]}')
    # ---------- MF-A
    fma, Va, (ea, eb) = build_mf_a(ver, Sg, Tg, op)
    mfa, fmfa, nc = fma.f_all()
    fgma = np.zeros(n); fgma[Va] = fmfa; WB[f'fMF_A__{tag}'] = fgma
    pva = pd.Series(np.arange(len(Va)), index=Va)
    mi = dict(n_nodes=int(len(Va)), n_edges=int(len(ea)), MF_milli_synHz=mfa, n_recomputed=nc,
              f_S_all=fma.f_set(list(pva[Sg].values)), f_T=float(fmfa[pva[Ti]]),
              GRN_f={int(g['fid'][s]): float(fmfa[pva[s]]) for s in Sg})
    mi['sum_f_GRN'] = float(sum(mi['GRN_f'].values()))
    for tname, mem in ext.items():
        K = [int(pva[i]) for i in C.idx_of(g, mem['present']) if i in pva.index]
        tset[tname].update(fMF_A=(fma.f_set(K) if K else 0.0), n_in_active_MF=len(K))
    da_ig = dominators_of_T(fma.n, ea, eb, fma.S, int(fma.T[0]), 'igraph') or []
    da_nx = dominators_of_T(fma.n, ea, eb, fma.S, int(fma.T[0]), 'networkx') or []
    da_mf = VertexCut(fma.n, ea, eb, fma.S, fma.T, uncut=fma.T).cut_nodes_single()
    Sset = set(fma.S.tolist())
    da_noS = [v for v in da_ig if v not in Sset]
    WB[f'dominator_active__{tag}'] = _mask(n, Va[da_noS])
    # min-cut membership at lambda50 (exact) and participation count over the intact grid
    vc = VertexCut(fma.n, ea, eb, fma.S, fma.T, uncut=np.concatenate([fma.S, fma.T]))
    kap, memb = vc.min_cut_members()
    WB[f'in_min_vertex_cut_lam50__{tag}'] = _mask(n, Va[memb])
    if 0 < kap < vc.BIG and len(memb) == kap:          # union of all minimum cuts has size kappa => the cut is unique
        cuts, complete = [tuple(memb)], True
    else:
        kap_e, cuts, complete = vc.all_min_cuts(time_budget=60)
    cnt = np.full(n, np.nan)
    if complete:
        part = np.zeros(fma.n, np.int64)
        for cs in cuts: part[list(cs)] += 1
        cnt[Va] = part
    WB[f'n_min_cuts_containing_lam50__{tag}'] = cnt
    pc_count, kap_grid = mincut_participation_over_grid(ver, Sg, Tg, Z, ro)
    WB[f'mincut_participation__{tag}'] = pc_count
    mi.update(dominators_active=[int(g['fid'][Va[v]]) for v in da_noS],
              dominators_active_types=[str(A['cell_type'].get(int(g['fid'][Va[v]]), 'NA')) for v in da_noS],
              dominators_including_S=[int(g['fid'][Va[v]]) for v in da_ig],
              dominators_agree_igraph_networkx_mf=(sorted(da_ig) == sorted(da_nx) == sorted(da_mf)),
              kappa_min_vertex_cut=int(kap), n_nodes_in_some_min_cut=len(memb),
              n_min_cuts=(len(cuts) if complete else None), min_cut_enumeration_complete=complete,
              min_cut_enumeration_note='exact enumeration attempted with a 60-s budget; if incomplete the number of minimum '
                                       'cuts is too large to enumerate and n_min_cuts_containing is NaN',
              kappa_over_grid=kap_grid, n_grid_levels_used=int(sum(1 for v in kap_grid.values() if v is not None)),
              n_nodes_participation_gt0=int((pc_count > 0).sum()))
    log(f'{tag}: MF-A n={len(Va)} MF={mfa} recomputed={nc} f_S={mi["f_S_all"]} doms={mi["dominators_active"]} '
        f'{mi["dominators_active_types"]} agree={mi["dominators_agree_igraph_networkx_mf"]} kappa={kap} '
        f'members={len(memb)} enum_complete={complete} grid-participation>0: {(pc_count > 0).sum()} ({time.time()-t4:.0f}s)')
    return _jsonable(dict(LIN_A=ai, MF_A=mi, wall_s=round(time.time() - t4, 1)))


def run_version(ver, inputs=('shiu', 'pure'), readouts=('contra', 'ipsi'), stage='all'):
    """stage='struct': stage 1 only (cached). stage='all': stage 1 (from cache if present) + stage 2 + table."""
    fh = open(C.ROOT + f'logs/predictors_{ver}.log', 'a')
    log = lambda s: _log(f'[{ver}] ' + s, fh)
    T0 = time.time()
    C.check_conventions()
    d = graph_mats(ver); g = d['g']; n = d['n']
    st = stage_struct(ver, inputs, readouts, log)
    if stage == 'struct': return st
    WB = st['WB']
    summary = dict(ver=ver, created=time.strftime('%Y-%m-%d %H:%M:%S'), L0=st['info']['L0'], checks={})
    ext = C.ext_type_members(ver); ext_rows = []
    Z = {inp: load_intact(ver, inp) for inp in inputs}
    for inp in inputs:
        for ro in readouts:
            tag = f'{inp}_{ro}'
            tset = {k: dict(v) for k, v in st['tset'][tag].items()}
            chk = dict(st['info'][tag]); chk['L2'] = stage_activity(ver, inp, ro, Z[inp], WB, tset, log)
            summary['checks'][tag] = chk
            for tname, mem in ext.items():
                ext_rows.append(dict(ver=ver, input=inp, readout=ro, type=tname, member_fids=';'.join(map(str, mem['all'])),
                                     n_members=len(mem['all']), n_present=len(mem['present']), **tset[tname]))
    # ---------------- rows and table
    rowset = set()
    for inp in inputs:
        rowset |= set(Z[inp]['gidx'].tolist()); rowset |= set(C.idx_of(g, C.INPUTS[inp](ver)).tolist())
    for ro in readouts: rowset.add(int(C.idx_of(g, [C.READOUTS[ro](ver)])[0]))
    rows = np.array(sorted(rowset), np.int64)
    df = pd.DataFrame({'fid': g['fid'][rows], 'gidx': rows})
    A = C.load_annotations()
    for col in ['cell_type', 'side', 'super_class', 'cell_class', 'cell_sub_class', 'top_nt']:
        df[col] = A[col].reindex(df.fid.values).values
    df['annotated_v783'] = df.fid.isin(A.index)
    for inp in inputs:
        df[f'is_S__{inp}'] = np.isin(rows, C.idx_of(g, C.INPUTS[inp](ver)))
        df[f'in_closure__{inp}'] = np.isin(rows, Z[inp]['gidx'])
        df[f'active_any_lambda__{inp}'] = np.isin(rows, Z[inp]['gidx'][Z[inp]['mean_rates'].max(0) > 0])
    for ro in readouts:
        df[f'is_T__{ro}'] = rows == C.idx_of(g, [C.READOUTS[ro](ver)])[0]
    for k in sorted(WB):
        df[k] = np.asarray(WB[k])[rows]
    log(f'rows: {len(rows)}, columns {df.shape[1]}')
    # ---------------- negative controls and correlations
    for inp in inputs:
        for ro in readouts:
            tag = f'{inp}_{ro}'
            nopath = ~np.isfinite(df[f'hop_from_S_all__{inp}'] + df[f'hop_to_T_all__{ro}'])
            noexc = ~np.isfinite(df[f'hop_from_S_exc__{inp}'] + df[f'hop_to_T_exc__{ro}'])
            cols = [c for c in df.columns if c.endswith('__' + tag) and c.startswith('f')]
            summary['checks'][tag]['negative_control'] = dict(
                n_rows_no_ST_path=int(nopath.sum()),
                max_abs_f_no_path={c: float(df.loc[nopath, c].abs().max()) if nopath.any() else 0.0 for c in cols},
                n_rows_no_exc_ST_path=int(noexc.sum()),
                max_abs_fMF_no_exc_path={c: float(df.loc[noexc, c].abs().max()) if noexc.any() else 0.0
                                         for c in cols if 'MF' in c})
            pc = ['in_degree', 'out_degree', 'in_strength', 'out_strength', 'pagerank', 'betweenness', 'kcore_total',
                  f'neg_hop_to_T__{ro}', f'walks_through_L5__{tag}', f'fLIN_S__{tag}', f'fMF_S__{tag}',
                  f'rate_lam50__{tag}', f'fLIN_A__{tag}', f'fLIN_A_r0__{tag}', f'fMF_A__{tag}', f'mincut_participation__{tag}']
            pc = [c for c in pc if c in df.columns]
            cand = df[f'active_any_lambda__{inp}'] & ~df[f'is_S__{inp}'] & ~df[f'is_T__{ro}']
            for nm, sub in (('rows', df), ('candidates', df[cand])):
                cm = sub[pc].replace([np.inf, -np.inf], np.nan).astype(float).corr(method='spearman')
                cm.to_csv(C.OUT + f'predictor_spearman_{ver}_{tag}_{nm}.csv')
            summary['checks'][tag]['n_candidates_active_nonS_nonT'] = int(cand.sum())
    df.to_parquet(C.OUT + f'predictors_{ver}.parquet', index=False)
    pd.DataFrame(ext_rows).to_csv(C.OUT + f'external_types_structural_{ver}.csv', index=False)
    summary['runtime_total_s_this_call'] = round(time.time() - T0, 1)
    json.dump(_jsonable(summary), open(C.OUT + f'predictors_{ver}_summary.json', 'w'), indent=1)
    log(f'DONE {time.time()-T0:.0f}s, {len(df)} rows x {df.shape[1]} cols')
    return df, summary


def write_s_pure_ids():
    A = C.load_annotations()
    ids = C.S_pure_all()
    shiu = set(pd.read_csv(C.IDS + 'sugar_GRN_right.csv').flywire_id.astype(np.int64))
    df = A.loc[ids, ['cell_type', 'cell_sub_class', 'side', 'super_class', 'top_nt']].reset_index()
    df['in_v783'] = df.root_id.isin(C.present_ids('v783')); df['in_v630'] = df.root_id.isin(C.present_ids('v630'))
    df['in_S_shiu_list'] = df.root_id.isin(shiu)
    df.rename(columns={'root_id': 'flywire_id'}).to_csv(C.OUT + 'S_pure_ids.csv', index=False)
    return df


def finalize(vers=('v783', 'v630')):
    """merge per-version external-type tables; write dominator / min-cut tables from the summaries."""
    ext = pd.concat([pd.read_csv(C.OUT + f'external_types_structural_{v}.csv') for v in vers
                     if os.path.exists(C.OUT + f'external_types_structural_{v}.csv')])
    ext.to_csv(C.OUT + 'external_types_structural.csv', index=False)
    rows = []
    for v in vers:
        p = C.OUT + f'predictors_{v}_summary.json'
        if not os.path.exists(p): continue
        sm = json.load(open(p))
        for tag, ck in sm['checks'].items():
            inp, ro = tag.split('_')
            for gname in ('all', 'exc'):
                dd = ck.get(f'dominators_{gname}', {})
                rows.append(dict(ver=v, input=inp, readout=ro, graph=f'whole-brain {"unsigned" if gname == "all" else "excitatory"}',
                                 dominators=';'.join(map(str, dd.get('ids', []))), crosscheck_agree=dd.get('mf_agree')))
            mfs = ck.get('MF_S', {}).get('corridor_dominators', {})
            rows.append(dict(ver=v, input=inp, readout=ro, graph='excitatory corridor L5',
                             dominators=';'.join(map(str, mfs.get('igraph', []))), crosscheck_agree=mfs.get('agree_igraph_networkx_mf')))
            l2 = (ck.get('L2') or {}).get('MF_A', {})
            if l2:
                rows.append(dict(ver=v, input=inp, readout=ro, graph='excitatory active at lambda50 (GRNs, T excluded)',
                                 dominators=';'.join(map(str, l2['dominators_active'])),
                                 dominator_types=';'.join(l2['dominators_active_types']),
                                 crosscheck_agree=l2['dominators_agree_igraph_networkx_mf'],
                                 kappa_min_vertex_cut=l2['kappa_min_vertex_cut'], n_min_cuts=l2['n_min_cuts'],
                                 enumeration_complete=l2['min_cut_enumeration_complete'],
                                 n_nodes_in_some_min_cut=l2['n_nodes_in_some_min_cut']))
    pd.DataFrame(rows).to_csv(C.OUT + 'dominators_and_mincuts.csv', index=False)
    # per-seed intact MN9 curves in long format, and the brief's file name for the primary input set
    import shutil
    long = []
    for v in vers:
        for inp in ('shiu', 'pure'):
            p = C.OUT + f'intact_curve_{v}_{inp}.npz'
            if not os.path.exists(p): continue
            z = np.load(p)
            for a, lam in enumerate(z['lam']):
                for b, sd in enumerate(z['seeds']):
                    long.append((v, inp, float(lam), int(sd), float(z['mn9_contra_rates'][a, b]), float(z['mn9_ipsi_rates'][a, b])))
            if inp == 'shiu': shutil.copyfile(p, C.OUT + f'intact_curve_{v}.npz')
    pd.DataFrame(long, columns=['ver', 'input', 'lam_hz', 'seed', 'mn9_contra_hz', 'mn9_ipsi_hz']).to_csv(
        C.OUT + 'intact_mn9_per_seed.csv', index=False)


if __name__ == '__main__':
    # python predictors.py <ver> [struct|all]      |      python predictors.py finalize
    if sys.argv[1] == 'finalize':
        write_s_pure_ids(); finalize()
    else:
        run_version(sys.argv[1], stage=sys.argv[2] if len(sys.argv) > 2 else 'all')
