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


# =====================================================================================================================
# L1: walk counts through k
# =====================================================================================================================
def walk_counts_through(M, S, T, L, d_S=None, d_T=None):
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
    MT = M.T.tocsr()
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
            vec = sp.csr_matrix(M[k])                     # walks of length 1 from k
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
        assert caps.sum() < 2 ** 31
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

    def all_min_cuts(self, cap=200000, exhaustive=False):
        """Enumerate ALL minimum vertex cuts (cuttable nodes only). Exact branching: a set P is a subset of some minimum
        cut iff kappa(G - P) = kappa(G) - |P| (removing one vertex lowers kappa by at most 1); every min cut is reached
        through its sorted prefixes. Candidates = nodes with kappa(G - v) = kappa - 1 (which must carry flow in every
        max flow, so only positive-throughput nodes are tested unless exhaustive). Returns (kappa, cuts, complete)."""
        k0, thr = self._flow(nodeflow=True)
        if k0 >= self.BIG: return k0, [], False
        if k0 == 0: return 0, [], True
        pool = range(self.n) if exhaustive else np.flatnonzero(thr > 0)
        cand = [int(v) for v in pool if not self.uncut[v] and self.kappa([v]) == k0 - 1]
        cuts = []; state = dict(complete=True)

        def rec(P, start):
            if len(cuts) >= cap: state['complete'] = False; return
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


def graph_mats(ver):
    """whole-brain matrices (cached): M_all/M_exc adjacency pre->post (int64), in-strength, signed W [post, pre]."""
    if ver in _G: return _G[ver]
    g = C.load_graph(ver); n = g['n']
    exc = g['sign'] > 0
    d = dict(g=g, n=n, exc=exc,
             M_all=csr_out(n, g['pre'], g['post']),
             M_exc=csr_out(n, g['pre'][exc], g['post'][exc]),
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
    val = g['sign'][m] * g['nsyn'][m] / d['in_strength'][g['post'][m]]
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
    W = sp.csr_matrix((g['sign'][m] * g['nsyn'][m] * W_SYN, (pos[g['post'][m]], pos[g['pre'][m]])), shape=(N, N))
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
    rho = float(np.max(np.abs(np.linalg.eigvals(model.A)))) if len(nodes_l) <= 4000 else spectral_radius(sp.csr_matrix(model.A))[0]
    info = dict(n_nodes=int(len(nodes_l)), n_active=int(active.sum()), rho_A=rho, n_D_neg=int((D < 0).sum()),
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
    cap = np.rint(scale * g['nsyn'][m] * rg[g['pre'][m]]).astype(np.int64)
    fm = FlowModel(len(V), pos[g['pre'][m]], pos[g['post'][m]], cap, pos[S], pos[T], backend='nx')
    return fm, V, (pos[g['pre'][m]], pos[g['post'][m]])


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
