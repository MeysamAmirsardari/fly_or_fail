---
title: "Silencing as input rescaling: predicting the intensity-dependent consequences of neuron loss from connectome structure"
---

<p class="byline"><b>Meysam Amirsardari</b><br>Final project proposal · BIOE689N/NACS728Z, Network Neuroscience and Brain Dynamic Analysis, Fall 2026</p>

## Background and gap

Whole-brain connectomes such as FlyWire (Dorkenwald et al. 2024) and connectome-constrained spiking
models (Shiu et al. 2024) make it possible to silence any neuron in silico. Graph "importance" is
often taken to imply functional necessity, yet silencing single neurons in the fly feeding circuit
frequently has little effect (Shiu, Sterne et al. 2022; Jacobs et al. 2024). Shiu et al. (2024)
report that redundancy in the model's sugar→feeding circuit *increases with sensory stimulation*,
but this remains a qualitative statement. Two mature frameworks already describe how a system
responds to losing one component of a shared transmission route: shared **flux control** in
metabolic networks, where control coefficients sum to one (Kacser & Burns 1981), and **receptor
reserve** in pharmacology, where losing part of a reserve shifts the dose–response curve before it
lowers the maximum. Neither framework has been given a *structural* estimator, and neither has been
tested in a signed, spiking, whole-brain connectome model. We supply both.

## Research question

Can one structurally estimable number per neuron, the fraction *f* of sensory→motor transmission it
carries, predict the full stimulus-intensity-dependent consequence of silencing it? This covers
whether the behaviour is abolished or only made less sensitive, by how much, and how pairs of
silenced neurons interact.

## Hypotheses

- **H1 (baseline).** Classical centralities (degree, strength, PageRank, betweenness, k-core,
  output-synapse count) predict single-neuron necessity poorly and inconsistently across intensities.
- **H2 (input-rescaling law).** Silencing neuron *k* acts like weakening the stimulus:
  O<sub>k</sub>(λ) = O((1 − f<sub>k</sub>)λ). The dose–response curve shifts by 1/(1 − f<sub>k</sub>)
  **in sugar-receptor (GRN) drive** with its maximum preserved. Being a source→target vertex cut
  implies no recovery at any tested intensity; the converse need not hold in a threshold network.
- **H3 (structure).** f<sub>k</sub> can be estimated without any perturbation simulation, from the
  connectome (walk-sum linear-response and max-flow fractions) plus intact activity, and these
  estimates outperform every classical centrality and the neuron's baseline firing rate.
- **H4 (pairs, pilot).** Pair curves are predicted from the two single-neuron fractions plus an
  independently computed shared-route overlap.
- **H5 (summation/redundancy).** The fractions of neurons forming a sensory→motor cut sum to about 1
  under conservative transmission; the departure from 1 quantifies redundancy and changes
  systematically as stimulus intensity rises, making Shiu et al.'s statement quantitative.

## Approach

- **Model and readout.** The Shiu et al. (2024) leaky integrate-and-fire model on FlyWire v783
  (138,639 neurons), with v630 as a replication. The 20 right sugar GRNs are driven by Poisson input at
  rate λ. The primary readout is the single MN9 proboscis motor neuron contralateral to the stimulated
  GRNs; the ipsilateral MN9 is reported separately and the two are never averaged.
- **Simulator.** A batched re-implementation (`fastlif`) that reproduces the original Brian2 model
  spike-for-spike on identical input trains and runs about 100× faster, passing all pre-set
  validation gates against Brian2 and the authors' stored outputs.
- **Screens.** An intact dose–response curve (λ = 0–400 Hz in 5 Hz steps, 60 seeds) fixes a
  10-level, log-spaced silencing grid (0.5–8× the half-maximal intensity) *before* any silencing run.
  All 573 neurons active under sugar drive are then silenced singly (30 seeds, common random numbers
  for paired contrasts), together with positive and negative controls, whole-cell-type silencing for
  the external test, a 60-pair stratified pilot, and a recruitment control (random halves of the input).
- **Curve models.** Each silenced curve is fit as shift-only, shift-plus-gain, or a free Hill curve,
  chosen by cross-validated predictive error, with an absolute goodness-of-fit test on independent
  seeds and an explicit "uninformative" class for neurons whose curves cannot discriminate the models.
- **Structural predictors** (computed before any screen result is viewed). L0: the classical
  centralities above and hop distance to MN9. L1, structure only: walk-sum fraction (exact via
  Sherman–Morrison), excitatory max-flow fraction, dominator status. L2, activity-aware: gain-weighted
  walk-sum fraction f<sup>LIN-A</sup> on the active subgraph, activity-weighted max-flow, baseline rate.
- **External test.** Silencing outcomes of 10 cell types are compared with labels frozen in advance
  from published two-concentration optogenetic silencing (Shiu, Sterne et al. 2022): Rattle and Usnea
  strongest; Zorro, Clavicle, G2N-1 and FMIn intermediate; Phantom none; Bract, Fdg and Roundup
  (a later layer) without effect.

## Statistical plan (pre-registered, git commit `e051e08`)

- **Primary test (P-A).** Δρ = ρ<sub>s</sub>(f<sup>LIN-A</sup>, f̂) − max over L0 of ρ<sub>s</sub>(X, f̂),
  with a cell-type-grouped bootstrap (about 200 effective units, B = 2,000) that re-selects the best
  competitor inside every resample. Decision: the one-sided 95% lower bound must exceed 0.
- **Secondary family (Holm, α = 0.05).** S1 activity-aware estimator vs baseline rate; S2 structure-only
  estimator vs L0; S3 dominators are mostly no-recovery (exact binomial); S4 Kendall τ<sub>b</sub>
  between type-level f̂ and the frozen labels (exact permutation null); S5 second-order types exceed
  the later layer (exact Wilcoxon).
- **Estimation only.** Collapse fraction (H2), summation (H5), pairs (H4), and replications (v630,
  left-side input, ±20% synaptic weight, and the authors' own published silencing runs).

## Predicted outcomes and falsifiers

Among neurons whose curves can discriminate the models, most obey the rescaling law; the claim fails
if the upper 95% bound of the collapse fraction is below 0.5. The activity-aware flow fraction ranks
neurons better than every centrality (fails if P-A's lower bound is ≤ 0). Failure to recover within
the tested range is concentrated in vertex cuts. Pre-declared failure modes are λ-gated inhibitory
neurons, routes with different thresholds, and coincidence-driven transmission near threshold.
A failure of the law is informative in its own right: it maps where connectome structure stops being
sufficient to predict function.

## Limitations

Results describe the model, not the fly; only the external test (about 10 cell types) bears on
biology, and it is a small-sample check. *f* is a finite-change flux control coefficient: the
contribution is its structural estimation and its dose–response consequences, not the concept. The
model lacks neuromodulation and gap junctions, and has a known transmitter-sign failure in GABAergic
second-order neurons (Phantom; Shiu et al. 2024) that the external test may expose; a failure
confined to Usnea and Phantom is pre-declared as this limitation. Because the model is built from
the same connectome as the predictors, "structure predicts model necessity" is partly true by
construction; the question is which compressions of the wiring suffice.

## Status and deliverables

As of Nov 3, the design is pre-registered, the simulator is validated, the intact curves and the
silencing grid are frozen, and the silencing screens are running. Deliverables for the Dec 10
presentation and the 3–5 page report: the rescaling test; a structure-vs-function predictor
comparison; the external concordance test; the pair pilot; and an experimentally testable
prediction: silencing a neuron shifts the dose–response curve in GRN firing rate by 1/(1 − f), with
the conversion to sucrose concentration given as a conditional corollary.

<p class="refs"><b>References.</b> Dorkenwald et al. 2024, <i>Nature</i> (FlyWire). Jacobs et al. 2024, <i>Cell Reports</i> 43:114782. Kacser &amp; Burns 1981, <i>Genetics</i> 97:639–666. Shiu, Sterne et al. 2022, <i>eLife</i>. Shiu et al. 2024, <i>Nature</i>.</p>
