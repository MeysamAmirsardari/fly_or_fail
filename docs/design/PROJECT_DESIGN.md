# PROJECT DESIGN v1.0 (PRE-REGISTRATION): Silencing as Input Rescaling

## Structural prediction of the intensity-dependent consequences of neuron loss in a whole-brain *Drosophila* model

**Status.** Pre-registration v1.0, 2026-11-03. It is frozen by the git commit that introduces this
version, and that commit hash is the timestamp. No silencing screen has been run before this commit.

**Supersedes.** v0.9 and `analysis_plan_draft.md`, which is retained for history only. Where they
conflict, **this document governs.** All red-team items are resolved in §10 and in DECISIONS D-008.

**Companion documents:**
- `docs/design/theory_note.md` (v0.3)
- `docs/research/redteam_review.md`
- `docs/research/fulltext_verification.md` (frozen external labels, §8)
- `docs/research/sim_validation.md` (simulator gates)

**Evidence tags:**
- `[V-full]`: full text read;
- `[V-abs]`: abstract or snippet;
- `[V-src]`: code or data inspected;
- `[MEM]`: unverified.

---

## 0. Summary

**Question.** In a connectome-constrained spiking model of the fly brain, can one structurally
estimable number per neuron predict the whole stimulus-intensity-dependent consequence of silencing
it? The number is the fraction f_k of sensory→motor transmission the neuron carries.

**Framework: an explicit bridge.** Two mature quantitative frameworks already describe how a
system responds to losing one component of a shared transmission route:
- **Metabolic control analysis (MCA).** The flux control coefficient is shared among enzymes and
  coefficients sum to 1 (summation theorem). This explains why removing one enzyme often barely
  changes flux (Kacser & Burns 1981 `[V-abs]`). f_k is a finite-change analogue of a flux control
  coefficient.
- **Pharmacology.** Losing part of a transduction reserve shifts the dose–response curve before it
  lowers the maximum (receptor reserve `[MEM]`).

Neither framework comes with a *structural estimator* of the control fraction, and neither has been
tested in a signed, spiking, whole-brain connectome model. **We provide and test both.**

**The law under test (Approximation A).** O_k(λ) = O((1 − f_k)·λ). Silencing *k* is equivalent to
weakening the stimulus by the factor (1 − f_k), measured along the GRN firing-rate axis λ.

**What is new, given what the full texts take off the table.** Already published, and cited as such:
- redundancy grows with stimulation (Shiu 2024 `[V-full]`);
- descriptive single and pair silencing in this model (Shiu 2024; Jacobs 2024 `[V-full]`);
- a structure→silencing correlation via output-synapse count (Minnick 2026 `[V-full]`);
- sensory→motor max-flow on a fly connectome (Berg 2026 `[V-full]`).

Our contribution:
1. a perturbation-free **structural estimator** of f_k (walk-sum / linear-response and max-flow
   fractions), tested against simulated f_k and against classical centralities including
   output-synapse count;
2. a **curve-collapse test** of scalar-drive transmission, with failure modes predicted in advance;
3. **dominator (single-vertex cut) status** vs failure to recover, at single-neuron resolution across
   intensities;
4. a **summation / redundancy** test that makes Shiu's qualitative statement quantitative;
5. pair-curve predictions (pilot);
6. a **pre-registered external test** against published two-concentration silencing data (Shiu &
   Sterne 2022), with labels frozen before any f is computed.

---

## 1. Literature basis

See `docs/research/lit_A`, `lit_B`, `lit_C`, `novelty_prior_art.md` and `fulltext_verification.md`.

**Key verified facts:**
- **Shiu 2024** `[V-full]`:
  - silencing screen over the top 200 neurons at 50–120 Hz, with an "≤ 80% at any frequency" rule;
  - "greater redundancy in the circuit as sensory stimulation increases";
  - W_syn chosen so that 100 Hz gives about 80% of maximal MN9;
  - robustness to W_syn ± 30% and to the inhibitory:excitatory ratio ± 50%.
- **Shiu & Sterne 2022** `[V-full, figure images]`:
  - GtACR1 at 50 mM: 6 of 7 second-order types reduce PER (Phantom does not);
  - at 100 mM, only Rattle and Usnea do;
  - Bract, Fdg and Roundup have no effect at 50 mM.
- **Jacobs 2024** `[V-full]`: all singles and pairs of second-order neurons at 50/100/200 Hz;
  readouts are stopping neurons, not MN9; descriptive.
- **Minnick 2026** `[V-full]`: output synapses vs single-type silencing effect, ρ = 0.78 (11 types).
- **Berg 2026** `[V-full]`: population-level sensory→motor max-flow.
- **Chen & Xi 2025** `[V-full]`: "additive" double silencing at a fixed intensity.

**Coverage caveat.** Searches hit tool quotas; three bridge-specific searches were never run
("flux control coefficient" + connectome; "dose ratio"/"Schild" + network model;
dominator/articulation + connectome). The bridge framing does not rest on absence claims.

---

## 2. Novelty positioning (replaces v0.9 §2)

| Element | Status | How we present it |
|---|---|---|
| Redundancy grows with intensity | Published (Shiu 2024) | Cited. We provide a quantitative version (S6) |
| Neuron pairs interact non-additively | Published descriptively (Jacobs 2024; Minnick 2026; Chen & Xi 2025; Towlson & Barabási 2020) | Cited. Our pair arm is an estimation pilot |
| f as a control coefficient; EC50 shift with the maximum kept | Concepts from MCA and pharmacology | Explicit bridge, cited |
| Structural estimator of f; collapse test; dominator vs no-recovery; summation test in a spiking connectome model; pre-registered external two-concentration test | Not found in quota-limited searches | Stated as our contribution, without "first" claims |

---

## 3. Notation (frozen)

| Symbol | Meaning |
|---|---|
| λ | Poisson rate (Hz) applied to every neuron of the input set S |
| O(λ) | intact MN9 rate (primary readout T, §5.1) |
| O_k(λ) | MN9 rate with *k* silenced |
| **f_k** | **rescaling fraction only**: O_k(λ) ≈ O((1 − f_k)λ). f̂_k is its simulation estimate (§6.3). f^LIN-A, f^LIN-S, f^MF-A, f^MF-S are structural estimators (§6.4) |
| **w_k(λ)** | O_k(λ)/O(λ), the normalized output |
| **N_k(λ)** | 1 − w_k(λ), single-intensity necessity |
| ε_ab(λ) | w_ab(λ) − w_a(λ)·w_b(λ) (Mani et al. 2008 product neutrality). Always reported together with w_a, w_b, w_ab |
| λ50 | intensity where O reaches 0.5·O_max on the intact curve |
| O_max | maximum of the intact mean curve over the grid |

---

## 4. Research questions and hypotheses

Each item lists its hypothesis, prediction, falsifier and limitation.

**RQ1 (baseline). Do classical structural measures predict single-neuron necessity N_k(λ)?**
- *Hypothesis.* Global measures predict poorly and inconsistently across λ. Task-specific
  measures do better.
- *Estimation.* Per-λ ρ_s and AUPRC.
- *Limitation.* Grey-literature precedents exist (StrokeSim, fly-bottlenecks); this is the
  baseline section.

**RQ2 (dynamics). Does the rescaling law hold?**
- *Hypothesis.* Among informative, effect-bearing, non-GRN neurons, most curves collapse.
- *Predicted failure modes* (theory v0.3 §3):
  - λ-gated inhibitory neurons;
  - routes with different thresholds;
  - coincidence-driven transmission near high-convergence, near-threshold targets.
- *Estimation, not a null-hypothesis test.* Collapse fraction with a cell-type-clustered CI, plus
  the informative fraction.
- *Falsifier (for the claim "the law describes most neurons").* The upper 95% CI bound of the
  collapse fraction is below 0.5.

**RQ3 (structure). Can f be estimated without perturbation?**
- *Hypothesis.* f^LIN-A predicts f̂ better than every member of a closed family of classical
  competitors.
- *Primary test.* P-A (§7.1).
- *Secondary tests.* Activity baseline (S1), structure-only version (S2), dominators (S3).

**RQ4 (pairs, pilot). Are pair curves predicted by f̂_a, f̂_b and a structural overlap term?**
- Estimation only (§6.6).

**RQ5 (validity).**
- External two-concentration test (S4, S5).
- Summation/redundancy (S6).
- Recruitment control; v630, left-input and W_syn replications.

---

## 5. Model, data and simulator

### 5.1 Model, inputs and readouts

**Model and data.**
- Shiu et al. LIF, as in `model.py` @ 91bdd1e7 `[V-src]`.
- FlyWire **v783 primary**; v630 for the reproduction gate and replication.

**Input sets.**
- **S_shiu**: Shiu's right sugar-GRN list, the 20 IDs present in v783. Primary for RQ1–RQ4, for
  comparability.
- **S_pure**: all v783 neurons annotated sugar (LB3c) or sugar/low_salt (LB3b) on the **same side**
  as S_shiu (annotation side "left"; notebook "right"). Primary for the external arm (S4, S5);
  replication for RQ2–RQ3.

**Readouts.**
- **Primary T** = MN9 `720575940660219265`. Annotated CB0701, side "right", so it is contralateral
  to the stimulated GRNs. Present in v630 and v783.
- **Secondary**: the ipsilateral MN9. In v783 this is CB0701 side "left", `720575940618238523`; the
  v630 ID is `720575940645521262`, mapping per ENG. It is reported as a separate curve.
- **The two MN9s are never averaged.**
- The left/right convention is fixed in one place in code and asserted.

### 5.2 Simulator

- `sim/fastlif.py`, a batched numba replica on an exact closure network (`sim/reduce.py`).
- Acceptance (`docs/research/sim_validation.md`):
  - G0: spike-for-spike agreement with Brian2 objects driven by identical input trains;
  - G1: per-neuron rates and MN9 within the pooled Brian2 95% CI (60 trials) at 50, 100 and 200 Hz;
  - G2: the authors' stored outputs;
  - G3: closure network bit-identical to the full network;
  - G4: common random numbers (CRN);
  - G5: speed.
- **Fallback.** If any gate fails, the identical design runs on Brian2 in a persistent process,
  following the descoping ladder in §9.
- **Unit tests (mandatory):**
  - silencing *k* zeroes exactly k's out-degree worth of weights;
  - silencing T itself gives f = 0;
  - silencing all of S gives no MN9 output.

### 5.3 Intensity grid and trials

| Item | Specification |
|---|---|
| Intact curve | λ = 0, 5, …, 400 Hz (81 levels) × 60 seeds (0–59). Seeds 0–29 are paired with the screen; seeds 30–59 are independent and used for the absolute goodness-of-fit (GOF) |
| Silencing grid | 10 levels, log-spaced from 0.5·λ50 to min(8·λ50, 400 Hz), fixed from the intact curve **before** any silencing run. Levels above 200 Hz are flagged non-physiological |
| Screen trials | 30 (seeds 0–29), CRN across conditions |
| CRN use | Contrasts use per-seed paired differences. Absolute GOF uses independent seeds |

### 5.4 Candidate set

- Every neuron with at least one spike in any intact run on the silencing grid, excluding S and T.
- The input neurons S are screened separately as **positive controls**. Their f is close to their
  share of output by construction, so they are excluded from all tallies.
- Neurons that are silent at every λ have f = 0 by construction. They are reported analytically, not
  simulated.
- The candidate set includes low-rate neurons (0 < r < 1 Hz), which preserves the range of the
  baseline-rate competitor (red-team M5).

---

## 6. Measurements and predictors

### 6.1 Effect gate

Neuron *k* is **effect-bearing** if both hold at at least one grid λ with O(λ) ≥ 5 Hz:
- the paired (CRN) mean difference O_k − O has a 95% seed-bootstrap CI excluding 0;
- |N_k(λ)| ≥ 0.05.

### 6.2 Informativeness gate

An effect-bearing neuron is **informative** if, under its shift-only fit f̂, the grid contains:
- at least 2 λ with Ô((1 − f̂)λ) ∈ [0.2, 0.8]·O_max, and
- at least 1 λ with Ô((1 − f̂)λ) ≥ 0.9·O_max.

All other effect-bearing neurons are classed **"uninformative"** (red-team C1).

### 6.3 Curve models (red-team C1, C5)

- **Ô** is a monotone (isotonic, then PCHIP) interpolant of the intact mean curve, estimated on the
  training seeds.
- **Candidate models per neuron:**
  - M_shift: Ô((1 − f)λ);
  - M_gain: γ·Ô((1 − f)λ);
  - M_free: an independent Hill curve (E_max, λ50, n).
- **Fitting.** Least squares on per-seed rates, weighted by the inverse empirical per-λ variance
  (quasi-likelihood; MN9 is under-dispersed, Fano ≈ 0.65 `[V-src]`).
- **Selection.** 5-fold cross-validation over seeds; lowest held-out error wins. A one-SE rule
  favours the simpler model (shift < gain < free).
- **Absolute GOF of M_shift.** Fit f on seeds 0–29 and compare to the intact curve Ô_ind built from
  seeds 30–59:

  χ² = Σ_λ (Ō_k(λ) − Ô_ind((1 − f̂)λ))² / (s_k²(λ)/30 + s_O²(λ)/30), with df = L − 1.

  **Collapse holds** if M_shift is selected and the GOF p ≥ 0.05.
- **Classes:**

  | Class | Definition |
  |---|---|
  | none | not effect-bearing |
  | shift | collapse holds |
  | gain | M_gain selected |
  | other | M_free selected, or GOF fails |
  | no-recovery | O_k < 0.1·O_max at every grid λ |
  | uninformative | fails the informativeness gate (§6.2) |

- **f̂ for every candidate** is the M_shift estimate. It is defined even when collapse fails, as the
  best one-parameter summary, and is used as the RQ3 target. A sensitivity analysis restricts to the
  shift class.
- **Reliability.** Split-half f̂ (odd vs even seeds). Report the reliability ceiling and the
  disattenuated ρ.
- **Shared-curve uncertainty.** Ô is re-estimated inside every bootstrap resample (nested bootstrap).

### 6.4 Structural predictors (computed by STRUCT before any screen result is viewed; `analysis/PREDICTORS.md`)

| Level | Predictors |
|---|---|
| L0, the closed competitor family for P-A | in-degree; out-degree; in-strength; **out-strength (output synapse count; the Minnick 2026 competitor)**; PageRank; sampled betweenness; k-core; −(hop distance to T) |
| L1, structure only | f^LIN-S (walk-sum fraction, exact by Sherman–Morrison); f^MF-S (excitatory max-flow fraction); S→T walk counts; dominator status |
| L2, intact activity | baseline rate r_k(λ50); f^LIN-A (gain-weighted walk sum on the active subgraph; gains D_i = Δr_i/Δμ_i from the intact curve); f^MF-A; active-graph dominator status; min-cut participation count |

### 6.5 Pairs (pilot; selected only after the single screen; red-team M1, M10, M11)

**Selection.** 60 pairs:
- 30 parallel-converging: no path of ≤ 3 hops between a and b in either direction, and a shared
  downstream target within 2 hops of both, before T;
- 15 serial: a → b within 3 hops, both on S→T paths;
- 15 non-converging.

Crossed with single-neuron f̂ magnitude:
- parallel pairs: both f̂ ∈ [0.05, 0.6];
- other strata: matched where possible.

The grid and trials are as in §5.3.

**Predictions.**
- **T5a** (dynamics + structure): Ô((1 − f̂_a − f̂_b + f^LIN-A_{a∧b})λ), where the overlap is
  computed directly as the walk-sum fraction through both neurons.
- **T5b** (structure only): Ô((1 − f^LIN-A_{ab})λ).

**Null.** The overlap term is set to its stratum mean.

**Metrics.**
- RMSE of w_ab(λ) and ε_ab(λ), evaluated only where O(λ) ≥ max(5 Hz, 3·SE);
- the fraction of pairs whose observed curve lies inside the 95% prediction band.

**Status.** Estimation only. Labelled as a pilot.

### 6.6 Recruitment control (red-team m8)

- 10 random 50% subsets of S_shiu, on the full grid.
- Prediction: O_sub(λ) ≈ Ô((1 − f_sub)λ), where f_sub = f^LIN-A of removing the complementary GRNs.
- Estimation.

---

## 7. Statistical plan

### 7.1 Primary confirmatory test (exactly one)

**P-A.** Δρ = ρ_s(f^LIN-A, f̂) − max_{X∈L0} ρ_s(X, f̂), over all candidates.

- **Unit.** Resampling is by cell type: n_eff ≈ 190–210 FlyWire types `[red-team M7]`. Unannotated
  neurons from ID drift are grouped with their nearest annotated homolog where the mapping is
  unambiguous; otherwise they are singletons. The singleton count is reported.
- **Procedure.** Grouped bootstrap with B = 2,000. The maximizing L0 predictor is **re-selected inside
  every resample** (red-team M8), and Ô is re-estimated inside every resample.
- **Decision.** One-sided: the lower bound of the 95% CI of Δρ must be > 0.
- **Effect size.** MEI Δρ ≥ 0.15. Power ≈ 0.71–0.89 at n_eff ≈ 200 `[red-team §4.3]`.
- **Sensitivity.** A Hotelling–Williams / Steiger test against the selected competitor; the
  shift-class-only subset; Spearman vs disattenuated ρ.

### 7.2 Secondary confirmatory family (Holm, α = 0.05)

| ID | Test |
|---|---|
| S1 | f^LIN-A vs baseline rate r_k(λ50): Δρ > 0, same procedure as P-A |
| S2 | f^LIN-S (structure only) vs L0 family: Δρ > 0 |
| S3 | Among dominators of T in the excitatory active graph at λ50 (single-vertex S→T cuts; super-source over S; GRNs and T excluded), the proportion in class no-recovery > 0.5 (exact one-sided binomial; run only if ≥ 5 dominators, otherwise descriptive). The converse direction is descriptive only, because no-recovery does not imply a cut in a threshold network (red-team M3) |
| S4 | External concordance: Kendall τ_b between the S_pure screen's signed f̂ for the 7 second-order types and the frozen 3-tier labels (Rattle, Usnea = 2; Zorro, Clavicle, G2N-1, FMIn = 1; Phantom = 0). Exact permutation null over 7! = 5,040 permutations; τ_b ≥ 0.6 gives p = 0.0286; the maximum attainable τ_b is 0.816 `[red-team §6.3]` |
| S5 | Layer test: f̂ of the 7 second-order types > f̂ of {Bract, Fdg, Roundup}. One-sided exact Wilcoxon (minimum p = 1/120) |

- **Cell-type f̂.** Each type's f̂ is the f̂ for silencing **all members of the type together** (one
  condition per type), which matches the genetic-line experiments.
- **Usnea and Phantom.** Usnea and Phantom are GABAergic in the model. A signed-f̂ failure confined
  to them is declared in advance as a transmitter-sign limitation of the model, not a falsification
  of the law. Shiu 2024 reports the model's own failure on Phantom `[red-team §6.4]`. A failure
  spread across cholinergic types counts as falsification.

### 7.3 Reported, not in the confirmatory family

- **S4 variants:** |f̂|; S_shiu input; f^LIN-A; top-2 exact test (p = 1/21); sensitivity labels with
  G2N-1 and FMIn as tier 0.5.
- **S6 summation/redundancy.** Let C1 be the cut set of neurons directly postsynaptic to S (a true S→T
  vertex cut). Pointwise f_k(λ) is obtained by inverting O_k(λ) = Ô((1 − f)λ) wherever
  O ∈ [0.1, 0.9]·O_max. Predictions:
  - Σ_{k∈C1} f_k(λ) ≈ 1 under conservative transmission;
  - the sum decreases with λ (quantifying Shiu's redundancy statement).

  Seed bootstrap.
- **RQ1:** per-λ ρ_s and AUPRC for N_k(λ) ≥ 0.2.
- **RQ2:** collapse fraction (clustered CI); informative fraction; class distribution.
- **Confounds:**
  - partial ρ controlling for hop distance to T and r_k;
  - within-layer analyses (red-team M6).
- **Pairs and recruitment** (§6.5–6.6).
- **Replications:** v630; left input (Kendall τ of type-level f̂ ranks, each side referenced to its
  own λ50); W_syn ± 20% (intact curve plus the top 50 neurons).

### 7.4 Multiplicity and reporting

- One primary test (P-A); a Holm family {S1–S5}; everything else is exploratory.
- Reported for every neuron and pair: raw w and O values with CIs, never derived scores alone.
- Deviations from this plan are logged in DECISIONS.md with a reason.

---

## 8. Controls and guardrails

**Positive controls:**
- silencing all of S: no output;
- each GRN individually: f̂ close to its structural share;
- top direct excitatory inputs of T.

**Negative controls:**
- silencing T: f = 0;
- silencing neurons with no S→T path: f = 0.

**Reproduction gate.** Stored author outputs: MN9 inside the empirical 95% interval of 30 trials,
per-neuron r ≥ 0.99. Numeric tolerances are as in sim_validation.md.

**Circularity guardrails:**
- RQ2 is a test of the model's dynamics only.
- RQ3 asks which compression of W suffices *within the model*.
- Only S4, S5 and the replications bear on biology or individual variability.
- Model necessity is not biological necessity.

---

## 9. Descoping ladder (frozen; apply in order without new deliberation)

Compute is not expected to bind (fastlif ≈ 0.05 s per trial-condition).

1. W_syn robustness. Cite Shiu 2024's ± 30% analysis instead.
2. v630 replication.
3. Pairs: reduce to 30 parallel pairs, then drop.
4. Left-input replicate.
5. Recruitment control: 4 subsets × 5 λ.
6. Grid 10 → 6 levels; trials 30 → 15.

**Never cut:** intact curve, primary screen, external arm (S4, S5), reproduction gate, unit tests,
controls.

---

## 10. Red-team resolution summary (details in DECISIONS D-008)

| Issue | Resolution |
|---|---|
| C1 (P1 cannot fail) | Absolute GOF on independent seeds; 3-way CV selection; informativeness gate; RQ2 reported as an estimate |
| C2 (compute infeasible) | Resolved by the validated fastlif simulator, about 100× faster than Brian2 (G0 spike-exact). The ladder in §9 is retained |
| C3 (archive Fig. 1F) | Requested from the user. If obtained, used as an independent replication on the authors' Brian2 runs (v630, 50–120 Hz) |
| C4 (notation clash) | §3 notation; analysis_plan superseded |
| C5 (likelihood) | Quasi-likelihood with empirical variance; held-out-seed CV; paired contrasts |
| M1 | T5a and T5b defined; no "no free parameters" claim |
| M2 | Predictions stated on the GRN-rate axis; the concentration form is a conditional corollary |
| M3 | Only the sound direction is confirmatory (S3) |
| M4 | Single contralateral MN9; never averaged |
| M5 | Low-rate neurons included |
| M6 | Distance to T in the competitor family; partial and within-layer analyses |
| M7 | n_eff stated; cell-type bootstrap |
| M8 | Max re-selected inside each resample |
| M9 | One primary test |
| M10 | Pairs selected by structure × f̂ strata |
| M11 | SNR floor for ε |
| M12 | S_pure for the external arm |
| M13 | MCA and receptor-reserve bridge |
| m1–m8 | Addressed: unit tests; theory v0.3; numeric gates; simulated rewired nulls dropped; 91% figure removed; left-input via ranks; recruitment control promoted |

---

## 11. Execution plan (whole project due 2026-11-05)

| When | Step |
|---|---|
| Nov 3 (today) | Pre-registration commit (this file) → SIM final gates → STRUCT predictors → intact curve → λ grid frozen (commit) → single screens (S_shiu, S_pure type-level) → pairs and recruitment → replications |
| Nov 4 | Analysis (P-A, S1–S6, RQ1–RQ2 estimates), figures, report draft |
| Nov 5 | Final report, slides, proposal, push |
