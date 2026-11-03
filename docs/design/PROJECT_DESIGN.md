# PROJECT DESIGN: Silencing as Input Rescaling

## Predicting the intensity-dependent consequences of neuron loss from connectome structure in a whole-brain *Drosophila* model

_Draft v0.9 (2026-11-03), for red-team review. Supporting documents:_
- _`docs/design/theory_note.md` (theory v0.2)_
- _`docs/research/*` (literature, ground truth, prior art, feasibility)_
- _`management/STRATEGY.md`_

_Evidence tags follow STRATEGY §5:_
- _`[V-abs]`: abstract or snippet seen this session;_
- _`[V-src]`: code or data inspected;_
- _`[MEM]`: unverified background knowledge._

_No paper full texts could be read from this environment, so every literature statement is at abstract level at best._

---

## 0. Executive summary

**Recommended research question.**
> Can one structurally estimable number per neuron predict the **whole stimulus-intensity-dependent
> consequence** of silencing it in a connectome-constrained brain model? The number is the fraction
> f_k of sensory→motor transmission the neuron carries. The consequences are: whether silencing
> abolishes the behaviour or only shifts its sensitivity, by how much, and how pairs of silenced
> neurons interact.

**Core idea (the "input-rescaling law").** If the motor readout depends on the stimulus and the
circuit mainly through one effective drive, then silencing neuron *k* is equivalent to weakening the
stimulus by the factor (1 − f_k): O_k(λ) = O((1 − f_k)λ). This one statement implies:
1. Silenced dose–response curves **collapse** onto the intact curve after rescaling the intensity axis.
2. The **EC50 shift** is 1/(1 − f_k).
3. **Abolition** happens exactly when the neuron is a source→target **vertex cut**.
4. Disinhibition gives **leftward** shifts.
5. Single-intensity "necessity" rankings must change with intensity. This explains, rather than
   asserts, the operating-point dependence built into Shiu et al.'s screens.
6. Pairwise interaction curves, including an intensity **window of synergy**, follow with no free
   parameters from f_a, f_b and their overlap.

**Why this question.**
- **It answers the student's question directly.** "To what extent can structure predict perturbation
  consequences?" becomes a quantitative decomposition with three parts:
  - **dynamics:** does the rescaling law hold?
  - **structure:** can f_k be estimated from the connectome, alone or with baseline activity?
  - **classical centrality:** does it carry any of this information?
- **It is positioned against the strongest prior art found.** The original authors already swept
  intensity in single-neuron silencing (Shiu et al. 2024 `[V-src]`). Pairwise synergy among
  second-order sugar neurons is reported (Jacobs et al. 2024 `[V-abs]`). Set-level min-cuts beat
  centrality in a non-peer-reviewed repo. **Not found** in our (abstract-level, budget-limited)
  searches:
  - the rescaling law;
  - curve-collapse testing;
  - structural prediction of the EC50 shift;
  - single-neuron abolition = vertex cut across intensities;
  - parameter-free prediction of pair interaction curves.
- **It is feasible.** Public data and model, roughly 60 CPU-hours of simulation for the minimum
  viable project (MVP). See §4 for measured costs.
- **It makes an experimentally testable prediction.** Silencing a neuron shifts the PER sucrose
  dose–response curve by a factor set by f_k. The mapping from sugar concentration to GRN rate is
  needed for the conversion. The EC50 ratio is invariant to any monotone link between MN9 rate and
  PER probability.

**MVP for 2026-12-10.**
- Sugar→MN9 circuit, FlyWire v783 (v630 for reproduction).
- Single-neuron silencing curves for the active set across about 8 intensities.
- Six structural estimators of f, plus classical-centrality and activity baselines.
- A pre-registered pilot of about 60 pairs.
- Left/right and v630/v783 robustness.

**Paper extension.**
- Full pair screen and synergy-window test.
- Water→MN9 and JON→descending-neuron tasks.
- Cross-connectome replication (BANC, male CNS: both available in a public bucket `[V-src]`).
- Analytic theory of when the scalar-drive approximation holds.
- Concrete PER dose–response predictions for experimental collaborators.

---

## 1. Literature assessment: what is established, what is open

Details, tags and URLs are in `docs/research/lit_A_connectome_models.md`, `lit_B_network_theory.md`,
`lit_C_ground_truth.md` and `novelty_prior_art.md`.

### 1.1 Established

| Claim | Evidence (closest sources) |
|---|---|
| A whole-brain LIF model built only from FlyWire synapse counts and predicted transmitter signs recovers sugar/water→MN9 and JO→grooming recruitment, with some experimental confirmation | Shiu et al. 2024 Nature `[V-abs]`. Model details `[V-src]`. The circulating "91% of 164 predictions" figure is unverified, so do not cite it |
| In that model, single-neuron silencing was swept over intensities: sugar 50–120 Hz (8 levels), water 160–220 Hz, JON 140–180 Hz, on the top 200 or 300 responders | `figures.ipynb` cells 12–14, 40–42, 58–60 `[V-src]`. An "≤ 80% at any frequency" criterion `[V-abs, snippet]` |
| Second-order sugar neurons act synergistically in the Shiu model; experimental single silencing is often negative | Jacobs et al. 2024 Cell Reports 43:114782 `[V-abs]`. The exact pair design is snippet-level only |
| Experimentally, only a subset of second-order neurons, and none of the third-order or premotor neurons tested, are individually required for sugar PER at one concentration in food-deprived flies | Shiu, Sterne et al. 2022 eLife (peer-review text) `[V-abs]` |
| Wiring beyond degree, sign and weight statistics matters: degree-preserving rewiring or weight shuffles abolish sugar→MN9 output | An 2026 bioRxiv `[V-abs]`; MLX-port shuffle control `[V-src, grey]`; Zhang et al. 2024 `[V-abs]` |
| A set-level S→T min-cut abolishes MN9; PageRank and out-strength sets do not (male CNS, Shiu-parameter LIF) | `fly-bottlenecks` repo `[V-src, grey]` |
| In the Shiu model, static path scores predict single-knockout effects (ρ = 0.70), rising to ρ = 0.81 when weighted by activity (n = 21) | StrokeSim repo `[V-src, grey]` |
| Linear-response / resolvent measures track LIF activity better than degree or betweenness | Fletcher & Wennekers 2016 `[V-abs]`; Trousdale et al. 2012 `[V-abs]` (operating-point dependence) |
| Lesion effects in network models depend on structure but only partly. Single-lesion inference is biased under redundancy, and multi-perturbation (Shapley) attribution is the axiomatic remedy | Alstott et al. 2009; Keinan et al. 2004; Fakhar & Hilgetag `[V-abs]` |
| Neuron pairs framed as "synthetic essential" (synthetic-lethality analogue), and flow-based double ablations | C. elegans: Towlson & Barabási 2020; Bacik et al. 2016 `[V-abs]` |
| The choice of interaction definition (neutrality function) changes which pairs "interact" | Mani et al. 2008 PNAS `[V-abs]` |
| Anatomy alone poorly predicts measured perturbation propagation in a real nervous system | Randi et al. 2023 Nature (C. elegans) `[V-abs]` |

### 1.2 Open (our opportunity), with pre-emption risk

| Gap | Risk | Why |
|---|---|---|
| Whether one scalar per neuron (f_k) captures the **whole** intensity-dependent silencing phenotype (collapse), and where it fails | Low–medium | No prior art found for curve collapse or the rescaling law in neural circuits. The pharmacology analogue (receptor reserve) exists and will be cited |
| Structural estimation of f_k: which compression of W suffices (topology only vs + baseline activity), versus classical centrality | Medium | StrokeSim and fly-bottlenecks are close but grey, n = 21 or set-level. Fletcher 2016 is about activity, not necessity |
| Single-neuron abolition = vertex cut, tested across intensities | Low–medium | Set-level analogue exists (grey) |
| Parameter-free prediction of pairwise interaction curves; intensity-dependent synergy window | Low | Pairs exist descriptively (Jacobs 2024, Chen 2025, arXiv 2610.33881). No interaction-curve theory found |
| Replication of necessity across hemispheres, connectome versions and animals | Medium | Cross-connectome running exists in grey repos. No systematic necessity-reproducibility study found |
| Experimental test of dose–response under silencing | n/a | No published PER dose–response-under-silencing data found (LIT-C §2). This is a **prediction to offer**, not something we can validate |

**Coverage caveat.** Both literature tools hit their quotas during the search. WebSearch hit the
shared budget; Consensus is out of free credits until 2026-12-01. The dominator/articulation-point
query was never run. Absence claims are therefore *weaker than usual*, and the student should re-run
§1.2's checks with full-text access (Google Scholar "cited by" on Shiu 2024 and Jacobs 2024) before
writing the proposal's novelty sentence.

---

## 2. Novelty assessment (candidate directions)

| Candidate | Closest prior art | Verdict | Keep as |
|---|---|---|---|
| H-A: centrality < flow < linear response for single-neuron necessity | StrokeSim (grey), fly-bottlenecks (grey, set-level), Fletcher 2016, Pospisil 2024 | **Incremental** | Baseline section (RQ1). Required to answer the student's question, but not the headline |
| H-B as originally phrased: "necessity is operating-point dependent" | Shiu 2024 design (intensity sweeps, any-rate rule); possibly an explicit statement in Shiu's text (unverified snippet) | **Not novel** | Dropped as a claim. Re-derived as consequence C5 of the rescaling law |
| H-B sharpened: rescaling law, curve collapse, EC50-shift law, abolition = cut | Receptor reserve (pharmacology analogy); Shiu sweeps (data type) | **Apparently novel** (abstract-level search) | **Core (RQ2, RQ3)** |
| H-C as originally phrased: "neural epistasis", between/within pathway | Towlson & Barabási 2020; Jacobs 2024; Bacik 2016; Kelley & Ideker 2005 | **Not novel as framing** | Dropped as framing. "Serial pairs mask" is near-tautological in a no-background threshold model, so it is used only as a sanity control |
| H-C sharpened: parameter-free interaction curves and synergy windows from flow fractions | Jacobs 2024 (pairs, descriptive); Phenix 2011 (signal-dependent epistasis, genetics) | **Apparently novel** | Pilot in MVP; full in paper (RQ4) |
| H-D: task specificity of necessity | Shiu 2024 ran both sugar and water screens; Jacobs 2024 (overlap and divergence) | **Incremental** | Generalization test (RQ5) |
| H-E: experimental validation and cross-connectome reproducibility | Yan 2017 (worm), Shiu 2024 (small validation), grey cross-connectome ports | **Partially novel, power-limited** | Validation layer (RQ5). The experimental part is qualitative only (about 6–10 labelled types) |

---

## 3. Research questions, hypotheses, predictions, limitations

Notation:
- λ: GRN Poisson rate (stimulus intensity).
- O(λ): intact MN9 rate curve.
- O_k(λ): MN9 rate with *k* silenced.
- f_k: transmission fraction.
- S: sugar GRNs (input). T: MN9 (output).

### RQ1 (baseline). Does classical structural importance predict functional necessity?

- **H1.** Global centralities (degree, strength, betweenness, PageRank, rich-club membership) predict
  single-neuron necessity N_k(λ) = 1 − O_k(λ)/O(λ) worse than task-specific S→T measures. Their
  ranking accuracy is unstable across λ.
- **Prediction.** AUPRC for "necessary" (N_k ≥ 0.2) is near the base rate for global centrality,
  substantially higher for S→T measures, and highest with baseline activity included. Centrality's
  ρ with N_k changes sign or magnitude across λ.
- **Falsifier.** Centrality matches S→T measures within CI at the reference intensity.
- **Limitations.**
  - Partly circular, because the model is built from W (§5.7).
  - The answer is "known in spirit" (grey precedents).
  - Its value is the clean, pre-registered quantification with grouped cross-validation and nulls.

### RQ2 (core: dynamics). Is silencing equivalent to weakening the stimulus?

- **H2.** For most neurons with a detectable effect, O_k(λ) = O((1 − f_k)λ) (pure shift).
  Deviations (gain loss) concentrate in neurons downstream of saturating convergence.
  Abolition occurs only for f_k → 1.
- **Prediction.**
  - Model comparison (shift vs shift + gain) favours shift-only for the majority (pre-registered
    criterion in §5.6).
  - Collapse residuals are within trial noise.
  - Inhibitory route neurons show f_k < 0 (leftward shifts).
- **Falsifier.** Shift-only is preferred for fewer than half of the effect-bearing neurons, or
  residuals systematically exceed the noise.
- **Limitations.**
  - This is a property of *this model*. It says nothing yet about real flies.
  - The intensity range is bounded by physiology; λ above about 300 Hz is flagged as non-physiological.

### RQ3 (core: structure). Can f_k be estimated from the connectome, and how much does baseline activity add?

- **H3.** Flow-fraction estimators computed without any perturbation simulation predict the
  empirical f_k. The estimators are linear-response fractions and max-flow fractions; the
  activity-aware versions use only the intact simulation.
  - f^LIN-A and f^MF-A outperform:
    - (a) global centrality,
    - (b) the neuron's baseline rate,
    - (c) distance to the output.
  - Activity-aware estimators outperform structure-only ones, and the structure-only ones still
    beat centrality.
  - Neurons that abolish output are the vertex cuts of the active excitatory S→T graph.
- **Prediction.**
  - ρ_s(f^LIN-A, f^emp) is substantially larger than ρ_s(best centrality, f^emp), with the
    grouped-bootstrap CI of the difference excluding 0.
  - On the fraction scale, Lin's concordance with the identity line is the strong form.
- **Falsifier.**
  - Centrality or baseline rate ≥ flow estimators.
  - Or vertex-cut status fails to identify the abolishing neurons (pre-set precision/recall bounds).
- **Limitations.**
  - Max-flow is sign-blind, so it uses the excitatory subgraph only.
  - Linear response requires a calibrated transfer function.
  - Agreement still lives inside the model (circularity, §5.7).

### RQ4 (extension: interactions). Do pairs follow from flow composition, with an intensity window of synergy?

- **H4.** ε_ab(λ) (product neutrality) is predicted with no free parameters by inclusion–exclusion
  f_ab = f_a + f_b − f_{a∧b} applied to the intact curve (theory §3).
  - Parallel converging pairs show a synergy window located at λ ∈ (λ*/(1 − max f), λ*/(1 − f_ab)).
  - Serial pairs show none.
  - Non-converging pairs are additive.
- **Prediction.**
  - Predicted vs observed ε(λ) curves agree better than a shuffled-pair null.
  - The window's position correlates with prediction.
- **Falsifier.** Prediction error is no better than the shuffled-pair null. That outcome would mean
  route-specific coincidence nonlinearities dominate, which is itself informative.
- **Limitations.**
  - Pair space is huge, so pairs must be pre-selected by a structural stratification (selection
    must not use pair outcomes).
  - The pilot has low power for class-level contrasts.

### RQ5 (generalization and validity). Does the law hold across tasks, hemispheres, connectome versions and animals, and is it consistent with experiments?

- **H5.** The law and the estimator ranking replicate:
  - left vs right sugar input;
  - v630 vs v783;
  - water→MN9 (paper extension: JON→descending neurons; BANC and male CNS).
- The model's f_k pattern is **qualitatively** consistent with experiment. Second-order types carry
  large f, and third-order/premotor types carry small f at the operating point corresponding to Shiu
  2022's 50 mM sucrose, matching "second-order required, premotor not".
- **Falsifier.** Sign reversals or collapse failure in replicates; or the model assigns premotor types
  larger f than second-order types.
- **Limitations.**
  - About 6–10 labelled types, so this is a sanity check, not a statistical benchmark.
  - Labels come from one concentration and one state, mostly one lab.
  - Hemispheres differ in GRN count: 21 right vs 10 left in the notebook sets `[V-src]`.
  - Neuromodulation and gap junctions are absent from the model.

---

## 4. Data and model feasibility (verified status)

| Resource | Status (this session) | Notes |
|---|---|---|
| Shiu model code (Brian2) | ✅ cloned, `philshiu/Drosophila_brain_model` @ 91bdd1e7 `[V-src]` | Silencing = outgoing weights only (README says "to and from"; code wins). Network is rebuilt every trial |
| FlyWire v783 and v630 connectivity | ✅ in the repo `[V-src]`. v783: 138,639 neurons, 15,091,983 edges (min 1 synapse), 40.0% inhibitory edges | No synapse threshold applied. Sign is per presynaptic neuron |
| Cell-type annotations (v783) | ✅ `flyconnectome/flywire_annotations` cloned `[V-src]` | **Notebook "right" = annotation "left"**: a consistent L/R label flip to resolve. One MN9 ID and 1 of 21 sugar GRN IDs are missing in v783 (ID drift: re-map) |
| Input set definitions | ⚠ The notebook "sugar" set includes 5 GRNs annotated high_salt and 4 "putative attractive"; the "water" set includes 7 annotated sugar `[V-src]` | Pre-register the input set: (i) Shiu's original list (reproduction) and (ii) annotation-pure LB3c/LB3b sugar GRNs (robustness) |
| Shiu raw simulation outputs | ❓ Edmond archive doi:10.17617/3.CZODIW (named in README) is **blocked here**; contents unverified | If it contains Fig. 1F (top-200 × 8 rates × 30 trials), it is a free pilot dataset for RQ2 on the user's own machine |
| BANC, male CNS, FAFB-783 compiled data | ✅ listed in public bucket `gs://lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/` `[V-src]` (male CNS simple edgelist 3.4 GB; BANC files up to 19.7 GB) | Paper extension only. ID and type matching is non-trivial |
| Hemibrain | ✅ public bucket `gs://hemibrain/` listed `[V-src]` | Lacks most of the SEZ, so not useful for this circuit |
| Simulation cost | **[ENG: final numbers pending]** Preliminary probe: about 5 s per 1-s trial (about 1 s build + 3.7 s simulate), RSS about 3 GB per process, 366–385 active neurons at 150 Hz (v630) | 4 cores / 15 GB here. Laptop numbers will differ |
| Stored outputs (author examples) | ✅ `results/example/`. At 100 Hz sugar: MN9_L 67.0 Hz, MN9_R 48.6 Hz. Single silencings shift MN9_L by −5.6% to +6.2% `[V-src]` | Single-neuron effects are small at 100 Hz, consistent with redundancy |
| Literature access | ⚠ Full texts blocked. WebSearch and Consensus budgets exhausted this session | Re-verify key claims with full text (§1.2) |

**Compute budget for the MVP** (to be finalized with ENG numbers). Assumes about 5 s per trial and
3 parallel workers:

| Block | Conditions | Trials | CPU-h |
|---|---|---|---|
| Intact curve O(λ), dense grid (25 λ) | 25 | × 30 | ≈ 1 |
| Calibration (transfer function, D*) | single-neuron runs | small | < 1 |
| Single-neuron curves: ~400 active neurons × 8 λ | 3,200 | × 8 (CRN) | ≈ 36 |
| Pair pilot: 60 pairs × 8 λ | 480 | × 8 | ≈ 5 |
| Robustness: w_syn ± 20% and left input, 60-neuron subset × 8 λ | ~1,500 | × 8 | ≈ 17 |
| **Total** | | | **≈ 60 CPU-h**, about 20 h wall-clock on 3 workers |

Speed-ups (validated before use):
- **Build once, reuse** (`store`/`restore`) saves about 20%.
- **Exact reduced subnetwork** (active set plus downstream closure, verified against the full model)
  could give a further 2–10×.

---

## 5. Experimental design

### 5.1 Circuit and readout

- **Primary.** Sugar GRNs → MN9 (proboscis extension), v783.
  - Input set: Shiu's 21 right sugar GRN IDs, re-mapped (20 present in v783).
  - Readout: MN9 rate.
  - Primary T: the MN9 present in both versions, plus its v783 contralateral partner after re-mapping.
- **Why.**
  - Defined input and output.
  - The richest published experimental labels (LIT-C).
  - The original authors' own validation.
  - Intensity sweeps already in the original design.
  - Single-neuron effects small at default drive, which is the regime where the theory is non-trivial.
- **Secondary (paper):**
  - water GRNs → MN9 (shared output, different input);
  - JON → aBN1/descending neurons (different circuit).

### 5.2 Perturbations

| Perturbation | Specification |
|---|---|
| Silencing | Zero outgoing synapses (as in the original code). A sensitivity check with "to and from" silencing for 20 neurons |
| Candidate set | All neurons with ≥ 1 Hz mean rate at λ_max in the intact model, about 400 (union across λ). Silent neurons have an effect of exactly 0 by construction. This is reported, not simulated |
| Intensity grid | Intact curve: 25 levels, 0 to about 4·λ50. Silenced curves: 8 log-spaced levels from about 0.7·λ50 to about 4·λ50 |
| Recruitment control | A random 50% of GRNs at fixed λ (sucrose concentration recruits GRNs as well as raising rates). Tests whether "rate" and "recruitment" rescale equivalently |
| Common random numbers (CRN) | Trial *t* uses seed *t* in every condition, so contrasts are paired |
| Pairs (pilot, ~60) | Pre-selected from neurons with 0.1 ≤ f^LIN-A ≤ 0.6 (individually non-abolishing), stratified by **structural** relation into parallel-converging, serial and non-converging (~20 each). Selection uses only structural or intact-simulation information |

### 5.3 Outcome metrics

| Metric | Definition |
|---|---|
| O(λ) | Mean MN9 spike rate over 1 s; λ50 from a monotone (constrained Hill or isotonic-spline) fit |
| f^emp_k | Fit O_k(λ) = γ·O((1 − f)λ) by maximum likelihood on trial-level counts (Poisson or negative binomial), with O interpolated from the intact fit. Shift-only fixes γ = 1 |
| Phenotype class | none / shift / gain / shift + gain / abolition (O_k ≈ 0 for all tested λ). Pre-registered BIC and CI rules |
| N_k(λ) | Single-intensity necessity 1 − O_k(λ)/O(λ) (for RQ1 comparability with Shiu's rule) |
| ε_ab(λ) | f_ab − f_a·f_b on normalized outputs (product neutrality; Min and Additive as sensitivity). Report w_a, w_b and w_ab, never ε alone |

### 5.4 Predictors

All predictors are computed without perturbation outcomes.

| Level | Predictors |
|---|---|
| L0 global | in/out degree and strength; PageRank; betweenness (exact on the SEZ-restricted graph and sampled whole-brain; method stated); k-core; rich-club membership (Lin et al. 2024 definition if obtainable, else degree > threshold) |
| L1 task topology | hop distance from S and to T; S→T path counts through *k* (length ≤ L); S→T betweenness; f^LIN-S; f^MF-S; dominator status in the excitatory S→T graph |
| L2 + activity | baseline rate r_k(λ_ref); f^LIN-A (calibrated gains); f^MF-A (capacities n_ij·r_j); active-subgraph vertex-cut status |
| Mechanistic | mean-field rate-model prediction (deterministic fixed point with calibrated φ). An optional rung between L2 and the spiking model |

### 5.5 Null models and controls

- **Rewired nulls** (for "is the structure–necessity relation special to the real wiring?"):
  degree-preserving, sign-preserving (Dale) rewiring with the synapse-count distribution permuted
  among swapped edges, and S and T fixed.
  - Prior work suggests MN9 may fall silent on rewired graphs (An 2026; MLX port), which would make
    a simulated null uninformative.
  - Use the nulls only for **structural** statistics: is S→T vertex connectivity or flow redundancy
    higher than chance?
  - Use the **type-label permutation** null for predictor-level claims.
- **Positive controls:**
  - silencing all sugar GRNs → abolition;
  - silencing the top direct excitatory inputs to MN9 → large f.
- **Negative controls:** silencing neurons with no S→T path → exactly 0 effect (pipeline check).
- **Reproduction gate:** reproduce stored author outputs (v630, 100 Hz and 200 Hz, and 3 silencing
  files) within Poisson CIs before any new run.
- **Parameter robustness:**
  - w_syn × {0.8, 1.2};
  - synapse threshold ≥ 1 (default) vs ≥ 5;
  - transmitter-sign flips for low-confidence neurons, if confidence is obtainable;
  - v630 vs v783.

  Report the stability of f^emp ranks (Kendall τ) and of every primary conclusion.
- **Input-set robustness:** Shiu's original list vs annotation-pure sugar GRNs.

### 5.6 Statistics

**Pre-registration.** This file plus `analysis_plan_draft.md`, frozen by a git commit before the
screens run.

**Primary confirmatory tests (Holm-corrected, family of 5).**

| # | Test |
|---|---|
| P1 (RQ2) | Proportion of effect-bearing neurons where shift-only beats shift + gain (ΔBIC > 2). H0: ≤ 0.5. One-sided exact binomial, with a cell-type-clustered sensitivity analysis |
| P2 (RQ3) | Δρ = ρ_s(f^LIN-A, f^emp) − max over L0 of ρ_s(·, f^emp). Grouped bootstrap (resample cell types, 2,000×); CI excluding 0 |
| P3 (RQ3) | Δρ between f^LIN-A and baseline rate r_k (same procedure) |
| P4 (RQ3) | Vertex-cut status vs abolition: precision and recall with exact CIs. Pre-set bound: both ≥ 0.8 (sensitivity analysis at 0.7) |
| P5 (RQ4, pilot) | Mean squared error of predicted ε(λ) curves vs observed, compared with 2,000 shuffled-pair predictions (permutation p) |

**Secondary analyses.**
- Incremental value of each rung: nested models with grouped 5-fold CV, folds by cell type.
- λ-stability of RQ1 rankings.
- Lin's CCC on the fraction scale.
- Window-position correlation.
- Left/right and v630/v783 concordance.
- Comparison with Shiu 2022 layer labels (Fisher exact, descriptive).

**Grouping.** All CIs resample **cell types** (FlyWire consensus annotation), because cell-type
members and L/R homologs are near-duplicates and random resampling leaks.

**Effect sizes.** Interpreted with pre-stated minimal effects of interest: Δρ ≥ 0.15; shift fraction ≥ 0.6.

### 5.7 Circularity and interpretation guardrails

1. RQ2 is purely dynamical. It tests the *model's* transmission, not structure.
2. RQ3 asks which compressions of W suffice. Because the model *is* W plus uniform dynamics, success
   means "transmission in this model is well summarized by S→T flow", **not** "real flies work this
   way".
3. Only RQ5's experimental comparison and cross-connectome replication bear on biology, and both
   are weak in the MVP.
4. Activity is not necessity, so baseline rate is a baseline every structural estimator must beat.
5. Model necessity ≠ biological necessity. The model lacks neuromodulation, gap junctions, hunger
   state and intrinsic heterogeneity. Single-neuron effects at default drive are small (§4), which
   may partly reflect the uniform-weight calibration.

---

## 6. Project selection (scoring)

Scores are 1–5 and reflect PI judgement, open to challenge. Weights: significance 0.25,
originality 0.25, feasibility in 5 weeks 0.20, compute 0.10, publication potential 0.20.

| Candidate | Signif. | Orig. | Feas. | Compute | Pub. | Weighted |
|---|---|---|---|---|---|---|
| C1 centrality vs necessity screen (H-A alone) | 3 | 1.5 | 5 | 4 | 2 | 2.93 |
| **C2 input-rescaling law + structural f (RQ2–RQ3)** | **4** | **4** | **4** | **3.5** | **4** | **3.95** |
| C3 pair interaction curves / synergy window (RQ4 full) | 4 | 3.5 | 2.5 | 2 | 4 | 3.38 |
| C4 task specificity (H-D) | 3 | 2 | 4 | 3.5 | 2.5 | 2.90 |
| C5 cross-connectome reproducibility of necessity | 3.5 | 3 | 2.5 | 3 | 3.5 | 3.13 |
| C6 Shapley (MSA) attribution on the Shiu model | 3 | 2.5 | 2 | 1.5 | 3 | 2.53 |

**Selection.**
- C2 as the core.
- C1 is folded in as RQ1, because it uses the same simulations and answers the student's literal question.
- A C3 pilot inside the MVP.
- C3 full, C5 and C4 as the paper extension.

---

## 7. Execution roadmap (MVP to 2026-12-10)

| Week | Dates | Deliverables | Gate |
|---|---|---|---|
| W1 | Nov 3–9 | Finalize design; red team; **1-page proposal**; pre-registration commit; simulation harness (CRN, build once, reproduction gate); input-set and ID re-mapping; calibration of φ and D* | Reproduction gate passed |
| W2 | Nov 10–16 | Intact dense curve; structural predictors L0–L2 and all f estimators (no perturbation data needed); launch single-neuron screen (overnight runs) | Predictors frozen before screen results are viewed |
| W3 | Nov 17–23 | Finish screen; fit f^emp and phenotype classes; RQ2 and RQ3 primary analyses; launch pair pilot and robustness subset | P1–P4 computed |
| W4 | Nov 24–30 (Thanksgiving 26th) | Pair pilot analysis (P5); L/R and v630/v783 replication; experimental-label comparison; figures | Figures drafted |
| W5 | Dec 1–9 | Slides (in-class workshops Dec 3 and Dec 8); rehearse; report outline | — |
| — | **Dec 10** | Presentation | — |
| After | Finals period (date to confirm) | 3–5 page report | — |

**Paper extension (2027).**
- Full pair screen (~500 pairs) with a fast validated simulator.
- Water and JON tasks.
- BANC and male-CNS replication.
- Analytic conditions for scalar-drive validity, from the mean-field theory.
- Rescaling-law predictions converted to sucrose concentration via published GRN dose–response.
- Outreach to experimental labs for a PER dose–response-under-silencing test.

---

## 8. Main risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| The scalar-drive law fails broadly (shift-only is a minority) | Medium | Still publishable as "where and why structure fails". The phenotype taxonomy and locations of failure become the result |
| Too few abolishing neurons for P4 | Medium–high (single effects are small at 100 Hz) | Report P4 descriptively if fewer than 5 positives. Use near-threshold intensities where cuts matter most |
| λ50 shifts beyond the tested range (large f) | Medium | Extend the grid adaptively for neurons with f^LIN-A > 0.6 (a pre-registered rule) |
| Compute exceeds budget | Low–medium | Reduce to the top 250 by f^LIN-A plus a stratified random 50; use the validated reduced-network simulator |
| Pre-emption by an unseen 2026 preprint | Medium (searches budget-limited) | Re-search with full text in W1. The quantitative law plus pair-curve prediction is a distinctive package |
| ID and side-convention errors | Medium | Re-map via annotations; unit tests on IDs; positive controls |

## 9. Decisions needed from the student

1. **Compute.** Where will simulations run (laptop cores and RAM, campus cluster, GPU)? This sets the
   screen size and whether a faster backend is worth validating.
2. **Proposal due date** (the course page released the requirements on 2026-11-03).
3. **Scope.** Is RQ4 (pairs) in the MVP as a pilot (recommended) or deferred?
4. **Full-text verification.** Can the student read Shiu 2024 (Fig. 1F text), Jacobs 2024 (pair
   methods) and Shiu 2022 (silencing figure source data) with browser access? This decides the final
   novelty wording.
