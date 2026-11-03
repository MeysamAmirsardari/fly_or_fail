# Theory Note: Silencing as Input Rescaling (PI draft v0.2)

_v0.2 (2026-11-03) replaces v0.1 after the prior-art audit. Changes from v0.1:_
- _"Necessity depends on the operating point" is no longer a claim. It is a design premise of Shiu et al.
  2024, who swept single-neuron silencing over 8 sugar rates `[V-src]`._
- _"Pairwise synergy" is no longer a claim. Jacobs et al. 2024 report that "second-order sugar
  neurons act synergistically" `[V-abs]`._
- _The theory is recast as a **quantitative input-rescaling law**. It predicts the full
  intensity-dependent phenotype of single and paired silencing from one structurally estimable
  quantity per neuron._

All model facts are `[V-src]` from `model.py` (commit 91bdd1e7). Analytic numbers are mean-field
approximations and must be calibrated (§7).

---

## 1. Model, as implemented

```
τ_m dv_i/dt = (v_0 − v_i + g_i)                 τ_m = 20 ms, v_0 = v_reset = −52 mV, v_th = −45 mV
τ_s dg_i/dt = −g_i                               τ_s = 5 ms
presynaptic spike of j (delay 1.8 ms):  g_i += W_ij = s_j · n_ij · w_syn      w_syn = 0.275 mV
on spike: v ← v_0, g ← 0, refractory 2.2 ms
```

- Sensory drive: Poisson jumps of 68.75 mV applied **directly to v** of the stimulated neurons, which
  have refractory period 0. Stimulated GRNs therefore spike as Poisson at the chosen rate λ.
- There is no background activity.
- Silencing *k* zeroes column *k* of W (outgoing synapses only).

**Derived scales (analytic):**
- Unitary PSP peak: 0.043 mV per synapse.
- About 162 synchronous synapses are needed to cross the threshold gap Θ = 7 mV from rest.
- Mean-drive threshold: Σ_j s_j n_ij r_j > D* = Θ/(τ_s w_syn) ≈ 5,091 synapse·Hz.
- A single excitatory edge alone is suprathreshold at presynaptic rate r when n > D*/r
  (n > 34 at 150 Hz).

## 2. The scalar-drive approximation and the rescaling law

Let O(λ) be the readout (MN9 rate) as a function of stimulus intensity λ (GRN rate).

**Approximation A (scalar drive).** O depends on the stimulus and the network only through an
effective drive Λ = λ·F:

&nbsp;&nbsp;&nbsp;&nbsp;O(λ) = g(λF)

Here F is the effective source→target (S→T) transmission capacity and g is a monotone
input–output function with a threshold and saturation.

**Definition (flow fraction).** Silencing neuron *k* removes a fraction f_k of the effective
capacity: F_k = (1 − f_k)F. Then

&nbsp;&nbsp;&nbsp;&nbsp;**O_k(λ) = O((1 − f_k)·λ)**  (the rescaling law)

In words: *silencing k is equivalent to weakening the stimulus by the factor (1 − f_k).*

**Consequences** (all testable without a free parameter once f_k is known):

| # | Consequence | Statement |
|---|---|---|
| C1 | Curve collapse | Silenced dose–response curves collapse onto the intact curve after rescaling the λ-axis by (1 − f_k) |
| C2 | Sensitivity-shift law | λ50′/λ50 = 1/(1 − f_k). The maximum response is preserved if λ can reach the saturating range |
| C3 | Abolition | f_k = 1 ⇔ no λ restores output ⇔ *k* is a source→target vertex cut (dominator) of the functional subgraph |
| C4 | Disinhibition | Silencing an inhibitory neuron on an S→T route gives f_k < 0, a **leftward** shift |
| C5 | Apparent operating-point dependence | Single-intensity necessity is N_k(λ) = 1 − O((1 − f_k)λ)/O(λ). It is large near threshold and small at saturation for the same f_k, so rankings by N_k(λ) change with λ while f_k does not. This **explains** Shiu's "any of 8 frequencies" observation instead of asserting it |

**What breaks A (and how to detect it):**
- A saturating stage downstream of *k* (the maximum drops: a "gain-loss" phenotype).
- Several outputs or routes with different thresholds (the curve shape changes).
- Inhibitory loops whose influence depends on λ.
- Fluctuation- and synchrony-driven transmission (rate scaling ≠ drive scaling).

Each violation shows up as a failed collapse. The **fraction of neurons obeying C1** is itself the
measured answer to "how much of functional necessity is captured by a scalar structural quantity".

## 3. Pairs: inclusion–exclusion of flow fractions

Silencing *a* and *b* removes all transmission through either:

&nbsp;&nbsp;&nbsp;&nbsp;f_ab = f_a + f_b − f_{a∧b}

where f_{a∧b} is the fraction of transmission passing through **both** (shared routes).

- Parallel routes: f_{a∧b} ≈ 0.
- Serial (same route): f_{a∧b} ≈ min(f_a, f_b).

The rescaling law then gives the whole interaction curve, with **no free parameter** given O(·) and
the three fractions:

&nbsp;&nbsp;&nbsp;&nbsp;ε_ab(λ) = O((1 − f_ab)λ)/O(λ) − [O((1 − f_a)λ)/O(λ)]·[O((1 − f_b)λ)/O(λ)]

(Mani et al. 2008 "Product" neutrality; Min and Additive are reported as sensitivity analyses.)

**Synergy window (parallel pairs).** For a steep O with threshold λ*, ε_ab(λ) ≈ −1 in the window

&nbsp;&nbsp;&nbsp;&nbsp;λ*/(1 − max(f_a, f_b))  <  λ  <  λ*/(1 − f_a − f_b + f_{a∧b})

and ε ≈ 0 outside it:
- **below** the window, each single silencing already abolishes the output;
- **above** it, the pair is still redundant.

The window has zero width for serial pairs, where f_{a∧b} = min(f_a, f_b). Its **position and width
are predicted from the fractions alone.** A graded O gives the smooth version from the formula above.

**Why this is not trivially true.** Max-flow is additive over disjoint routes, so it shows no
synergy. The synergy here comes entirely from the threshold nonlinearity in O. The theory claims that
this nonlinearity enters **only through the intact curve O**, i.e. that pair effects are predictable
from (a) the unperturbed input–output curve plus (b) structure. A failure of this prediction means
interactions involve route-specific nonlinearities (coincidence detection at specific convergence
points), which would be an informative negative result.

## 4. Estimating f from structure (the "structure" side of the question)

All estimators are computed **without** running any perturbation simulation (pre-registered):

| Estimator | Information | Definition |
|---|---|---|
| f^G0 (null) | global topology | rank-transformed degree / PageRank / betweenness. These are not fractions; they are used only as ranking baselines |
| f^LIN-S | structure only | 1 − O_lin(G∖k)/O_lin(G), where O_lin = 1_Tᵀ (I − αŴ)⁻¹ Ŵ 1_S on the signed, strength-normalized matrix Ŵ, with α = 0.9/ρ(Ŵ). Exact deletion for each *k* by Sherman–Morrison or a sparse solve |
| f^MF-S | structure only | 1 − MF(G∖k)/MF(G): S→T max-flow on the excitatory subgraph, capacities n_ij (synapse counts), path length ≤ L |
| f^LIN-A | structure + baseline activity | as f^LIN-S, but on the active subgraph at the reference intensity λ_ref, with operating-point gains D = diag(φ′(μ_i)) from a calibrated transfer function: O_lin = 1_Tᵀ(I − τ_s D W)⁻¹ D(·) |
| f^MF-A | structure + baseline activity | max-flow on the active excitatory subgraph with capacities n_ij·r_j(λ_ref) |
| f^emp | simulation (target) | the best-fitting rescaling factor of the simulated silenced curve (the ground truth for §2, *not* a predictor) |

- Overlap terms f_{a∧b} come from the same estimators (inclusion–exclusion on deletions of a, b and {a, b}).
- **Reference intensity.** λ_ref = λ50 of the intact curve (pre-registered). Robustness: λ_ref ∈ {λ25, λ75}.

## 5. Predictions (falsifiable)

| ID | Prediction | Falsified if |
|---|---|---|
| T1 | Most nonzero-effect silencings obey the rescaling law (pure shift preferred over shift+gain by BIC) | pure shift is the minority class |
| T2 | λ50′/λ50 = 1/(1 − f^emp): slope 1 by construction of f^emp. **The real test is T3** | (consistency check only) |
| T3 | Structural estimates predict f^emp: ρ_s(f^LIN-A, f^emp) ≫ ρ_s(centrality, f^emp); f^LIN-A and f^MF-A beat baseline rate r_k and distance-to-T | centrality ≥ flow estimators, or flow estimators ≤ baseline rate |
| T4 | Abolishing neurons (no recovery up to λ_max) are vertex cuts of the active excitatory S→T graph | precision or recall < pre-set bound |
| T5 | Pair curves ε_ab(λ) are predicted by §3 from single-neuron f^emp (dynamics-only test) and from structural f (full test); parallel pairs show a window at the predicted λ | prediction error not better than a shuffled-pair null |
| T6 | The law and the estimator ranking replicate for water→MN9, JON→aDN, left vs right input, v630 vs v783 | sign reversal or collapse failure in a replicate |

## 6. Relation to prior work (see `docs/research/novelty_prior_art.md`)

- **Pharmacology.** C2 is the network analogue of receptor reserve / the operational model of agonism
  (partial receptor inactivation shifts EC50 before reducing the maximum). Cited as an analogy, not
  claimed as new.
- **Genetics.** §3 uses Mani et al. (2008) neutrality functions. The between- vs within-pathway
  intuition (Kelley & Ideker 2005) appears as f_{a∧b}.
- **Neural pairs in connectome models.** These exist descriptively: Jacobs et al. 2024 (Shiu model,
  sugar circuit); Chen et al. 2025 bioRxiv (MN9, escape; "additive"); arXiv 2610.33881 (BANC,
  supra-additive); Towlson & Barabási 2020 (worm, control-theoretic "synthetic essential" pairs);
  Bacik et al. 2016 (worm, flow-based double ablation).
- **Set-level cuts.** A non-peer-reviewed repository (`danilo-lazovic/fly-bottlenecks`) shows that
  silencing a 34-neuron taste→MN9 min-cut abolishes MN9 in a Shiu-parameter model on the male CNS,
  while PageRank and out-strength sets do not. A single-neuron screen with path predictors also
  exists (StrokeSim; ρ = 0.70 static vs 0.81 activity-weighted, n = 21).
- **What appears unclaimed** (abstract-level search, budget-limited; see §0 of the novelty report):
  - the rescaling law;
  - curve collapse as a test of scalar-drive transmission;
  - the EC50-shift law with structural f;
  - abolition = vertex cut at the single-neuron level across intensities;
  - parameter-free prediction of pairwise interaction curves and synergy windows from single-neuron
    fractions.

## 7. Calibration required before use

1. Empirical transfer function φ of a model neuron for Poisson input of known (n, r). This gives the
   gains D for f^LIN-A.
2. The effective threshold D*, compared with the analytic 5,091 synapse·Hz.
3. The intact curve O(λ) on a dense λ grid (the only nonlinearity used by §3).
