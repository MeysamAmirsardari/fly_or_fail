# STRUCTURAL PREDICTORS (STRUCT): definitions, derivations, verification

Pre-registration: `docs/design/PROJECT_DESIGN.md` v1.0, §6.4. Code: `analysis/predictors.py` (and `common.py` for
frozen IDs, `intact.py` for the intact curves). Tests: `analysis/tests/test_predictors.py`.

**Rule kept.** No silencing simulation was run, and no silencing outcome was read. The only simulation input is the
INTACT fastlif runs (`intact.py` asserts that no job carries a `silence` field).

<!--RESULTS-->

---

## 1. Inputs, readouts and conventions (frozen in `analysis/common.py`, asserted by `check_conventions()`)

| Item | Definition |
|---|---|
| Connectome | `Completeness_783.csv` + `Connectivity_783.parquet` (v783, primary); `2023_03_23_*_630_final` (v630). Index = completeness row order. Loader asserts: rows sorted by presynaptic index, no duplicate (pre, post) pairs, no self-loops, sign constant per presynaptic neuron, `Excitatory x Connectivity == Excitatory * Connectivity` |
| Edge sign | `Excitatory` (±1, per presynaptic neuron). Synapse count n_ij = `Connectivity` (≥ 1, no threshold) |
| S_shiu | `feasibility/ids/sugar_GRN_right.csv` (Shiu's notebook "right" list = annotation side "left"); IDs present in the version (v783: 20, v630: 21) |
| S_pure | v783 annotation `cell_sub_class ∈ {sugar, sugar/low_salt}` (LB3c, LB3b) with annotation side "left": 33 neurons (`out/S_pure_ids.csv`); present in v783: 33, in v630: 31. Only 11 overlap S_shiu |
| T_contra (primary) | MN9 `720575940660219265` (CB0701, annotation side "right" = contralateral to the GRNs) |
| T_ipsi (secondary) | v783: `720575940618238523` (CB0701, side "left"); v630: `720575940645521262` (per ENG) |
| MN9 handling | Every T-dependent quantity is computed for ONE readout. The two MN9s are never summed or averaged |
| Silencing semantics | Removing k's OUTGOING edges (model.py). For flows and cuts this equals removing k's in- and out-edges for every k ∉ T; for k = T the readout is untouched, so f^MF(T) = 0 and T is never counted as a cut |
| Sources | In every linear model, S nodes are exogenous sources: their incoming edges are dropped (rows of A set to 0) and the stimulus enters as u_S. Justification: stimulated GRNs are driven by 68.75 mV Poisson kicks with refractory 0, so their rate is set by λ (measured r_S/λ50 is reported in the summary JSON) |

Column naming in `predictors_<ver>.parquet`: S- or T-dependent columns carry the suffix `__<input>_<readout>`
(e.g. `fLIN_A__shiu_contra`); S-only columns `__<input>`; T-only columns `__<readout>`; L0 columns have no suffix.

---

## 2. L0: global, whole-brain graph (all 127,400 / 138,639 neurons; directed; no synapse threshold)

| Column | Exact definition |
|---|---|
| `in_degree`, `out_degree` | number of distinct presynaptic / postsynaptic partners |
| `in_strength`, `out_strength` | total input / output synapse count Σ n (out_strength = the Minnick 2026 competitor) |
| `total_degree` | in_degree + out_degree |
| `pagerank` | PageRank on the directed graph with transition weights ∝ n_ij (out-normalized), damping 0.85, dangling-node mass and teleport spread uniformly; power iteration to L1 change < 1e-13 (`pagerank_power`). Cross-checked against igraph/PRPACK and networkx (unit test; and igraph on a 20k-node induced subgraph of the real graph) |
| `betweenness` | Brandes shortest-path betweenness, unweighted, directed, endpoints excluded, **estimated from sampled sources**: B̂(v) = (n/k) Σ_{s∈sample} δ_s(v), with k uniform sources without replacement. Unbiased for B(v) = Σ_{s≠v≠t} σ_st(v)/σ_st (unit-tested: exact when k = n; mean over 3,000 resamples ≈ exact). Two independent replicates of k = 1,000 sources (seeds 20261103, 20261104), each split into 10 batches of 100; `betweenness` = mean of the two replicates (2,000 sources); `betweenness_se` = SD of the 20 batch estimates / √20; `betweenness_rep1/2` kept for the re-sample comparison |
| `kcore_total` | k-core index (coreness) using total degree (in + out; a reciprocal pair counts 2), igraph `coreness(mode='all')`; equals networkx `core_number` on DiGraph (unit test) |
| `rich_club_deg37` | total_degree > 37. **Lin et al. 2024 is reported (UNVERIFIED) to place the rich-club regime at degree > 37; the threshold is used as stated, not verified** |
| `neg_hop_to_T__<ro>` | −(hop distance to T on the full directed graph): the pre-registered distance competitor |

---

## 3. L1: task topology (structure only)

### 3.1 Hop distances
`hop_from_S_{all,exc}__<inp>` = min over s ∈ S of the directed hop distance s → k; `hop_to_T_{all,exc}__<ro>` =
hop distance k → T. `all` = full directed graph, `exc` = only edges whose presynaptic neuron is excitatory.
Unreachable = +inf. (Multi-source BFS; unit-tested against networkx.)

### 3.2 Walk counts (L = 5)
Unweighted, unsigned full graph, adjacency M (M_uv = 1 for an edge u → v). These are **walks** (vertices and edges may
repeat), not paths. A walk is counted once per (start s ∈ S, vertex sequence, end t ∈ T), with length 1..5.

- N_i(k) = #walks S → k of length i = ((Mᵀ)^i 1_S)_k, B_j(k) = #walks k → T of length j = (M^j 1_T)_k (exact int64).
- `walk_visits_L5` = Σ over walks of the number of positions at k = Σ_{i+j ≤ 5, i+j ≥ 1} N_i(k) B_j(k).
- `walks_through_L5` = number of walks that visit k **at least once**. First-passage decomposition: with
  C_t(k) = (M^t)_kk the closed-walk counts, the renewal identity N_i = Σ_{m ≤ i} F_m C_{i−m} gives the first-passage
  counts F_m, and through(k) = Σ_i F_i(k) Σ_{j ≤ 5−i} B_j(k). Only C_t with t ≤ 5 − d(S,k) − d(k,T) are needed
  (here t ≤ 3).
- Both verified against brute-force walk enumeration on random graphs (L = 3, 4, 5), and `walks_through_L5(T)` equals
  the total walk count (stored check).

### 3.3 f^LIN-S: walk-sum transmission fraction (structure only)

**Subgraph.** The corridor V_5 = {v : d(S,v) + d(v,T) ≤ 5} of the full signed graph (all nodes lying on some S→T walk
of length ≤ 5), with **all** edges among them (recurrent loops inside V_5 are kept; walks inside V_5 have unbounded
length). Reason: the exact "reachable-from-S and co-reachable-to-T" set is the whole giant SCC (≈ 126k / 135k nodes),
on which the diagonal of the resolvent cannot be computed exactly in the time available; V_5 has ≈ 13.6k nodes
(dense exact inverse). Neurons outside V_5 get f^LIN-S = 0. **Flag:** this corridor choice is a definition.

**Matrix.** Ŵ_ij = s_j n_ij / Σ_{j'} n_ij' (signed synapse count normalized by the postsynaptic neuron's
**whole-brain** total input synapse count), restricted to V_5, rows of S set to 0. α = 0.9/ρ(Ŵ) with ρ the spectral
radius of that matrix (ARPACK, two random starts, agreement reported). A = αŴ, R = (I − A)⁻¹, u = 1_S.

**Transmission.** x = R u (node responses), O = 1_Tᵀ R u. Because u lives on S, S ∩ T = ∅ and RA = R − I,
O = 1_Tᵀ R A 1_S (the form in the brief).

**Exact single deletion (Sherman–Morrison).** Silencing k removes column k: A′ = A − a_k e_kᵀ with a_k = A e_k, so
I − A′ = (I − A) + a_k e_kᵀ and

  R′ = R − R a_k e_kᵀ R / (1 + e_kᵀ R a_k),  with 1 + e_kᵀ R a_k = 1 + (RA)_kk = R_kk.

Hence O_{−k} = O − (1_Tᵀ R a_k)(e_kᵀ R u)/R_kk = O − ỹ_k x_k / R_kk, where ỹ = Aᵀ Rᵀ 1_T (ỹ_k = 1_Tᵀ R A e_k:
transmission from k's output to T), and

  **f_k = 1 − O_{−k}/O = ỹ_k x_k / (R_kk O).**

Interpretation: x_k = walk-sum from S to k, ỹ_k = walk-sum from k's output to T, 1/R_kk removes the double counting of
walks that revisit k. f_k < 0 is allowed (silencing a neuron on a net-inhibitory route increases O: disinhibition).

**Sets and pairs (Woodbury).** For a set K: I − A′ = (I − A) + A E_K E_Kᵀ, and I + E_Kᵀ R A E_K = R_KK, so

  O_{−K} = O − ỹ_Kᵀ (R_KK)⁻¹ x_K,   f_K = 1 − O_{−K}/O.

Pairs: f_ab = f_{a,b} (rank 2), overlap f_{a∧b} = f_a + f_b − f_ab (`LinModel.f_pair`, and
`predictors.pair_fractions(ver, inp, ro, pairs)` for the later pre-registered pair list).

**Positive control (exact).** S rows are zero, so R_SS = I and x_S = 1: O_{−S} = O − Σ_s ỹ_s = 0, i.e. f_S = 1; and
Σ_{s∈S} f_s = 1 exactly (each GRN's f is its share of the linear S output).

**Verification.** Unit tests: Sherman–Morrison vs direct recomputation for every node of random signed graphs
(incl. S and T), Woodbury rank-2 for all pairs and rank-6 sets, hand-computed 4-node examples (parallel routes with
feedback; serial chain f = 1; equal parallel branches f = ½, overlap 0). Real data: dense values vs an independent
sparse GMRES solve (rtol 1e-13) of the column-deleted system for 16 nodes per (input, readout), one pair, every
external type set, and all of S (results in §R).

### 3.4 f^MF-S: excitatory max-flow fraction
Excitatory corridor V^exc_5 = {v : d_exc(S,v) + d_exc(v,T) ≤ 5}, excitatory edges among V^exc_5, integer capacities
n_ij, super-source → each s ∈ S and T → super-sink with capacity "∞" (= total capacity + 1). MF by scipy
`maximum_flow` (Dinic, int32). **f_k = 1 − MF(G minus k's out-edges)/MF(G).**
Exact shortcut: if some maximum flow sends zero flow through k, that flow survives the deletion, so f_k = 0; only
nodes with positive throughput in the computed max flow are recomputed. Verified: unit tests vs networkx for every
node of random graphs (both backends) and a hand example; real data: networkx preflow-push MF(G) and the two largest
f_k recomputed independently.

### 3.5 Dominators / single-vertex cuts
k is a single-vertex S→T cut iff every path from a super-source (edges to all of S) to T passes through k, i.e. k is
a strict dominator of T in the flow graph rooted at the super-source. Computed three ways and cross-checked:
(i) Lengauer–Tarjan dominator tree (igraph `dominator`), (ii) networkx `immediate_dominators`
(Cooper–Harvey–Kennedy), (iii) unit-node-capacity max-flow (node splitting): MF drops to 0 when k is removed
(only positive-throughput nodes need testing). On the whole-brain graphs (too large for networkx/node-split
enumeration) (ii)+(iii) are replaced by a direct reachability test of every node of one shortest S→T path (every
cut lies on every path). T is excluded (silencing semantics). Graph variants (red-team M3): whole-brain unsigned
(`dominator_all`), whole-brain excitatory (`dominator_exc`), excitatory corridor V^exc_5 (`dominator_exc_L5`), and the
excitatory **active** graph at λ50 (`dominator_active`, §4.5).

---

## 4. L2: activity-aware (INTACT simulations only)

### 4.1 Intact curves (`analysis/intact.py`)
fastlif on the exact closure network (sim/reduce.py `run_exact`, runtime boundary check, automatic exact expansion,
closure not persisted), salt 0, 1-s trials, λ = 0, 5, …, 400 Hz (81 levels) × seeds 0–59, for each version and
input set. Output `out/intact_curve_<ver>_<inp>.npz`: `lam`, `seeds`, `mn9_contra_rates` and `mn9_ipsi_rates`
(n_lam × 60, spikes/s per seed), `mean_rates` (n_lam × n_closure, per-neuron mean over seeds), `fid`/`gidx` of the
closure, `active_counts` (per-seed counts of every neuron that spiked anywhere), metadata (fastlif/reduce md5).
Neurons outside the final closure are exactly silent (reduction theorem), so their rate is 0.

### 4.2 λ50 and rates
O(λ) = mean over the 60 seeds of the readout's spike count. O_max = max over the grid of the mean curve.
λ50 = first upward crossing of 0.5·O_max, linear interpolation between the bracketing grid levels
λ_a < λ50 ≤ λ_b (PROJECT_DESIGN §3). λ_ref = λ50 (per input and per readout). `rate_lam50` = per-neuron mean rate
linearly interpolated at λ50. "Active at λ50" ⇔ rate_lam50 > 0.

### 4.3 Empirical gains
μ_i(λ) = τ_s Σ_j W_ij r_j(λ), τ_s = 5 ms, W_ij = s_j n_ij · 0.275 mV, r = mean rates (all presynaptic neurons in the
closure; neurons outside are silent). **D_i = (r_i(λ_b) − r_i(λ_a)) / (μ_i(λ_b) − μ_i(λ_a))** in Hz/mV, the finite
difference between the grid levels bracketing λ50. D_i = 0 if i is inactive at λ50, if Δμ_i = 0 (counted), and for
i ∈ S (sources). Negative D (noise or non-monotone neurons) are kept as measured (counted); the variant
`fLIN_A_Dpos` uses max(D, 0).

### 4.4 f^LIN-A
A_ij = τ_s D_i W_ij on the node set (active at λ50) ∪ S ∪ T, S rows 0, u_S = r_S(λ50). No α scaling, as specified. ρ(A) and max Re λ(A) are reported: the
Woodbury formulas are exact algebra whenever I − A is invertible, and (I − A)⁻¹ is the exact steady-state linear
response when the linearization is stable (max Re λ < 1); the *walk-sum* (Neumann series) reading additionally needs
ρ(A) < 1. **FLAG:** with empirical finite-difference gains ρ(A) can exceed 1 (it did in a coarse pilot), so f^LIN-A is
then a linear-response fraction, not a convergent walk sum.
Then exactly as §3.3: **f_k = ỹ_k x_k/(R_kk O)**, sets/pairs by Woodbury. Restricting to the active set is exact:
inactive rows are 0, so x = 0 there and they carry nothing (verified numerically by padding the model with 1,500
inactive closure neurons: identical f on active nodes, f = 0 on the padding).

**Equivalence (derived and verified).** In the linear model r = A r + u, silencing k changes the network to A′ and
(I − A′) r = u + a_k r_k, so the response to removing k's output current a_k r_k is
δO_k = −1_Tᵀ R′ a_k r_k = −ỹ_k r_k / R_kk (Sherman–Morrison: R′ a_k = R a_k/R_kk). Removing all S input gives
δO_S = −O. Hence f_k = δO_k/δO_S with r_k = x_k: **"linear response to removing k's output / linear response to
removing all S input" equals the walk-sum fraction.** Verified on random graphs (unit test) and on the real active
matrices (40 neurons per condition, by explicit solves). Variant `fLIN_A_r0` replaces the model rate x_k by the
simulated rate r_k(λ50) (the two differ because the LIF network is not homogeneous-linear); both are reported.

### 4.5 f^MF-A, active dominators and min-cut participation
Excitatory subgraph induced on (active at λ50) ∪ S ∪ T; capacity c_ij = n_ij · r_j(λ50) (synapse·Hz), stored as
round(1000·c_ij) integers and solved with networkx preflow-push (exact integer arithmetic). f as in §3.4.
`dominator_active`: dominators of T in this graph (super-source over S; **GRNs and T excluded**), three-way
cross-check as in §3.5.

**Min-cut participation (definition changed during implementation; FLAG for PI).** With unit capacity on every
non-S, non-T node (S and T uncuttable), κ(λ) = minimum S→T vertex-cut size of the excitatory active graph at λ.
Exact enumeration of all minimum cuts was implemented and unit-tested (a set P lies in some minimum cut iff
κ(G − P) = κ − |P|), but on the real active graph κ > 25 and the number of minimum cuts is combinatorially large, so
counting "cuts containing k" is infeasible (counting closures of the residual DAG is #P-hard). Pre-specified
replacement, exact and tractable:
- `in_min_vertex_cut_lam50`: k belongs to SOME minimum vertex cut at λ50 ⇔ κ(G − k) = κ − 1 (removing one vertex lowers
  κ by at most 1; only nodes with positive throughput in a maximum flow can qualify). Unit-tested against full
  enumeration.
- `mincut_participation`: **number of intact-grid levels λ (with mean readout rate > 0) at which k belongs to some
  minimum vertex cut** of the excitatory active graph at λ (0–81). This is the graded score for the monotone-trend
  analysis.
- `n_min_cuts_containing_lam50`: exact count of minimum cuts at λ50 containing k, only if the enumeration finished
  within 60 s (else NaN; completeness reported).

---

## 5. Set-level external types (`out/external_types_structural.csv`)
Types (all members silenced together): Rattle, Usnea, Zorro, Clavicle, G2N-1, FMIn, Phantom, Bract (Bract 1 + Bract 2 =
DNge173 + DNge174, 4 neurons), Fdg, Roundup. IDs from `Drosophila_brain_model/sez_neurons.pickle`. **Zorro** is not a
pickle key: Jacobs et al. 2024 STAR Methods (= Shiu & Sterne 2022 "Zorro R") give `720575940629888530`, present in
both versions and annotated `cell_type = CB0192` (side left); Zorro = all CB0192 neurons in the v783 annotation
(2: `720575940629888530`, plus its homolog). The Shiu 2022 "Zorro L" ID `720575940643219566` is absent from both
versions (outdated root ID). LIN-S/LIN-A by exact Woodbury (verified vs GMRES / direct solves), MF by direct
recomputation. Computed for S_shiu and S_pure, both readouts, both versions. Only structural values; no simulated
type-level f was computed or inspected.
