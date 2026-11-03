---
title: "Silencing as Input Rescaling: Predicting the Intensity-Dependent Effects of Neuron Loss from Connectome Structure"
---

<p class="byline">Project proposal · BIOE689N/NACS728Z Network Neuroscience and Brain Dynamic Analysis · Fall 2026</p>

## 1. Background and motivation

Complete synaptic wiring diagrams such as the FlyWire connectome of the adult *Drosophila* brain
(Dorkenwald et al., 2024), together with spiking models built directly on them (Shiu et al., 2024),
allow any neuron to be silenced in simulation and its behavioural consequence read out. A common
working assumption is that neurons that are central in the graph are also functionally necessary.
Experiments in the fly feeding circuit argue against a simple version of this view: silencing single
second-order gustatory neurons often has modest or no effect on proboscis extension (Shiu et al.,
2022; Jacobs et al., 2024). In the whole-brain model, Shiu et al. (2024) further observed that
redundancy in the sugar pathway increases with stimulus strength, so that the effect of losing a
neuron depends on how strongly the circuit is driven.

Two established frameworks describe closely related situations. In metabolic control analysis,
control over pathway flux is shared among enzymes and the control coefficients sum to one, which
explains why removing a single enzyme often barely alters flux (Kacser & Burns, 1981). In
pharmacology, partial loss of a receptor reserve shifts the dose–response curve to the right before
it lowers the maximal response. Neither framework has been equipped with an estimator derived from
network structure, and neither has been tested in a signed, spiking, whole-brain connectome model.
This project develops such an estimator and tests its predictions.

## 2. Research question and hypotheses

Can a single, structurally estimable quantity per neuron, the fraction $f_k$ of sensory-to-motor
transmission carried by neuron $k$, predict the full intensity-dependent consequence of silencing
that neuron? Let $O(\lambda)$ denote the firing rate of the proboscis motor neuron MN9 when sugar
gustatory receptor neurons (GRNs) are driven at rate $\lambda$, and $O_k(\lambda)$ the same rate
with neuron $k$ silenced.

**H1.** Classical centrality measures (degree, synaptic strength, PageRank, betweenness, k-core,
output synapse count) predict single-neuron necessity poorly and inconsistently across stimulus
intensities.

**H2 (input-rescaling law).** Silencing acts as a weakening of the stimulus,
$O_k(\lambda) = O\big((1-f_k)\,\lambda\big)$: the dose–response curve shifts by a factor
$1/(1-f_k)$ along the GRN-rate axis while its maximum is preserved. A neuron that is a
source-to-target vertex cut should abolish the response at every tested intensity; the converse is
not expected to hold in a threshold network.

**H3.** $f_k$ can be estimated without simulating any perturbation, from walk-sum (linear-response)
and max-flow fractions computed on the connectome and weighted by intact activity, and this estimate
outperforms both classical centralities and the neuron's baseline firing rate.

**H4 (pilot).** The response to silencing a pair of neurons is predicted by their individual
fractions together with an independently computed measure of their shared routes.

**H5.** Across a set of neurons that separates the sensory input from the motor output, the
fractions sum to approximately one, and the departure from one, which measures redundancy, changes
systematically with stimulus intensity.

## 3. Methods

**Model and stimulation.** We use the leaky integrate-and-fire model of Shiu et al. (2024) on
FlyWire v783 (138,639 neurons), with v630 as a replication. Twenty right-hemisphere sugar GRNs
receive Poisson input at rate $\lambda$. The primary readout is the MN9 contralateral to the
stimulated GRNs; the ipsilateral MN9 is analysed separately. Simulations use an optimized
re-implementation of the model that reproduces the original simulator spike for spike under
identical input and is roughly two orders of magnitude faster.

**Silencing experiments.** An intact dose–response curve (0–400 Hz in 5 Hz steps, 60 trials)
defines a 10-level, logarithmically spaced intensity grid spanning 0.5 to 8 times the half-maximal
intensity, fixed before any silencing simulation. Each of the 573 neurons active under sugar drive
is silenced individually across this grid (30 trials, with common random numbers so that silenced
and intact conditions can be compared trial by trial). The design also includes positive and
negative controls, whole-cell-type silencing for external validation, a stratified pilot of 60
neuron pairs, and a recruitment control in which random halves of the input population are driven.

**Curve analysis.** Each silenced dose–response curve is fitted with three nested descriptions: a
pure horizontal shift (H2), a shift with an additional gain change, and an unconstrained Hill
function. Model choice is made by cross-validated prediction error, and the shift model is
additionally checked with an absolute goodness-of-fit test on held-out trials. Neurons whose curves
cannot distinguish between the models are reported as uninformative rather than counted as support.

**Structural predictors.** All predictors are computed before any silencing result is examined. The
baseline family comprises the classical centralities above and the hop distance to MN9. The
structure-only family comprises the walk-sum fraction (computed exactly with Sherman–Morrison
updates), the excitatory max-flow fraction and dominator status. The activity-aware family weights
the walk-sum and max-flow fractions by neuronal gains measured on the intact dose–response curves.

**External validation.** For ten cell types with published optogenetic silencing data at two
sucrose concentrations (Shiu et al., 2022), behavioural outcomes were assigned to three tiers in
advance of any model analysis (Rattle and Usnea strongest; Zorro, Clavicle, G2N-1 and FMIn
intermediate; Phantom without effect), with Bract, Fdg and Roundup forming a downstream layer
without effect. Model fractions are obtained by silencing all members of each type together.

## 4. Statistical analysis

The analysis plan was fixed before any silencing simulation. The primary test compares rank
correlations with the simulated fractions $\hat f$:
$\Delta\rho = \rho_s(f^{\mathrm{LIN\text{-}A}}, \hat f) - \max_{X} \rho_s(X, \hat f)$, where
$f^{\mathrm{LIN\text{-}A}}$ is the activity-aware walk-sum fraction and $X$ ranges over the
classical centralities. Confidence intervals come from a bootstrap that resamples cell types (about
200 effective units, 2,000 resamples) and re-selects the best competitor in every resample; H3 is
supported if the one-sided 95% lower bound exceeds zero. Five secondary tests, corrected with the
Holm procedure, compare the activity-aware estimator with baseline firing rate, the structure-only
estimator with centrality, the outcome of dominator neurons (exact binomial test), the agreement
between type-level fractions and the experimental tiers (Kendall's $\tau_b$ with an exact
permutation null), and the separation between second-order and downstream types (exact Wilcoxon
test). The fraction of neurons obeying H2, the summation test (H5), the pair pilot (H4) and the
replications (v630, left-hemisphere input, ±20% synaptic weight, and the original authors' published
silencing simulations) are reported as estimates with confidence intervals.

## 5. Expected results and falsification

We expect most neurons with informative curves to follow the rescaling law; the claim will be
rejected if the upper 95% confidence bound on this fraction lies below one half. We expect the
activity-aware flow fraction to rank neurons more accurately than any centrality measure, and loss
of response across all intensities to be concentrated in vertex-cut neurons. Deviations are
anticipated for inhibitory neurons whose influence depends on stimulus intensity, for parallel
routes with different thresholds, and for transmission that relies on coincident input near
threshold. Where the law fails, the pattern of failures identifies the conditions under which
connectome structure is insufficient to predict function.

## 6. Limitations

All conclusions concern the model rather than the animal; only the external comparison, which
involves ten cell types, bears directly on biology. The quantity $f_k$ is a finite-change analogue of
a flux control coefficient, so the contribution lies in its structural estimation and its
dose–response consequences rather than in the concept itself. The model omits neuromodulation and
electrical synapses and is known to misrepresent some GABAergic second-order neurons, including
Phantom (Shiu et al., 2024); disagreement confined to Usnea and Phantom will therefore be attributed
to transmitter sign rather than to the law. Finally, because the model and the predictors share the
same wiring diagram, part of any structure–function agreement is expected by construction; the
substantive question is which compressions of the connectome are sufficient.

<div class="refs">

**References**

Dorkenwald, S., et al. (2024). Neuronal wiring diagram of an adult brain. *Nature*.

Jacobs, R. V., et al. (2024). Overlap and divergence of neural circuits mediating distinct behavioral responses to sugar. *Cell Reports*, 43, 114782.

Kacser, H., & Burns, J. A. (1981). The molecular basis of dominance. *Genetics*, 97, 639–666.

Shiu, P. K., Sterne, G. R., et al. (2022). Taste quality and hunger interactions in a feeding sensorimotor circuit. *eLife*, 11, e79887.

Shiu, P. K., et al. (2024). A *Drosophila* computational brain model reveals sensorimotor processing. *Nature*.

</div>
