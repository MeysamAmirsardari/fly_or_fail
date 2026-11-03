"""Unit tests for analysis/predictors.py on toy graphs with hand-computable or brute-force answers."""
import os, sys, itertools
import numpy as np, scipy.sparse as sp, networkx as nx, pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import predictors as P


def rand_signed(n, p, rng, S=(), zero_S_rows=True):
    A = (rng.random((n, n)) < p) * rng.uniform(-1, 1, (n, n))
    np.fill_diagonal(A, 0)
    rho = np.max(np.abs(np.linalg.eigvals(A))) or 1.0
    A = 0.9 * A / rho
    return A


# ------------------------------------------------------------------------------------------------- LIN: hand-computed
def test_lin_hand_parallel_feedback():
    # S={0} -> 1 (p), 0 -> 2 (q), 1 -> 3 (r), 2 -> 3 (s), feedback 3 -> 1 (c).  A[post, pre].
    p, q, r, s, c = 0.5, 0.3, 0.8, 0.4, 0.25
    A = np.zeros((4, 4)); A[1, 0] = p; A[2, 0] = q; A[3, 1] = r; A[3, 2] = s; A[1, 3] = c
    m = P.LinModel(A, [0], [3])
    O = (r * p + s * q) / (1 - r * c)
    assert m.O == pytest.approx(O, rel=1e-13)
    f = m.f_single()
    assert f[1] == pytest.approx(1 - s * q * (1 - r * c) / (r * p + s * q), rel=1e-12)   # silence 1: O' = s q
    assert f[2] == pytest.approx(1 - (r * p / (1 - r * c)) / O, rel=1e-12)              # silence 2: O' = rp/(1-rc)
    assert f[3] == pytest.approx(r * c, rel=1e-12)                                       # silence T: feedback loss only
    assert f[0] == pytest.approx(1.0, rel=1e-13)                                         # positive control
    # serial chain: 0 -> 1 -> 2(T): f_1 = 1
    A2 = np.zeros((3, 3)); A2[1, 0] = 0.7; A2[2, 1] = 0.6
    m2 = P.LinModel(A2, [0], [2]); assert m2.f_single()[1] == pytest.approx(1.0)
    # equal parallel branches: f = 1/2 each, overlap 0, pair 1
    A3 = np.zeros((4, 4)); A3[1, 0] = A3[2, 0] = 0.5; A3[3, 1] = A3[3, 2] = 0.5
    m3 = P.LinModel(A3, [0], [3]); fa, fb, fab, ov = m3.f_pair(1, 2)
    assert (fa, fb, fab) == pytest.approx((0.5, 0.5, 1.0)) and ov == pytest.approx(0.0, abs=1e-14)


@pytest.mark.parametrize('seed', range(8))
def test_lin_sherman_morrison_and_woodbury_vs_direct(seed):
    rng = np.random.default_rng(seed)
    n = 25; S = [0, 1, 2]; T = [n - 1]
    A = rand_signed(n, 0.2, rng)
    m = P.LinModel(A, S, T)
    f = m.f_single()
    for k in range(n):                                    # every node incl. S and T
        assert 1 - m.O_direct([k]) / m.O == pytest.approx(f[k], abs=1e-10)
    for a, b in itertools.combinations(range(n), 2):      # rank-2 Woodbury
        assert m.f_set([a, b]) == pytest.approx(1 - m.O_direct([a, b]) / m.O, abs=1e-10)
    K = list(rng.choice(n, 6, replace=False))             # rank-m
    assert m.f_set(K) == pytest.approx(1 - m.O_direct(K) / m.O, abs=1e-10)
    assert m.f_set(S) == pytest.approx(1.0, abs=1e-12)    # silencing all of S
    assert f[S].sum() == pytest.approx(1.0, abs=1e-12)    # GRN shares sum to 1 (S rows are zero)
    fa, fb, fab, ov = m.f_pair(3, 4)
    assert ov == pytest.approx(fa + fb - fab)


def test_lin_sparse_input_equals_dense():
    rng = np.random.default_rng(1); n = 30
    A = rand_signed(n, 0.15, rng)
    m1 = P.LinModel(A, [0, 1], [29]); m2 = P.LinModel(sp.csr_matrix(A), [0, 1], [29])
    assert np.allclose(m1.f_single(), m2.f_single(), atol=1e-13) and m1.O == pytest.approx(m2.O)


def test_lin_negative_control_off_path_nodes():
    rng = np.random.default_rng(2); n = 20
    A = rand_signed(n, 0.25, rng)
    A[:, 15:] = 0; A[15:, :] = 0                          # 15..19: no edges at all
    A[16, 3] = 0.3                                        # 16 receives from the network but has no output
    A[3, 17] = 0.3                                        # 17 projects into the network but receives nothing
    m = P.LinModel(A, [0], [14])
    f = m.f_single()
    assert np.all(f[15:20] == 0.0)


def test_linear_response_equivalence():
    """f_k (walk-sum) == [response of T to removing k's output current a_k r_k] / [response to removing all S input],
    in the homogeneous linear model r = A r + u."""
    rng = np.random.default_rng(3); n = 25; S = [0, 1]; T = [24]
    A = rand_signed(n, 0.2, rng); A[S, :] = 0
    m = P.LinModel(A, S, T, u_S=[40.0, 55.0])
    r = m.x
    f = m.f_single()
    for k in range(2, n):
        a_k = A[:, k].copy()
        A2 = A.copy(); A2[:, k] = 0
        R2 = np.linalg.inv(np.eye(n) - A2)
        dO = -(R2 @ (a_k * r[k]))[T].sum()                # exact response of the silenced network
        assert dO == pytest.approx(-(m.ytil[k] * r[k] / m.diag[k]), abs=1e-10)
        A3 = A.copy(); A3[:, S] = 0
        dO_S = (np.linalg.inv(np.eye(n) - A3) @ m.u)[T].sum() - m.O
        assert dO / dO_S == pytest.approx(f[k], abs=1e-10)


# ------------------------------------------------------------------------------------------------- spectral radius / gmres
def test_spectral_radius_arpack():
    rng = np.random.default_rng(4); n = 800
    M = sp.random(n, n, density=0.01, random_state=5, data_rvs=lambda k: rng.uniform(-1, 1, k)).tocsr()
    rho, dev = P.spectral_radius(M)
    assert rho == pytest.approx(np.max(np.abs(np.linalg.eigvals(M.toarray()))), rel=1e-9) and dev < 1e-9


def test_gmres_matches_woodbury():
    rng = np.random.default_rng(6); n = 60; S = [0, 1, 2]; T = [59]
    A = rand_signed(n, 0.1, rng)
    m = P.LinModel(sp.csr_matrix(A), S, T)
    O, res = P.gmres_O(sp.csr_matrix(A), S, T, 1.0)
    assert O == pytest.approx(m.O, rel=1e-10)
    O2, _ = P.gmres_O(sp.csr_matrix(A), S, T, 1.0, removed_cols=[5, 9])
    assert O2 == pytest.approx(m.O_minus([5, 9]), rel=1e-9)


# ------------------------------------------------------------------------------------------------- walks
def brute_walks(n, edges, S, T, L):
    adj = [[] for _ in range(n)]
    for a, b in edges: adj[a].append(b)
    through = np.zeros(n, np.int64); visits = np.zeros(n, np.int64); total = 0
    def dfs(path):
        nonlocal total
        if len(path) - 1 >= 1 and path[-1] in T:
            total += 1
            for v in set(path): through[v] += 1
            for v in path: visits[v] += 1
        if len(path) - 1 == L: return
        for b in adj[path[-1]]: dfs(path + [b])
    for s in S: dfs([s])
    return through, visits, total


@pytest.mark.parametrize('seed', range(6))
def test_walk_counts_bruteforce(seed):
    rng = np.random.default_rng(seed); n = 12
    E = [(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.25]
    S, T = [0, 1], [11]
    M = P.csr_out(n, [e[0] for e in E], [e[1] for e in E])
    for L in (3, 4, 5):
        th, vi, tot = P.walk_counts_through(M, S, T, L)
        bth, bvi, btot = brute_walks(n, E, S, T, L)
        assert tot == btot and np.array_equal(vi, bvi) and np.array_equal(th, bth)


def test_walk_counts_hand():
    # 0 -> 1 -> 2(T), 0 -> 2, 1 -> 1? (no self loops) ; cycle 1 -> 3 -> 1
    E = [(0, 1), (1, 2), (0, 2), (1, 3), (3, 1)]
    M = P.csr_out(4, [a for a, b in E], [b for a, b in E])
    th, vi, tot = P.walk_counts_through(M, [0], [2], 4)
    # walks: 0-2, 0-1-2, 0-1-3-1-2 -> total 3; through 1: 2 walks; visits 1: 1 + 2 = 3; through 3: 1
    assert tot == 3 and th[1] == 2 and vi[1] == 3 and th[3] == 1 and th[0] == 3 and th[2] == 3


# ------------------------------------------------------------------------------------------------- hop distances
def test_bfs_dist_vs_networkx():
    rng = np.random.default_rng(7); n = 40
    E = [(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.06]
    M = P.csr_out(n, [e[0] for e in E], [e[1] for e in E])
    d = P.bfs_dist(M, [0, 3])
    G = nx.DiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
    ref = nx.multi_source_dijkstra_path_length(G, {0, 3})
    for v in range(n):
        assert (d[v] == ref[v]) if v in ref else np.isinf(d[v])


# ------------------------------------------------------------------------------------------------- max-flow
def test_flow_hand():
    # S={0,1} -> 2 (cap 5), 1 -> 3 (cap 2), 2 -> 4(T) (cap 4), 3 -> 4 (cap 7):  MF = 4 + 2 = 6
    pre, post, cap = [0, 1, 2, 3, 1], [2, 3, 4, 4, 2], [5, 2, 4, 7, 1]
    fm = P.FlowModel(5, pre, post, cap, [0, 1], [4])
    mf, f, _ = fm.f_all()
    assert mf == 6
    assert f[2] == pytest.approx(1 - 2 / 6) and f[3] == pytest.approx(1 - 4 / 6)
    assert f[0] == pytest.approx(0.5)                # without 0: 1->2->4 (1) + 1->3->4 (2) = 3
    assert f[1] == pytest.approx(1 / 3)              # without 1: 0->2->4 = 4
    assert f[4] == 0.0                               # silencing T: readout intact
    assert fm.f_set([0, 1]) == 1.0


def _nx_mf(n, pre, post, cap, S, T, removed=()):
    G = nx.DiGraph(); G.add_nodes_from(range(n + 2))
    for a, b, c in zip(pre, post, cap):
        if a in removed: continue
        G.add_edge(a, b, capacity=c)
    for s in S: G.add_edge(n, s)                      # no capacity attr = infinite
    for t in T: G.add_edge(t, n + 1)
    return nx.maximum_flow_value(G, n, n + 1)


@pytest.mark.parametrize('seed', range(6))
def test_flow_vs_networkx_and_shortcut(seed):
    rng = np.random.default_rng(seed); n = 18
    E = [(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.18]
    pre = [a for a, b in E]; post = [b for a, b in E]; cap = rng.integers(1, 20, len(E)).tolist()
    S, T = [0, 1, 2], [17]
    for backend in ('scipy', 'nx'):
        fm = P.FlowModel(n, pre, post, cap, S, T, backend=backend)
        mf, f, _ = fm.f_all()
        ref = _nx_mf(n, pre, post, cap, S, T)
        assert mf == ref
        for k in range(n):
            exp = 0.0 if k in T else 1 - _nx_mf(n, pre, post, cap, S, T, removed={k}) / ref
            assert f[k] == pytest.approx(exp, abs=1e-12)
        assert fm.f_set(S) == pytest.approx(1.0)


# ------------------------------------------------------------------------------------------------- dominators / cuts
def _brute_cuts(n, E, S, T):
    G = nx.DiGraph(); G.add_nodes_from(range(n + 1)); G.add_edges_from(E); G.add_edges_from((n, s) for s in S)
    out = []
    for k in range(n):
        if k == T: continue
        H = G.copy(); H.remove_node(k)
        if not nx.has_path(H, n, T): out.append(k)
    return out


@pytest.mark.parametrize('seed', range(10))
def test_dominators_three_ways(seed):
    rng = np.random.default_rng(seed); n = 16
    E = [(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.12]
    E += [(0, 5), (5, 9), (9, 15)]                    # ensure a path
    E = sorted(set(E))
    pre = np.array([a for a, b in E]); post = np.array([b for a, b in E])
    S, T = [0, 1], 15
    d_ig = P.dominators_of_T(n, pre, post, S, T, 'igraph')
    d_nx = P.dominators_of_T(n, pre, post, S, T, 'networkx')
    vc = P.VertexCut(n, pre, post, S, [T], uncut=[T])   # T itself is not a cut (silencing semantics)
    cuts_mf = vc.cut_nodes_single(exhaustive=True)
    cuts_fast = vc.cut_nodes_single()
    brute = _brute_cuts(n, E, S, T)
    by_path = P.cut_nodes_by_path(P.csr_out(n, pre, post), S, T)
    assert d_ig == d_nx == cuts_mf == cuts_fast == brute == by_path


def test_dominator_hand():
    # 0(S) -> 1 -> 2 -> 4(T); 1 -> 3 -> 4 : dominator {1}; 1(S2) adds nothing
    E = [(0, 1), (1, 2), (2, 4), (1, 3), (3, 4)]
    pre = np.array([a for a, b in E]); post = np.array([b for a, b in E])
    assert P.dominators_of_T(5, pre, post, [0], 4) == [0, 1]   # the single source itself dominates
    assert P.dominators_of_T(5, pre, post, [0, 2], 4) == []  # second source bypasses 1 via 2 -> 4


@pytest.mark.parametrize('seed', range(8))
def test_all_min_cuts_bruteforce(seed):
    rng = np.random.default_rng(seed); n = 13
    E = sorted(set((a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.2))
    pre = np.array([a for a, b in E]); post = np.array([b for a, b in E])
    S, T = [0, 1], [12]
    vc = P.VertexCut(n, pre, post, S, T, uncut=S + T)
    k0, cuts, complete = vc.all_min_cuts()
    k0e, cutse, _ = vc.all_min_cuts(exhaustive=True)
    G = nx.DiGraph(); G.add_nodes_from(range(n + 1)); G.add_edges_from(E); G.add_edges_from((n, s) for s in S)
    if not nx.has_path(G, n, 12):
        assert k0 == 0; return
    direct = any(G.has_edge(s, 12) for s in S)
    if direct:
        assert k0 >= vc.BIG; return
    cuttable = [v for v in range(n) if v not in S + T]
    best = None; found = []
    for size in range(1, len(cuttable) + 1):
        for C in itertools.combinations(cuttable, size):
            H = G.copy(); H.remove_nodes_from(C)
            if not nx.has_path(H, n, 12): found.append(C)
        if found: best = size; break
    assert k0 == best and sorted(cuts) == sorted(found) == sorted(cutse) and complete


def test_uncuttable_path_detected():
    E = [(0, 1), (1, 2)]                               # S={0}, uncuttable 1, T={2}
    vc = P.VertexCut(3, np.array([0, 1]), np.array([1, 2]), [0], [2], uncut=[0, 1, 2])
    assert vc.kappa() >= vc.BIG


# ------------------------------------------------------------------------------------------------- L0
def test_pagerank_igraph_networkx_power():
    rng = np.random.default_rng(8); n = 60
    E = sorted(set((a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.05))
    pre = np.array([a for a, b in E]); post = np.array([b for a, b in E]); w = rng.integers(1, 30, len(E)).astype(float)
    g = P.igraph_from_edges(n, pre, post)
    pr_ig = np.array(g.pagerank(weights=w.tolist(), damping=0.85, directed=True))
    pr_pw, _ = P.pagerank_power(n, pre, post, w)
    G = nx.DiGraph(); G.add_nodes_from(range(n)); G.add_weighted_edges_from(zip(pre, post, w))
    ref = nx.pagerank(G, alpha=0.85, weight='weight', tol=1e-14, max_iter=10000)
    pr_nx = np.array([ref[i] for i in range(n)])
    assert np.allclose(pr_ig, pr_nx, atol=1e-9) and np.allclose(pr_pw, pr_nx, atol=1e-9)


def test_betweenness_full_sample_is_exact_and_coreness():
    rng = np.random.default_rng(9); n = 40
    E = sorted(set((a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.08))
    pre = np.array([a for a, b in E]); post = np.array([b for a, b in E])
    g = P.igraph_from_edges(n, pre, post)
    est, per = P.sampled_betweenness(g, n, n, seed=0, batches=4)
    G = nx.DiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
    ref = nx.betweenness_centrality(G, normalized=False)
    assert np.allclose(est, [ref[i] for i in range(n)], atol=1e-9)
    core = nx.core_number(G)
    assert list(g.coreness(mode='all')) == [core[i] for i in range(n)]


def test_betweenness_estimator_unbiased():
    rng = np.random.default_rng(10); n = 50
    E = sorted(set((a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.07))
    g = P.igraph_from_edges(n, np.array([a for a, b in E]), np.array([b for a, b in E]))
    exact = np.array(g.betweenness(directed=True))
    ests = np.array([P.sampled_betweenness(g, n, 10, seed=s, batches=2)[0] for s in range(3000)])
    assert np.abs(ests.mean(0) - exact).max() < 0.05 * exact.max()


# ------------------------------------------------------------------------------------------------- L2 helpers
def test_lam50_and_interp():
    lam = np.array([0., 10., 20., 30.]); O = np.array([0., 2., 6., 8.])
    l50, Omax, i = P.lam50(lam, O)
    assert (l50, Omax, i) == (15.0, 8.0, 2)
    Rm = np.array([[0., 1.], [2., 3.], [4., 5.], [6., 7.]])
    assert np.allclose(P.interp_rates(lam, Rm, 15.0), [3., 4.]) and np.allclose(P.interp_rates(lam, Rm, 20.0), [4., 5.])


def test_empirical_gains_hand():
    # neuron 2 receives from 0 (exc, 10 syn) and 1 (inh, 4 syn); W in mV
    W = sp.csr_matrix(np.array([[0, 0, 0], [0, 0, 0], [10 * 0.275, -4 * 0.275, 0]]))
    r_a = np.array([100., 20., 5.]); r_b = np.array([110., 20., 9.])
    D, info = P.empirical_gains(W, r_a, r_b, active=np.array([False, True, True]))
    dmu = P.TAU_S * 10 * 0.275 * 10           # = 0.1375 mV
    assert D[2] == pytest.approx(4 / dmu) and D[0] == 0 and D[1] == 0 and info['n_dmu_zero'] == 1


@pytest.mark.parametrize('seed', range(8))
def test_min_cut_members_vs_enumeration(seed):
    rng = np.random.default_rng(100 + seed); n = 14
    E = sorted(set((a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.2))
    pre = np.array([a for a, b in E]); post = np.array([b for a, b in E])
    S, T = [0, 1], [13]
    vc = P.VertexCut(n, pre, post, S, T, uncut=S + T)
    k0, cuts, complete = vc.all_min_cuts(exhaustive=True)
    k1, memb = vc.min_cut_members()
    k2, memb_ex = vc.min_cut_members(exhaustive=True)
    assert k0 == k1 == k2
    if 0 < k0 < vc.BIG:
        assert sorted(set(v for c in cuts for v in c)) == memb == memb_ex
