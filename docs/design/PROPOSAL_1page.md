# Final Project Proposal (draft v0.9; superseded by PROPOSAL.md / PROPOSAL.pdf)

**Silencing as input rescaling: predicting the intensity-dependent consequences of neuron loss from connectome structure in a whole-brain *Drosophila* model**

BIOE689N/NACS728Z, Network Neuroscience and Brain Dynamic Analysis, Fall 2026. Meysam Amirsardari.

**Background and gap.** Whole-brain connectomes such as FlyWire (Dorkenwald et al. 2024) and
connectome-constrained spiking models (Shiu et al. 2024) let us silence any neuron in silico. Graph
"importance" is often assumed to imply functional necessity. In practice, silencing single neurons in
the fly feeding circuit often has little effect (Shiu et al. 2022; Jacobs et al. 2024). In the
whole-brain model, the effect of silencing a neuron also varies with stimulus intensity: Shiu et al.
screened single-neuron silencing at 8 sugar intensities. We found no theory that predicts from
structure **how** the consequence of silencing a neuron changes with stimulus strength.

**Research question.** Can one structurally estimable number per neuron, the fraction f of
sensory→motor transmission it carries, predict the full intensity-dependent consequence of silencing
it? That consequence covers whether the behaviour is abolished or only made less sensitive, by how
much, and how pairs of silenced neurons interact.

**Hypotheses.**
- **H1.** Classical centrality (degree, betweenness, PageRank) predicts single-neuron necessity
  poorly and inconsistently across stimulus intensities.
- **H2 (input-rescaling law).** Silencing neuron *k* acts like weakening the stimulus. The
  dose–response curve shifts by 1/(1 − f_k) with its maximum preserved, and is abolished only when
  *k* is a source→target vertex cut.
- **H3.** f_k can be estimated without any perturbation simulation, from the connectome
  (linear-response and max-flow fractions) plus baseline activity. These estimates outperform
  centrality and baseline firing rate.
- **H4 (pilot).** Pairwise interactions follow from inclusion–exclusion of flow fractions. Parallel
  pairs show synergy only within a predictable window of stimulus intensity.

**Methods.**
- **Model and readout.** Shiu et al.'s Brian2 leaky integrate-and-fire model of FlyWire v783
  (138,639 neurons). Sugar gustatory neurons are driven at about 8 intensities; the readout is the
  proboscis motor neuron MN9.
- **Single-neuron screen.** Every active neuron (about 400) is silenced individually across
  intensities, with common random numbers for paired comparisons.
- **Fitting.** Silenced curves are fit with shift-only vs shift-plus-gain models.
- **Structural predictors.** Global centralities; task-specific path, flow and dominator measures;
  linear response at the operating point.
- **Statistics.** Pre-registered, with grouped bootstrap by cell type and Holm-corrected primary tests.
- **Controls.** Positive and negative controls, reproduction of the published model outputs, and
  robustness to synaptic weight scale, connectome version (v630/v783) and stimulated hemisphere.
- **Pairs.** A pre-registered pilot of about 60 pairs stratified by structural relation.

**Predicted outcomes.**
- Most effect-bearing neurons obey the rescaling law.
- Flow-fraction estimators rank neurons far better than centrality.
- Abolition is confined to vertex cuts.
- Parallel pairs show intensity-limited synergy.

Each prediction has a stated falsification criterion. Failure of the law would itself map where
connectome structure stops being sufficient to predict function.

**Limitations.**
- Results describe the model, not the fly.
- Experimental labels are few (about 6–10 cell types), so they are a sanity check only.
- The model lacks neuromodulation and gap junctions.

**Deliverables (Dec 10).**
- The rescaling test.
- A structure-vs-function predictor comparison.
- Pair pilot results.
- An experimentally testable prediction: silencing shifts the PER sucrose dose–response curve by a
  factor set by f.
