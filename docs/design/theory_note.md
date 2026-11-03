# Theory Note: Operating-Point Theory of Functional Necessity (PI draft v0.1)

_Status: DRAFT for red-team review. The derivations use the Shiu et al. LIF model exactly as implemented
in `model.py` (commit 91bdd1e7) `[V-src]`. Numbers marked "analytic" come from the equations below.
They are mean-field approximations and **must be calibrated empirically** (Section 6) before they
are used as predictors._

---

## 1. The model, as implemented

For neuron *i*, with *v* the membrane potential and *g* a synaptic input variable in voltage units:

```
τ_m dv_i/dt = (v_0 − v_i + g_i)        τ_m = 20 ms,  v_0 = −52 mV
τ_s dg_i/dt = −g_i                     τ_s = 5 ms
spike when v_i > v_th = −45 mV  →  v_i ← v_0,  g_i ← 0,  refractory t_ref = 2.2 ms
presynaptic spike of j (delay 1.8 ms):  g_i += W_ij,   W_ij = s_j · n_ij · w_syn,   w_syn = 0.275 mV
```

- s_j = ±1 is the predicted neurotransmitter sign; n_ij is the number of synapses.
- Sensory drive is Poisson, with jumps of 250·w_syn = 68.75 mV applied **directly to v** of the
  stimulated neurons, whose refractory period is set to 0. A stimulated GRN therefore fires almost
  exactly as a Poisson process at the chosen rate λ. The **drive parameter λ is clean**.
- There is no background activity, so a neuron that never spikes has no influence. The reset sets
  g ← 0, which means each output spike "consumes" the input accumulated so far.
- Silencing neuron *k* sets column *k* of W to zero (outgoing synapses only).

Let Θ = v_th − v_0 = 7 mV.

## 2. Single-synapse and mean-drive scales (analytic)

- **Unitary PSP.** For a spike of weight w, the voltage response is
  δv(t) = w·τ_s/(τ_m − τ_s)·(e^{−t/τ_m} − e^{−t/τ_s}).
  It peaks at t* = 9.24 ms with height 0.1575·w, i.e. **0.043 mV per synapse**.
  A synchronous volley from rest therefore needs about **162 synapses** to fire a neuron.
- **Mean drive.** The time average of g is ⟨g_i⟩ = τ_s Σ_j W_ij r_j. In the mean-driven
  approximation, neuron *i* is suprathreshold when

  &nbsp;&nbsp;&nbsp;&nbsp;D_i ≡ Σ_j s_j n_ij r_j  >  D* = Θ / (τ_s w_syn) ≈ **5,091 synapse·Hz**

  Fluctuations lower the effective threshold, and the g-reset and refractoriness raise it, so
  D* must be calibrated (Section 6).
- **Sufficient edge.** A single excitatory connection can drive its target alone when
  n_ij · r_j > D*. That requires n > 204 at r = 25 Hz, n > 51 at 100 Hz, n > 34 at 150 Hz, and
  n > 11 at the refractory ceiling of about 455 Hz.

  **Consequence:** the graph of "functionally sufficient" edges is not fixed. It grows with the
  operating point.

## 3. Threshold margins and local necessity

- Margin: m_i = D_i − D*.
- Contribution of *k* to *i*: c_ik = s_k n_ik r_k.
- Removing *k* lowers D_i by c_ik. To first order, *i* is silenced if c_ik > m_i (for excitatory *k*).

Define the **local necessity ratio**

&nbsp;&nbsp;&nbsp;&nbsp;ν_ik = c_ik / m_i,  where ν_ik > 1 means *k* is locally necessary for *i*.

This ratio combines structure (n_ik) with the operating point (r_k, m_i). It shows that **the same
synapse can be necessary at low drive and redundant at high drive**: as λ grows, the margins m_i
grow faster than the individual contributions c_ik whenever a neuron has many active inputs.

## 4. A ladder of predictors (each rung adds exactly one ingredient)

| Rung | Information used | Predictor of necessity of *k* for output *o* |
|---|---|---|
| L0 | Global topology | degree, strength, betweenness, PageRank, k-core (task-agnostic) |
| L1 | Task-specific topology, uniform gain | walk-sum influence [(I − αŴ)⁻¹]_{o,k} restricted to source→target walks; S–T path counts; S–T max-flow loss ΔF_k (Menger) on the full graph; dominator status |
| L2 | + operating point (baseline activity only) | linear response δr_o ≈ −τ_s r_k [(I − τ_s Φ′W)⁻¹ Φ′ W]_{o,k}, with Φ′ = diag(φ′(μ_i)) the gains of active neurons; active-subgraph max-flow and cuts |
| L3 | + threshold nonlinearity (deterministic) | fixed point of the mean-field rate model r = φ(τ_s W r + I) after deleting column *k* |
| L4 | + spiking fluctuations and timing | full Brian2 LIF simulation (the in-silico ground truth) |
| L5 | + biology | published experimental perturbations (sparse) |

- L1 is a special case of L2 with uniform gains: communicability-type walk sums are linear response
  with Φ′ = αI. Inactive neurons have φ′ = 0, so **L2 sees only the active subgraph**. That is
  exactly what L1 lacks.
- L2 cannot capture recruitment or de-recruitment (threshold crossings). L3 can.
- L3 cannot capture fluctuation-driven firing or synchrony. L4 can.
- The predictive gains between rungs (ΔAUC, Δρ under grouped cross-validation) are the
  quantitative answer to "how much of functional necessity is structure?"

## 5. Two asymptotic regimes and a predicted crossover (core hypothesis, sharpened H-B)

1. **Near-threshold regime** (λ just above the output threshold). Every margin on the
   source→target route is small, so output changes almost linearly with lost drive.
   Necessity ≈ the weighted linear influence of *k* (L1/L2 walk sums, flow share).
2. **High-drive regime** (large λ, with margins ≫ single contributions). Losing any single
   non-bottleneck input is compensated. Silencing *k* abolishes the output only if *k* is an
   **S–T vertex cut** (dominator) in the graph of active, *sufficient* excitatory edges (Section 2).
   Pairs {a, b} produce synthetic deficits iff they form a minimal 2-vertex cut there
   (Menger: redundancy = local vertex connectivity).

**Prediction P1 (crossover).** The best structural predictor *changes with operating point*:
- weighted-influence / flow predictors win near threshold;
- cut / dominator predictors win at high drive;
- classical centralities (degree, betweenness) win in neither regime.

**Falsified if:** one predictor family dominates at every λ, or centrality matches task-specific predictors.

## 6. Flow-fraction law of sensitivity shift (sharpened H-B, quantitative)

Suppose output depends approximately on a scalar effective drive D_o = λ·F, where F is the effective
source→target capacity (flow), and silencing *k* removes a fraction f_k of F. Restoring the same
output then needs λ′ = λ/(1 − f_k). The predicted **EC50 shift** of the input–output (psychometric)
curve is

&nbsp;&nbsp;&nbsp;&nbsp;**λ50′ / λ50 = 1 / (1 − f_k)**, i.e. log(λ50′/λ50) = −log(1 − f_k), slope 1.

- If *k* is a cut vertex, f_k = 1. The curve never recovers: **abolition**.
- If *k* is partially redundant, 0 < f_k < 1: a **sensitivity shift**, with the maximum kept if the
  output can still saturate.
- If the capacity loss is downstream of a saturating stage: a **gain reduction** (O_max falls,
  EC50 is roughly unchanged).

**Prediction P2.** Silencing phenotypes form classes {none, shift, gain-loss, abolition} that are
predicted by structural position (cut vertex → abolition; parallel route → shift). Shift
magnitudes follow the slope-1 law, with f_k estimated from L2 linear response or from active-subgraph
max-flow (both pre-registered). Because a PER dose–response curve under neuron silencing is a
standard fly experiment, this gives an **experimentally testable** prediction.

**Known approximations that may break P2:** inhibition (non-monotone D_o), several outputs with
different thresholds, saturation at intermediate stages, and fluctuation-driven firing. L3 and L4
quantify each departure.

## 7. Pairwise interactions (sharpened H-C)

Let f_x = O_x/O_0 be the normalized output after silencing set x (paired common random numbers,
CRN; see design).
- Primary interaction score (multiplicative, following Mani et al. 2008, pending LIT-B verification):
  ε_ab = f_ab − f_a·f_b.
- Secondary scores: additive, minimum, and λ50-based ε^shift_ab = log(λ50_ab/λ50) −
  log(λ50_a/λ50) − log(λ50_b/λ50).

**Predictions P3:**
- *Parallel converging pairs* (no path between a and b; both on S→T routes; jointly forming a 2-cut
  in the sufficient-edge graph): ε < 0 (synergy), growing in magnitude with λ.
- *Serial pairs* (a upstream of b on the same route): masking, f_ab ≈ min(f_a, f_b), so ε ≥ 0.
- *Non-converging pairs* (routes that do not re-merge before T): ε ≈ 0.
- Under the flow-fraction law, the shift-based interaction for two parallel routes carrying fractions
  f_a, f_b is ε^shift = −log(1 − f_a − f_b) + log(1 − f_a) + log(1 − f_b). This is ≥ 0, because
  (1 − f_a)(1 − f_b) ≥ 1 − f_a − f_b, and it grows sharply as f_a + f_b → 1. It is a closed-form
  prediction for synergy in EC50 space.

  **Sign convention:** in EC50 space, ε^shift > 0 means a larger-than-additive sensitivity loss
  (synergy). In output space, ε_ab < 0 means synergy.

## 8. Calibration required before use (pre-registration item)

1. Empirical single-neuron transfer function φ: drive isolated model neurons with Poisson inputs of
   known (n, r) and fit r_out = φ(D).
2. Empirical sufficient-edge threshold n*(r_pre).
3. Effective D* (compare to the analytic 5,091 synapse·Hz).

These use model neurons only (no connectome-wide perturbation), so they are cheap and are done before the screens.

## 9. What would make this non-novel or trivial (for the red team)

- If prior work already showed that lesion effects in threshold networks depend on drive, and that
  cuts govern at saturation, P1 is incremental. The NOV agent is checking this.
- If the model's default operating point puts almost every neuron deep in one regime, the crossover
  may not be observable in the biologically relevant λ range. The ENG agent's input–output curve decides this.
- If the sugar → MN9 active subgraph is nearly a chain, cut predictors will trivially win.
  We must then report the number of node-disjoint S–T paths (vertex connectivity) per λ.
