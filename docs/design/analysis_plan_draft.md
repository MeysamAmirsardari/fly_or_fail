> **SUPERSEDED (2026-11-03)** by `PROJECT_DESIGN.md` v1.0, the pre-registration. Kept for history only. Its notation (f_k = O_k/O) conflicts with the frozen notation, so do not use it.

# Analysis Plan: Building Blocks (PI draft v0.1)

_Independent of the literature outcome. Items marked `[pending ENG]` wait for feasibility numbers.
This becomes the pre-registered analysis plan once the research questions are fixed._

## A. Perturbation protocol

1. **Common random numbers (CRN).** Trial *t* uses Brian2 seed *t* in every condition, so the
   baseline and every perturbed condition receive identical Poisson input realizations.
   - Effects are estimated from **paired** differences, which removes input-noise variance from the contrast.
   - Unit of replication is the trial (seed); n_trials is set by a pilot power analysis `[pending ENG]`.
2. **Silencing** = zero all outgoing weights of the target neuron(s), as in the original `silence()`.
   This mimics synaptic-output block (closer to TNT than to Kir2.1 hyperpolarization, which also
   stops spiking; in this model the two are equivalent for downstream effects).
3. **Candidate set.** Neurons with ≥ 1 spike in ≥ 1 baseline trial at **any** tested drive level
   (the union over λ). Neurons that never spike have an effect of exactly 0, and that is reported
   analytically, not simulated.
   - **Exception:** under a perturbation, a silent neuron could be *disinhibited*. The candidate set
     is still correct because silencing a silent neuron does nothing. But simulations on a reduced
     subnetwork must include the downstream closure (Section F).
4. **Drive levels λ.** Poisson rates applied to the sugar GRNs. The grid is chosen from the baseline
   input–output curve: one level below the output threshold, about 3 levels across the rising
   phase, and 1–2 levels near saturation `[pending ENG]`.
   - **Recruitment control:** a random fraction p of GRNs at fixed λ (sucrose concentration recruits
     more GRNs as well as raising their rates).

## B. Outcome metrics

| Symbol | Definition | Notes |
|---|---|---|
| O(λ) | mean MN9 spike rate over 1 s (average of left and right MN9; each side also reported) | primary readout; robustness readouts: other proboscis motor neurons, if identifiable |
| f_k(λ) | O_k(λ)/O_0(λ), from paired trials | normalized output; f > 1 means suppressor |
| N_k(λ) | 1 − f_k(λ) | single-level necessity |
| "Necessary" | N_k ≥ 0.2 **and** the paired bootstrap 95% CI excludes 0 | pre-registered threshold; sensitivity analysis at 0.1 and 0.5 |
| "Abolishing" | f_k ≤ 0.1 at every λ tested | |
| λ50, O_max, slope | from a constrained sigmoid (Hill) fit of O(λ) per condition | phenotype classes {none, shift, gain-loss, abolition}, decision rules fixed before running |
| ε_ab | f_ab − f_a·f_b (primary); additive, min and λ50-based (secondary) | pairwise interaction |

## C. Predictors (pre-registered list)

All predictors are computed **without** using any perturbation outcome.

- **L0, global:**
  - in/out degree and in/out strength (synapse counts)
  - PageRank and eigenvector centrality on the full v783 graph
  - betweenness (exact on the SEZ subgraph, or sampled whole-brain; the method is stated)
  - k-core index
  - rich-club membership (if a published definition is available)
- **L1, task-specific topology:**
  - hop distance from S (sugar GRNs) and to T (MN9)
  - S→T path counts through *k* with length ≤ L (matrix products)
  - signed walk-sum influence (α sweep; α = 1/ρ(W)·0.9 as default)
  - S–T betweenness
  - full-graph S–T max-flow loss ΔF_k (capacity = excitatory synapse count)
  - dominator status
  - probabilistic-traversal layer (Schlegel et al. 2021 method, pending LIT-B verification)
- **L2, operating point:**
  - baseline rate r_k(λ) **(the activity baseline every structural predictor must beat)**
  - linear response at the baseline, with calibrated gains
  - active-subgraph max-flow loss
  - cut/dominator status in the sufficient-edge graph
  - local necessity ratios propagated to T
- **L3, mean-field rate model:** the predicted f_k from fixed-point iteration with the calibrated φ.

## D. Statistical tests

1. **Association.** Spearman ρ(predictor, N_k) and AUPRC and AUROC for "necessary" (AUPRC is
   primary because of class imbalance), at each λ.
2. **Uncertainty.** Grouped bootstrap that resamples **cell types** (FlyWire annotation), because
   left–right homologs and cell-type members are near-duplicates. 2,000 resamples, percentile CIs.
3. **Incremental value of each rung.** Nested models (logistic regression for "necessary", rank
   regression for N_k) with grouped 5-fold cross-validation, folds split by cell type. Report ΔAUPRC
   for L0 → L1 → L2 → L3 with grouped-bootstrap CIs.
4. **Crossover (P1).** Δ(λ) = AUPRC_cut(λ) − AUPRC_flow(λ). Test a monotone increasing trend in λ:
   bootstrap the slope of Δ on log λ; one-sided, as pre-registered. Robustness: restrict to a
   **fixed neuron set** (active at all λ) so that changes in the active set cannot explain the trend.
5. **Flow-fraction law (P2).** Regress log(λ50′/λ50) on −log(1 − f̂_k) over the neurons with a
   shift phenotype. H0: slope = 1, intercept = 0 (equivalence test with a pre-set margin ±0.2),
   plus a Deming regression variant because f̂_k has error.
6. **Epistasis (P3).** Stratified pair sample by structural class (parallel-converging, serial,
   non-converging, Menger 2-cut). Planned contrasts:
   - ε(parallel) < 0
   - ε(serial) ≥ 0, with f_ab ≈ min
   - ε(non-converging) ≈ 0 (equivalence)

   Permutation test of class labels within strata of single-effect magnitude, to control for the
   ceiling and floor dependence of ε on f_a and f_b.
7. **Multiplicity.** At most 6 primary confirmatory tests, Holm-corrected. Everything else is
   labelled exploratory.

## E. Controls and robustness

- **Positive controls:** silence all sugar GRNs (expect abolition); silence the top direct
  excitatory inputs of MN9.
- **Negative controls:** silence random neurons with no S→T path (expect exactly 0, which validates
  the pipeline).
- **Reproduction:** match the stored outputs of the original authors (ENG) before any new run.
- **Parameter robustness:**
  - w_syn × {0.8, 1.2}
  - synapse threshold ≥ 5 vs ≥ 10
  - neurotransmitter signs flipped for low-confidence predictions (if confidence is available)
  - v783 vs v630

  Report Kendall τ of the N_k ranks and the stability of every primary conclusion.
- **Internal replication:** stimulate left vs right sugar GRNs and compare N_k of mirror homolog
  pairs. This measures sensitivity to idiosyncratic wiring within one animal.
- **Circularity control:** each structural predictor is also evaluated against L3 and L4. A predictor
  "explains" necessity only when it beats the activity baseline r_k and distance to output.

## F. Simulation engineering (only if Brian2 is too slow) `[pending ENG]`

- **Build once, reuse:** Brian2 `store()`/`restore()`, varying only the silenced weights and the seed.
- **Exact subnetwork reduction:** simulate active set A ∪ out-neighbours(A). After each perturbed
  run, if a neuron in the boundary fired, expand and re-run. Validate the reduced model against the
  full model on a random 5% of conditions; require identical spike trains under CRN, or report the deviation.
- **Fallback:** a vectorized event-driven re-implementation, accepted only if it matches Brian2 spike
  statistics on the reproduction tests.
