# Red-Team Review: "Silencing as Input Rescaling" (PROJECT_DESIGN v0.9)

_Reviewer: RED (adversarial). Date: 2026-11-03. Reviewed: `PROJECT_DESIGN.md` v0.9, `theory_note.md`
v0.2, `analysis_plan_draft.md` v0.1, `PROPOSAL_1page.md` v0.9, `fulltext_verification.md`,
`novelty_prior_art.md`, `lit_A/B/C`, `STRATEGY.md`, `DECISIONS.md`, `feasibility/logs/*`,
`/home/user/external/Drosophila_brain_model/{model.py,figures.ipynb}`._

_Evidence tags as in STRATEGY §5. `[V-src]` = I inspected code/data this session. `[V-full]` = I read
the extracted full text. `[MEM]` = my background knowledge, unverified, not citable._

---

## (1) Verdict and 5-line summary

**Verdict: MAJOR REVISION REQUIRED BEFORE FREEZE. Do not freeze v0.9 as written.** The core idea is
good and the positioning is defensible, but the primary confirmatory test is biased toward its own
hypothesis, the project as scoped cannot run in the time left, and two documents define `f`
incompatibly. All three are fixable today.

1. **The headline test (P1) cannot fail.** BIC between two nested curve models, with 8 trials, an
   over-dispersed likelihood, and a grid that partly saturates, prefers "shift-only" whenever the data
   are uninformative. P1 measures statistical power, not the law. Replace with an absolute
   goodness-of-fit against measured trial noise, plus an explicit "uninformative" class.
2. **The schedule is infeasible by roughly 4×.** The MVP is ~59 CPU-h ≈ 20 h wall on 3 workers, with
   an unvalidated simulator, inside ~1.5 days that must also hold analysis, figures and slides.
3. **`f` means two different things** (theory: fraction of capacity removed; `analysis_plan` §B:
   `f_k = O_k/O_0`). In a pre-registration this is disqualifying. Rename one today.
4. **Two claims are overstated:** the pair inclusion–exclusion is an algebraic identity, not a
   prediction; and "PER EC50 shifts by 1/(1−f)" is false unless concentration→GRN-rate is linear.
5. **The best asset is being left on the table.** Shiu's archived Fig. 1F CSVs are a 200-neuron × 8-
   intensity × 30-trial single-silencing dataset — exactly the RQ2 dataset, at zero compute cost.
   Fetching them today is the highest-value action available.

---

## (2) Issues table

Severity: **Critical** = must fix or the result is uninterpretable/unobtainable. **Major** = would
draw a reviewer's rejection or materially weaken a claim. **Minor** = correctness/presentation.

| ID | Sev | Section | Problem | Concrete fix |
|---|---|---|---|---|
| **C1** | Critical | §5.6 P1; theory T1 | P1 is "proportion of neurons where ΔBIC>2 favours shift-only vs shift+gain". Nested model selection prefers the simpler model when data are uninformative. With 8 trials, MN9 SEM ≈ 3%, single-neuron effects of −5.6%…+6.2% `[V-src]`, and a grid that saturates at the top, most neurons will yield ΔBIC>2 *for lack of power*. The primary test therefore confirms H2 under the null. | Replace P1 with a **two-part test**: (i) an *absolute* collapse test per neuron — calibrated χ²/posterior-predictive p of the shift-only fit against the empirically measured trial-to-trial variance, so a neuron can fail to collapse; (ii) a **three-way** comparison (shift-only / shift+gain / free Hill with independent λ50, slope, Emax) by **cross-validated** held-out-seed predictive error, not BIC. Add a pre-registered **"uninformative"** class: neurons whose λ range does not span enough of the rising phase to separate shift from gain (declare the discriminability criterion numerically before running). Report the shift fraction **among informative neurons** as primary, and the informative fraction itself as a headline number. |
| **C2** | Critical | §4, §7; D-007 | Infeasible. Measured ~5 s/trial in a persistent Brian2 process, ~41 s/trial through the author's loky path `[V-src: 04_repro_run.log]`. MVP ≈ 59 CPU-h ≈ 20 h wall on 3 workers, with the fast simulator still unvalidated, 4 shared cores, and ~1.5 days that must also absorb analysis, figures, report and slides. No slack for a simulator that fails its gates. | Adopt the minimum design in §(7): Tier A ≈ 80–120 neurons, 5 λ levels, 12–15 trials ⇒ ≈ 13–15 CPU-h ≈ 5 h wall. Freeze the descoping order in §(7) **today**, in `DECISIONS.md`, so cuts need no new decision tomorrow. Highest priority: fetch Shiu's Fig. 1F CSVs (see C3). |
| **C3** | Critical | §4 row "Shiu raw simulation outputs"; `fulltext_verification.md` §7 | The archive's `fig_1f_*_hz_rate.csv` files are the top-200 × 8-frequency × 30-trial single-silencing MN9 dataset — i.e. the RQ2 target variable, already computed by the original authors on v630 with their exact grid `[V-src: figures.ipynb cells 12–14]`. Only the Fig. 1E activation CSVs were uploaded. The design lists this as an optional "free pilot". It is not optional: it is better powered than anything simulable in the time left. | Make retrieval of `fig_1f_{50..120}_hz_rate.csv` **and** `_std.csv` the first action today (Edmond doi:10.17617/3.CZODIW). If obtained, re-base RQ2 on it: 200 neurons × 8 λ × 30 trials, zero compute. Pre-register the fallback now so the analysis plan is identical either way. Note two caveats to pre-register: the CSVs give per-condition **mean and SD over 30 trials**, not trial-level counts (so use a Gaussian/quasi-likelihood with the reported SD — which is the right choice anyway, see C5), and the 50–120 Hz grid ≈ 1–2.4·λ50 does **not** reach deep saturation, so Emax is weakly identified and the C1 informativeness gate matters even more. |
| **C4** | Critical | theory §2/§4 vs `analysis_plan` §B | `f` is defined incompatibly. Theory: `f_k` = fraction of S→T capacity removed, so `O_k(λ)=O((1−f_k)λ)`. `analysis_plan` §B: `f_k(λ) = O_k(λ)/O_0(λ)`, i.e. normalised output (theory's `w`). PROJECT_DESIGN §5.3 then writes `ε_ab = f_ab − f_a·f_b` using the §B sense while citing the theory sense. Two different quantities, one symbol, across the documents being frozen. | Rename globally **today**: `f_k` = rescaling fraction (theory) only; `w_k(λ) = O_k/O` = normalised output; `N_k(λ) = 1 − w_k`. Rewrite §5.3's ε row as `ε_ab(λ) = w_ab − w_a·w_b` and delete the `f_ab − f_a f_b` form. Supersede `analysis_plan_draft.md` explicitly (it is already stale on P1–P3 numbering too) or delete it from the pre-registration set — do not freeze two documents with conflicting notation. |
| **C5** | Critical | §5.3 f^emp; §5.6 | Likelihood mis-specification, in the direction that favours H2. MN9 counts are **underdispersed**, not Poisson: 67.0 ± 6.6 Hz over 1 s ⇒ Fano ≈ 0.65 `[V-src: 04_stored_results_inspect.log]`, as expected from a refractory threshold unit. A Poisson likelihood overstates noise; negative binomial can only *add* dispersion, never remove it. Both inflate the tolerance of the collapse fit and bias BIC toward shift-only. Additionally, CRN makes conditions **paired on the same Poisson realisations**, so counts are not independent across conditions and the per-condition likelihood is wrong for the contrast. | Fit on a **Gaussian/quasi-likelihood with an empirically estimated variance function** `Var = φ(μ)` calibrated on the intact replicate trials (a mean–variance curve across the dense λ grid), not an assumed family. Do model selection by **held-out-seed cross-validation**. For contrasts, use the **paired per-seed differences** (which is what CRN buys) with a seed-level bootstrap. State explicitly that CRN pairing is used for contrasts and broken (independent seeds) for any absolute goodness-of-fit. |
| **M1** | Major | theory §3; §5.6 P5; RQ4 | The pair inclusion–exclusion is **vacuous as stated**. `f_{a∧b}` is to be obtained "from the same estimators (inclusion–exclusion on deletions of a, b and {a,b})" (theory §4), i.e. `f_{a∧b} := f_a + f_b − f_ab^struct`. Substituting back returns `f_ab^pred ≡ f_ab^struct`. No prediction is made; it is an identity. The real content is only "structural f for the pair predicts empirical f for the pair" — RQ3 applied to pairs. "No free parameters" is therefore true but empty. | Keep the pair arm, drop the derivation claim. State the two genuinely distinct tests: **(T5a, dynamics-only)** predict `w_ab(λ)` from the *singly measured* `f^emp_a`, `f^emp_b` and an **independently computed** overlap `f_{a∧b}` (computed directly as shared-route flow, e.g. flow through both a and b, *not* by back-solving); **(T5b, full)** same from structural f. Only T5a/T5b have content. Delete "with no free parameters from f_a, f_b and their overlap" from §0 and the proposal. |
| **M2** | Major | §0 bullet, §5.1 "experimentally testable prediction"; proposal deliverables | "Silencing shifts the PER sucrose dose–response by a factor set by f" is **not implied** by the law. The invariance result holds on the **GRN-rate axis**: if PER = h(O) with h monotone and the half-maximal PER level O\* is attainable in both conditions, then λ ratio = 1/(1−f), invariant to h. Converting to **sucrose concentration** requires the concentration→rate map φ; for the usual saturating (Hill-shaped) GRN dose–response the concentration ratio is *not* 1/(1−f) and depends on where on φ you sit. | State the prediction on the **GRN firing-rate axis** ("the dose–response shifts rightward by 1/(1−f) in GRN drive"), and present the concentration version only as a conditional corollary with φ stated, plus a sensitivity analysis over plausible Hill φ. Also state the two preconditions: h identical across conditions, and O\* still attainable after silencing (so the prediction is **defined only within the shift-only class** — in the gain-loss/abolition classes there is no EC50 ratio). |
| **M3** | Major | §5.6 P4; theory C3/T4 | "Abolition ⇔ vertex cut" is wrong in one direction and the test is underpowered. (a) **cut ⇒ abolition** is sound; **abolition ⇏ cut**: in a threshold network, parallel routes can exist graph-theoretically yet never cross threshold at any physiological λ, giving abolition without a cut. So recall is predicted to be low *by the theory itself*, yet P4 demands precision **and** recall ≥ 0.8. (b) "Abolition" is defined as no recovery up to λ_max, and λ_max ≈ 4·λ50 ≈ 200–240 Hz with >300 Hz declared non-physiological. A neuron with f = 0.8 needs 5·λ50 to recover, so it is *classified* as abolishing although it is a pure shift: the category is **range-dependent** and "abolition only for f→1" is partly definitional. (c) The design itself rates "too few abolishers" as medium–high risk; with <5 positives, exact CIs on precision/recall are uninformative. | Reframe. (i) Rename the class **"no recovery within the tested range (λ ≤ λ_max)"** and state λ_max numerically. (ii) Test the **sound direction only** as confirmatory: among single-vertex S→T cuts, the proportion showing no recovery (one-sided exact binomial); report the converse descriptively. (iii) Replace the binary test with a **monotone-trend test of f^emp on cut status / on min-cut participation count**, which uses all neurons and has real power. (iv) Define the graph unambiguously: super-source over S, single target T, **dominators of T** in the directed graph = the single-vertex S→T cuts (Lengauer–Tarjan); say whether the graph is unsigned, excitatory-only, and/or activity-restricted, and report all three as pre-specified variants. |
| **M4** | Major | §5.1, §4 (annotations row) | MN9 readout is ambiguous and partly broken. `MN9_R` (720575940645521262) is **absent from v783** `[V-src: 08_annotations_check2.log]`; the surviving ID 720575940660219265 is the notebook's `id_mn9` but is annotated **side = right** while the stimulated "sugar_GRN_right" set is annotated **side = left** — a consistent L/R label flip `[V-src]`. So the primary readout is the **contralateral** MN9 (which Shiu 2024 reports responds more strongly `[V-full]`). Worse, `analysis_plan` §B sets O(λ) = **average of left and right MN9**: averaging two differently-shifted, differently-thresholded sigmoids *guarantees* a shape change under silencing and so **biases RQ2 against itself** by construction. §5.1's "plus its v783 contralateral partner after re-mapping" relies on an unverified homolog mapping. | Pre-register **one** primary readout: the single MN9 present in v783 (720575940660219265), described explicitly as contralateral to the stimulated GRNs. **Never average the two MN9s.** Report the second MN9 as a separate, secondary curve. If the partner is needed, identify it by `cell_type == CB0701` + `side` (annotation gives left = 720575940618238523 `[V-src]`) and state the mapping and its uncertainty in the pre-registration. Fix the L/R convention in one place and add an assertion to the harness. |
| **M5** | Major | §5.2 candidate set; §5.6 P3 | Selection confound in the hypothesis's favour. The candidate set is neurons with ≥1 Hz at λ_max in the **intact** model. Activity correlates with f, so the sample is activity-selected; evaluating "flow beats baseline rate" (P3) on a range-restricted sample **attenuates the competitor** and favours the flow estimators. | Add a pre-registered **stratified sample of low-rate neurons** (0 < r < 1 Hz) that lie on S→T paths, to restore the range of the baseline-rate predictor. Report P3 both on the restricted and the extended sample. State that silent neurons have exactly 0 effect by construction and are excluded analytically, not by a data-dependent filter. |
| **M6** | Major | §5.4, §5.6 P2 | Distance-to-output confound. `f^LIN-A` is an α-discounted walk sum, so it is monotonically entangled with hop distance to T; neurons one hop from MN9 get large f almost automatically. "Flow beats global centrality" may reduce to "distance to MN9 beats global degree", a far weaker claim. | Report, as pre-registered secondary: **partial** Spearman of f^struct with f^emp controlling for hop-distance-to-T and baseline rate; and a **within-layer** analysis stratified by hop distance to T. Add distance-to-T to the L0 competitor set (it is already in L1 — promote it to a named competitor in P2, not just a listed predictor). |
| **M7** | Major | §5.6 "Grouping"; effect sizes | Power is overstated because the effective n is the number of **cell types**, not neurons. I counted, over the author's stored v630 run with v783 annotations: **391 neurons ≥1 Hz at 200 Hz → 207 distinct `cell_type` labels** (110 types with ≥2 active members, max 9); at 100 Hz, 347 → 186 types `[V-src, computed this session]`. So the grouped bootstrap has n_eff ≈ 190–210, not ~400. My SE approximation for Δρ (ρ_flow 0.50 vs ρ_cent 0.35, inter-predictor correlation 0.3–0.6) gives power for the stated MEI Δρ ≥ 0.15 of **0.71–0.89 at n = 200**, falling to **≈ 0.4 at n ≈ 70** (the descoped 100-neuron screen). | State n_eff explicitly in the pre-registration. Prefer a **Hotelling–Williams-type test for dependent correlations** (more efficient than bootstrapping a difference) with the grouped bootstrap as the sensitivity analysis. If the screen is descoped below ~150 types, **demote P2 to secondary** and say so in advance — or use the Fig. 1F archive route (C3) to keep n at 200. Also: 46 of 391 active neurons have no v783 annotation (ID drift); treating them as bootstrap singletons is anti-conservative if they are homologs of labelled types — pre-register the rule. |
| **M8** | Major | §5.6 P2 | "max over L0 of ρ_s" is a **selected maximum**; its bootstrap CI is not a standard quantity. If the max is chosen once on the full data and then bootstrapped, the CI is anti-conservative. | Re-select the maximising L0 predictor **inside each bootstrap resample**. Pre-register the exact L0 list (closed set) so the max is over a fixed family. Note the direction: selecting the max is conservative for the *point* estimate but not for the CI. |
| **M9** | Major | §5.6 Holm family | Five Holm-corrected tests are declared co-primary, but they are not of equal importance and P2/P3 are near-duplicates (both Δρ against f^LIN-A). Holm over a heterogeneous family costs power on the one test that matters. | Declare **one** primary confirmatory test (recommend the revised C1 collapse test, or P2 if the archive route lands), with P2–P5 as **secondary confirmatory** under their own Holm family. State this ordering in the frozen commit. |
| **M10** | Major | §5.2 pairs | Pairs are selected on the **predictor** (0.1 ≤ f^LIN-A ≤ 0.6), then the predictor is tested. Range restriction on the predictor attenuates the very correlation P5 evaluates, in an uncontrolled direction relative to the shuffled-pair null. | Select pairs by **structural relation strata** (parallel-converging / serial / non-converging) crossed with **single-neuron f^emp** magnitude (outcome data for singles, not for pairs — legitimate and better justified, and the design already contemplates a "dynamics-only" test). Keep the f range wide. Pre-register the strata sizes. |
| **M11** | Major | theory §3; §5.3 | `ε(λ)` has a **0/0 singularity** exactly where the effect is. `w = O_k/O` is undefined where the intact `O(λ) = 0` (below threshold) and has near-infinite variance just above it — which is where the predicted synergy window sits. | Evaluate ε only where the intact curve exceeds a **pre-set SNR floor** (state it numerically, e.g. O ≥ k·SE(O)), or model counts directly in a hierarchical GLM on the absolute scale and derive ε as a contrast with propagated uncertainty. Report `w_a`, `w_b`, `w_ab` always (the design already says this — keep it) and never ε alone. |
| **M12** | Major | §5.1, RQ5 external arm | Input-set contamination for the external-validation arm. Shiu's notebook "sugar" set of 21 contains, by v783 annotation: 9 LB3c sugar, 2 LB3b sugar/low_salt, **5 LB3d high_salt/heavy_metal**, 4 LB4b putative_attractive `[V-src: 08_annotations_check2.log]`. Shiu 2022's behavioural work used a **different set of 17 candidate sugar GRNs** `[V-full]`. Driving ~24% high-salt GRNs contaminates the f ranking of the very second-order types used for external validation. | Keep Shiu's 21 as the **reproduction** input set. For the **external-validation arm, make the annotation-pure sugar set (LB3c + LB3b = 11 neurons) primary**, pre-registered. Report the f-ranking under both and state the concordance. |
| **M13** | Major | novelty §2; theory §6; proposal | Missing prior framework. `f_k` is, formally, a **finite-change flux control coefficient** from metabolic control analysis; "flux is nearly insensitive to any single enzyme because control is shared" (Kacser & Burns 1981, summation theorem) is the same statement as "single-neuron silencing has small effect because f is small". `lit_B` §4.10 already found and URL-verified this `[V-abs]`, but neither the theory note nor PROJECT_DESIGN cites it, while receptor reserve *is* cited. An MCA-literate reviewer will call this a rediscovery. | Cite both frameworks and position the work as a **bridge** (see §(5)). This *strengthens* the contribution: the summation theorem supplies an extra falsifiable prediction the design currently lacks (Σf over a layer cut), and it pre-empts the "isn't this just X?" referee. |
| **m1** | Minor | §5.2 silencing | Silencing zeroes **outgoing** synapses only `[V-src: model.py silence()]`, and the implementation is a string expression `syn.w['{} == i'] = 0*mV` that already produced a namespace-collision warning in the repro run (`'i' … also exists in the run namespace`) `[V-src: 04_repro_run.log]`. It resolved to the intended variable here, but the code is one collision away from silently silencing nothing. | Add a **unit test to the harness**: after silencing k, assert `(syn.w == 0).sum()` increased by exactly k's out-degree. This is the cheapest high-value control in the whole design and it is currently absent. Also note: silencing **MN9 itself gives f = 0 by construction** (its own rate is unaffected) — use as a pipeline negative control. |
| **m2** | Minor | theory §1 | `eq_rst = 'v = v_rst; w = 0; g = 0*mV'` assigns `w`, which is **not** a NeuronGroup variable (the model has v, g, rfc) `[V-src: model.py]`. It appears to be dead code. Harmless if so, but it is in the model the whole project rests on. | 10-minute check: confirm Brian2 treats it as an unused auxiliary and that no synaptic weight is touched at spike time. Record the result in the pre-registration. |
| **m3** | Minor | theory §1 | Two extra nonlinearities are unstated: `dg/dt` carries `(unless refractory)`, so **g is clamped (not decaying) during the 2.2 ms refractory period** while `on_pre: g += w` continues to accumulate; and `g ← 0` at spike **discards** accumulated conductance. Both break exact rate-linearity and both matter for the scalar-drive argument. | Add to theory §2 "What breaks A". They are the mechanistic reason for the coincidence/synchrony objection in §(3) below. |
| **m4** | Minor | §4, §5.5 | The reproduction gate is stated but the **acceptance tolerance is not**. "Within Poisson CIs" is the wrong family given the measured underdispersion (C5). | State the gate numerically: e.g. MN9 mean rate within X% and within the empirical 95% interval over 30 trials, on the named stored files. Pre-register X before running. |
| **m5** | Minor | §5.5 nulls | The design concedes rewired nulls may leave MN9 silent, making a simulated null uninformative, and then still lists them. | Keep **only** the structural nulls and the type-label permutation (as §5.5 already proposes) and delete the simulated rewired null from the MVP. Saves compute and a dead end. |
| **m6** | Minor | §1.1 table | The "91% of 164 predictions" figure is correctly flagged as uncitable in `fulltext_verification.md`, but §1.1's row still references the circulating figure. | Delete the parenthetical from §1.1; cite instead the verified robustness numbers (90.2%/95% agreement; 85%/88% accuracy) `[V-full]`. |
| **m7** | Minor | §3 RQ5 | "Hemispheres differ in GRN count: 21 right vs 10 left" is reported as a limitation but not as a **design consequence**: the left-input replicate has roughly half the drive, so its λ axis is not comparable to the right's. | Pre-register that the L/R replicate compares **f ranks** (Kendall τ), not λ50 values, and that the left curve is re-referenced to its own λ50. |
| **m8** | Minor | §5.2 recruitment control | Under-used. A random 50% of GRNs at fixed λ is the **cheapest non-trivial test of the scalar-drive assumption** (it probes whether removing specific W-columns equals scaling all of them), and it needs no 400-neuron screen. It is currently one row in a table. | Promote to a named confirmatory test with its own prediction (`O_half-set(λ) ≈ O(f·λ)` with f estimated from the removed GRNs' flow share) and keep it in the design to the very last descoping step. Note it is only a clean test if the GRNs are heterogeneous in outgoing weights — which they are (M12). |

---

## (3) Math check, with counterexamples

### 3.1 PSP scale and D\* — correct

I re-derived both from `model.py` `[V-src]`. For `τ_m dv/dt = −v + g`, `τ_s dg/dt = −g`, unit jump
`w_syn = 0.275 mV`:

- unitary PSP peak = `w·τ_s/(τ_s−τ_m)·(e^{−t*/τ_s} − e^{−t*/τ_m})` at `t* = ln(τ_m/τ_s)/(1/τ_s − 1/τ_m)`
  = **0.0433 mV at t\* = 9.24 ms**. Theory says 0.043 mV. ✔
- synchronous synapses to cross Θ = 7 mV: 7/0.0433 = **161.6 ≈ 162**. ✔
- mean-drive threshold `D* = Θ/(τ_s·w_syn) = 7/(0.005 × 0.275) =` **5090.9 synapse·Hz**. ✔

Two caveats the theory note should state. `D*` is the condition for the **mean** of v to reach
threshold at steady state; a unit fires *below* `D*` in the fluctuation-driven regime, which is
precisely the regime single-neuron silencing probes (small changes near margin). And `D*` ignores
`g ← 0` at spike and the refractory clamp on `dg/dt` (m3), both of which make the true threshold
drive **higher** than 5091 for an actively firing unit. Treat 5091 as a lower bound and calibrate
empirically (theory §7 already requires this — good).

### 3.2 When is `O_k(λ) = O((1−f_k)λ)` exact in *this* model?

The stimulated GRNs get 68.75 mV Poisson jumps **directly to v** with refractoriness 0, so each jump
spikes immediately (68.75 ≫ 7 mV gap): λ enters the model **only** as the rate of the GRN Poisson
processes `[V-src]`. That is the cleanest possible setting for the law, and it makes the following
precise.

**Exact cases (and why two of them make RQ2 uninformative):**

1. **k is a stimulated GRN, and the GRN set is homogeneous in outgoing weight vectors.** Then
   deleting one of N GRNs removes exactly a 1/N share of every downstream drive, which is identical
   to scaling λ by (N−1)/N. `f_k = 1/N` **exactly**, for any downstream nonlinearity. → **The law is
   exact by construction for the ~20 GRNs.** They are in the candidate set (25 sensory neurons are
   active `[V-src]`). Including them in the P1 tally inflates the shift fraction with guaranteed
   successes. **They must be excluded from P1 and reported separately as a positive control.** (In
   reality the GRNs are *not* homogeneous — M12 — so they are an approximate, not exact, case; which
   makes them a genuinely useful *calibration* of how much heterogeneity costs.)
2. **`f_k = 0`:** k has no S→T path, or k is downstream of T, or k is T itself (silencing MN9 leaves
   MN9's own rate untouched, m1). Then `O_k ≡ O` and the law holds exactly with f = 0. → **Trivially
   true, and it is why the "effect-bearing" gate is load-bearing.** The gate must be pre-registered
   with a power-aware threshold, not an eyeball one.
3. **O flat over the tested range.** If the grid sits in saturation, `O((1−f)λ) ≈ O(λ) ≈ Emax` for all
   tested λ and any moderate f. Shift-only fits; shift+gain does not improve; ΔBIC > 2. → **The law
   "holds" because the experiment asked nothing.** This is C1 in one line. Quantitatively: 100 Hz
   gives ≈ 72–80% of maximal MN9 `[V-full + V-src]`, so λ50 is well below 100 Hz and a grid topping
   at 4·λ50 ≈ 200–240 Hz spends a substantial share of its points in saturation.
4. **A single linear chain with one monotone output stage.** If every route from S to T passes through
   one stage whose output is a monotone function of total drive, and all upstream transmission is
   linear in rate, the law is exact. This is the content of Approximation A; it is exact for a
   feedforward rate-linear network with a single saturating output.

**Trivial-failure cases:**

5. **λ-gated inhibition.** Let k be inhibitory and recruited only above λ_on (it is silent below, since
   the model has no background activity). Then silencing k does nothing for λ < λ_on and shifts the
   curve leftward for λ > λ_on. **No single f reproduces both halves** — the curve changes shape, not
   scale. Since the model has 0 spontaneous activity and recruitment is graded in λ, *every*
   inhibitory route neuron is of this type to some degree. C4/"disinhibition gives leftward shifts" is
   therefore the **weakest** consequence in the set, and `f_k < 0` is not generally well defined.
   Predicting that inhibitory neurons show "f < 0" is predicting the sign of a quantity whose
   existence is in question.
6. **Multiple routes with different thresholds.** Let `O(λ) = σ₁(λ) + σ₂(λ)` with thresholds λ₁ ≪ λ₂.
   Silencing a neuron carrying only route 2 gives `O_k = σ₁`, which is **not** `O(cλ)` for any c:
   removing a high-threshold route lowers the high-λ end while leaving the low-λ end untouched; rate
   rescaling does the opposite. In a 390-neuron active network with 56 active descending and 21 active
   motor neurons `[V-src]`, multi-route structure is the generic case — which is why "shift-only for
   the majority" is an **aggressive** prediction, not a safe one.
7. **Averaging two outputs.** `O = ½(O_L + O_R)` with different λ50s is case 6 exactly. This is M4:
   the `analysis_plan` readout definition manufactures a law violation.
8. **Coincidence-driven transmission.** This is the deepest objection and it is specific to this
   model. A unit needing ~162 near-synchronous synapses (3.1) fires on *coincidences*, whose rate
   scales like λ² (pairwise) within a window, not λ. Silencing k removes one spike **stream**;
   lowering λ scales **all** streams. For a linear rate-summing target these coincide; for a
   coincidence detector they do not. Combined with `g ← 0` at spike and the refractory clamp (m3),
   which make a unit's output depend on input *timing* and not only on mean drive, this guarantees
   residual, structured failure of the law. **This is a prediction the design should make and test,
   not a caveat:** collapse should fail preferentially for neurons whose downstream targets operate
   near threshold with high convergence. That turns the honest expected negative result into a
   positive finding (and it is close to `lit_B` §2.5's margin index — connect them).

**Is RQ2 non-trivial?** Yes — but **only after** three of the above are excluded by pre-registration:
(a) exclude GRNs from the primary tally (case 1); (b) exclude f ≈ 0 neurons by a pre-registered,
power-aware effect gate (case 2); (c) gate on **informativeness** so saturated/noise-dominated curves
are classified "uninformative" rather than "shift" (case 3). Without all three, P1 is a
foregone conclusion. With them, RQ2 is a real and interesting test, because cases 5–8 give genuine
failure mechanisms that the active network will certainly contain in some proportion — and *that
proportion* is the finding.

### 3.3 The EC50 shift 1/(1−f) and invariance to monotone output links

Given the law and a strictly increasing O, the shift is exact and immediate: if `O(λ_a) = O*` then
`O((1−f)λ_b) = O*` ⇒ `λ_b = λ_a/(1−f)`, for **any** target level O\*. Hence:

- **Invariance to monotone links is true, with two conditions.** If PER = h(O), h monotone and
  identical across conditions, then the half-maximal-PER level corresponds to a **fixed O\***, so the
  λ-ratio is 1/(1−f) regardless of h. ✔ Conditions: (i) h unchanged by the perturbation; (ii) O\*
  **still attainable** after silencing. (ii) fails exactly in the gain-loss and abolition classes, so
  the invariance is a statement *within* the shift-only class — it cannot be used to argue that the
  class assignment doesn't matter.
- **It is not invariant to the concentration→rate map** (M2). This is the error in the "experimentally
  testable prediction": a λ-ratio of 1/(1−f) maps to a concentration ratio of 1/(1−f) only if φ is
  linear over the range. For a saturating GRN dose–response the concentration ratio is larger and
  position-dependent. Fix: state the prediction in GRN rate; give the concentration version as a
  corollary with φ explicit.
- **T2 is vacuous and the design says so** — correct, and worth keeping that honesty. But note the
  consequence: **the EC50-shift law is never independently tested.** `f^emp` is *defined* as the
  best-fitting rescaling factor, so "λ50′/λ50 = 1/(1−f^emp)" is a reparameterisation. The only real
  tests are (i) does the one-parameter rescaling fit at all (C1), and (ii) does structure predict
  f (P2). §0's consequence list should not present C2 as an independently confirmed law.

### 3.4 Abolition ⇔ vertex cut — which graph, and which direction

Covered in M3. The formal points: with 20 sources and 1 target, single-vertex S→T cuts are the
**dominators of T** with respect to a super-source over S (Lengauer–Tarjan; `lit_B` §5.4 `[V-abs]`).
Because `silence()` removes only **outgoing** edges, silencing k is exactly vertex deletion as far as
S→T paths *through* k are concerned — so the graph-theoretic object is right. Three unresolved
specification choices that change the answer and must be pre-registered: unsigned vs excitatory-only
vs activity-restricted; whether GRNs/T may themselves count as cuts; and λ_max. And the logical
direction matters: cut ⇒ no recovery is sound; no recovery ⇒ cut is **false** in a threshold network,
so demanding recall ≥ 0.8 is demanding that the theory's own failure mode not occur.

### 3.5 Pair inclusion–exclusion and the synergy window

**Inclusion–exclusion.** `f_ab = f_a + f_b − f_{a∧b}` presumes f is an additive *measure* over routes.
It is not, for either estimator: max-flow loss is not additive (deleting two nodes can cost more than
the sum of their individual losses when the min-cut restructures — `lit_B` §2.3 makes the related
point that flow is additive across disjoint parallel routes and therefore *cannot* see
threshold-induced synergy `[V-abs]`), and for the resolvent `(I − αŴ)⁻¹` a two-node deletion is a
rank-2 update, not a set subtraction. So the identity is an approximation of unquantified error — and,
as written (M1), it is then made vacuous by defining `f_{a∧b}` through it.

**Window bounds — correct, with a domain caveat.** For a step O with threshold λ\*, single a is dead
for λ < λ\*/(1−f_a) and alive above; the pair is dead for λ < λ\*/(1−f_ab). Since f_ab ≥ max(f_a, f_b),
on `λ*/(1−max f) < λ < λ*/(1−f_ab)` both singles are alive (w = 1) while the pair is dead (w_ab = 0),
so `ε_P = 0 − 1·1 = −1`. ✔ The stated bounds are right. Caveats: the result needs λ > λ\* for O to be
nonzero at all, and `ε` is undefined where O = 0 (M11). For **serial** pairs
`f_{a∧b} = min(f_a,f_b)` ⇒ `f_ab = max(f_a,f_b)` ⇒ **zero width**, and `ε = w_max − w_a w_b ≥ 0`
automatically. So the serial prediction is near-tautological in a no-background threshold model — the
novelty report already said this `[V-abs]` and the design already demotes it to a sanity control.
Correct call: keep it a control, and note that it means the pair arm has **one** informative class
(parallel) with ~20 pairs in the pilot. That is a pilot, not a test; label it so.

### 3.6 Rate rescaling vs GRN recruitment

For N independent Poisson sources at rate λ, the aggregate input spike count is Poisson(Nλ), so for a
purely **rate-summing** target, halving N at fixed λ and halving λ at fixed N are identical. They
differ exactly when (a) GRNs have **different outgoing weight vectors** — removing a subset removes
specific W-columns, whereas scaling λ scales all columns uniformly; and (b) the target is
**coincidence-sensitive** (3.2 case 8), since the two manipulations alter higher-order input
statistics differently. Both hold here (M12 shows the GRN set is heterogeneous: 4 annotated subclasses
across 21 neurons `[V-src]`). So the recruitment control is a **genuine, cheap, and currently
under-used** test of the scalar-drive premise at the input layer (m8). Promote it.

---

## (4) Statistics redesign, with power estimates

All numbers below are mine, computed this session; the derivations are stated so they can be checked.

### 4.1 Grounded effective sample size

Over the authors' stored v630 run with v783 annotations `[V-src, computed this session]`: 391 neurons
≥ 1 Hz at 200 Hz drive map to **207 distinct `cell_type` labels** (110 types with ≥ 2 active members,
largest type 9 members; 46 of 391 unannotated from ID drift). At 100 Hz: 347 → **186 types**. Since
all CIs resample cell types (correctly — L/R homologs and type members are near-duplicates),
**n_eff ≈ 190–210 for the full screen**, and ≈ 70 for a descoped 100-neuron screen.

### 4.2 P1 (revised) — collapse

Replace model selection with absolute fit (C1) + CV (C5). Keep a binomial summary as the headline,
but computed over **informative, non-GRN, effect-bearing** neurons only (3.2).

One-sided exact binomial against H0: p ≤ 0.5, power by number of informative neurons n and true
shift fraction p:

| n | p = 0.6 | p = 0.7 | p = 0.8 | (at Holm-adjusted α = 0.01) p = 0.7 |
|---|---|---|---|---|
| 20 | 0.13 | 0.42 | 0.80 | 0.24 |
| 30 | 0.29 | 0.73 | 0.97 | 0.43 |
| 40 | 0.32 | 0.81 | 0.99 | 0.58 |
| 60 | 0.45 | 0.94 | 1.00 | 0.76 |
| 100 | 0.62 | 0.99 | 1.00 | 0.95 |

**Reading:** the stated MEI (shift fraction ≥ 0.6) is **underpowered at every realistic n** — 0.45
even at n = 60. The test only works for a strong effect (p ≥ 0.7) with n ≥ 40 informative neurons.
**Action:** either raise the MEI to 0.7 and pre-register n ≥ 40 informative neurons as a gate, or
report P1 as an estimate with a CI and drop the H0: p ≤ 0.5 framing (which is a weak null anyway —
nobody believes exactly half). I recommend the latter: **report the shift fraction with a
cell-type-clustered CI, and make the informative fraction a co-headline number.** An estimate with a
CI is more honest and more informative than a binomial p-value against 0.5.

### 4.3 P2/P3 — Δρ

Using `Var(ρ) ≈ (1−ρ²)²/(n−1)` and the SE of a difference of two correlated correlations
(inter-predictor correlation c), for ρ_flow = 0.50 vs ρ_cent = 0.35:

| n_eff | c = 0.3: SE(Δρ) | power for Δρ = 0.15 | c = 0.6: SE(Δρ) | power |
|---|---|---|---|---|
| 60 | 0.126 | 0.32 | 0.096 | 0.47 |
| 120 | 0.089 | 0.52 | 0.068 | 0.72 |
| 200 | 0.069 | 0.71 | 0.052 | 0.89 |
| 400 | 0.048 | 0.93 | 0.037 | 0.99 |

**Reading:** at the grounded n_eff ≈ 200 the design is adequately powered (0.71–0.89) **only if the
full screen runs**. Under the C2 descope (n_eff ≈ 70) power falls to ≈ 0.35–0.50 and P2 becomes
uninterpretable. This is the single strongest argument for the Fig. 1F archive route (C3), which
delivers n = 200 neurons at zero compute.

**Three further corrections to P2/P3:**

1. **Attenuation.** `f^emp` is measured with error, which attenuates ρ toward 0 — and the error is
   *larger* for small-|f| neurons, so the attenuation is non-uniform. The design never accounts for
   this. **Fix:** estimate the reliability of `f^emp` by **split-half over trials** (fit f on odd and
   even seeds separately), report the split-half correlation as the reliability ceiling, and present
   both raw ρ and a disattenuated ρ. Also state the ceiling explicitly: no predictor can exceed the
   reliability of the target.
2. **Shared intact-curve error (the real double-dipping).** `f^emp` for *every* neuron is fitted
   against one interpolated intact curve `Ô`, so all `f^emp` share a common error; the grouped
   bootstrap resamples cell types but holds `Ô` fixed, understating uncertainty and inflating apparent
   consistency. **Fix:** (a) **split the intact trials** — estimate `Ô` on one half, test collapse on
   the other; and/or (b) nest the intact-curve bootstrap inside the cell-type bootstrap so `Ô` is
   re-estimated in each resample; and/or (c) fit one **hierarchical model** with O(·) as a shared
   monotone spline and per-neuron f, which propagates the shared uncertainty correctly. (c) is the
   cleanest and is cheap once the data exist.
3. **Use a more efficient test.** Prefer a **Hotelling–Williams-type test for dependent
   correlations** as primary (it exploits the known dependence structure) with the grouped bootstrap
   as sensitivity, rather than bootstrapping the difference as primary (M7).

### 4.4 P4 — replaced

Per M3: (i) confirmatory = among single-vertex S→T cuts (dominators), the proportion with no recovery
to λ_max, one-sided exact binomial; (ii) primary continuous version = monotone trend of `f^emp` on
min-cut participation, which uses all ~200 neurons instead of <5 positives; (iii) converse direction
reported descriptively with the theoretical reason recall should be < 1 stated **in advance**.

### 4.5 P5 — pairs

With ~20 parallel pairs, a permutation test of MSE against shuffled-pair predictions can detect only a
large effect, and the shuffled-pair null is weak (it breaks the pairing of predictions to pairs but
preserves the marginal distribution of predicted curves, so it mostly tests "are predictions better
than chance pairing" — a low bar). **Fix:** (a) add a **stronger null**: predictions from the *same*
f values with the overlap term set to its stratum mean (tests whether the overlap term carries
information, which is the actual claim); (b) pre-register the pair arm as an **estimation** exercise —
report predicted-vs-observed ε curves with CIs and the fraction of pairs whose observed curve lies in
the prediction band — rather than a p-value; (c) label it a pilot in the proposal (it already is in
the design — keep that wording out of the headline).

### 4.6 Multiplicity and reporting

One primary (revised P1, or P2 if the archive lands), secondary-confirmatory family {P2/P3, P4, P5,
external validation} under its own Holm correction, everything else explicitly exploratory (M9). State
the MEIs as revised: shift fraction ≥ 0.7 (not 0.6); Δρ ≥ 0.15 retained but with the n_eff and
attenuation caveats attached.

---

## (5) Novelty positioning

### 5.1 What the full texts have taken off the table

| Claim in v0.9 | Status after full-text verification |
|---|---|
| "Necessity is operating-point dependent / redundancy grows with intensity" | **Published.** Shiu 2024 states it in the text: "silencing of individual neurons had the greatest effect when sugar GRNs were activated at low frequencies, implying greater redundancy in the circuit as sensory stimulation increases" `[V-full]`. Already dropped in D-006 — correct. §0's consequence C5 ("explains, rather than asserts") is the right residual framing, but §0 bullet 5 still reads as if the observation were being contributed. Tighten. |
| "Pairs interact / are synergistic" | **Published.** Jacobs 2024 tested every single and every pair of second-order neurons at 50/100/200 Hz `[V-full]`. Readout was third/fourth-order **stopping** neurons, **not MN9**, and the analysis was descriptive with no interaction score, null, or structural predictor `[V-full]`. So the residual novelty is real but narrow: *a stated neutrality function + a structural predictor + intensity dependence, read out at MN9*. Say exactly that. |
| "Structure predicts silencing effect" | **Published in weaker form.** Minnick 2026: single-type silencing effect correlates with the type's **output synapse count**, ρ = 0.78, n = 11 types `[V-full]`. This is a published structural predictor of silencing magnitude. **Out-synapse count must become a named L0 competitor in P2** — it is the closest published baseline and it is nearly free to compute. Beating ρ = 0.78 on 11 types is not the bar; beating out-degree on ~200 types is. |
| "Max-flow on fly connectomes" | **Published.** Berg 2026 (male CNS) uses sensory→motor max-flow (Dinic, input-normalised capacities, signs ignored) `[V-full]`. Our use (per-neuron flow *fraction* predicting a dose–response) is genuinely different, but max-flow-on-connectomes must be cited to them, not presented as imported from CS. |
| "Joint silencing is supra-additive" | **Published** (Minnick 2026 `[V-full]`; Chen 2025 "additive" `[V-full]`). Do not claim the phenomenon. |

### 5.2 `f_k` is a flux control coefficient — and that is good news

**Yes.** `f_k` as defined is a finite-change analogue of the **flux control coefficient** of metabolic
control analysis, `C^J_E = (∂lnJ/∂lnE)`. Kacser & Burns (1981), *Genetics* 97:639–666 — found and
URL-verified in `lit_B` §4.10 `[V-abs]` — argue that flux is nearly insensitive to any single enzyme
because control is **shared**, formalised by the **summation theorem** (coefficients sum to 1). That is
the same proposition as "single-neuron silencing has little effect because each neuron's f is small",
which is the design's own starting observation. An MCA-literate referee will see this immediately.

Likewise, **C2 (EC50 shift with Emax preserved) is structurally the receptor-reserve / dose-ratio
result** of classical pharmacology: partial, irreversible loss of a transduction component shifts the
dose–response rightward before it lowers the maximum. The theory note already cites receptor reserve
as an analogy (§6) — correct — but names the "operational model of agonism" `[MEM]`. **Do not cite
Black & Leff, Furchgott or Stephenson by year/DOI from memory.** Either verify them or write "the
classical receptor-reserve argument in pharmacology `[MEM]`" and let the citation auditor resolve it.

### 5.3 Recommended positioning: an explicit bridge

Reposition from "we discovered a law" to **"we import two mature quantitative frameworks into
connectomics and test them where they have never been tested — a spiking, signed, whole-brain
connectome model — and we make the control coefficient *structurally predictable*."**

This **strengthens** the work, for four reasons:

1. **It pre-empts the strongest referee objection** ("isn't this MCA / receptor reserve?") by answering
   it in the introduction instead of in the rebuttal.
2. **It imports a new falsifiable prediction the design currently lacks** — the **summation theorem**.
   For a conservative flow measure, `Σ_k f_k` over the neurons of any S→T cut set should equal 1;
   over an arbitrary set it should not. The **excess of `Σ_k f^emp_k` over 1** is then a direct,
   interpretable measure of **redundancy** — and it connects straight to Shiu 2024's own verified
   statement that redundancy rises with stimulation, which becomes a quantitative prediction:
   `Σ_k f_k` measured at low λ should exceed `Σ_k f_k` at high λ. **This is the single best addition
   available to the design**: it is nearly free (it reuses the screen), it is novel as far as the
   searches go, and it converts a published qualitative observation into a quantitative law test.
3. **It gives the right null for "f is special".** MCA predicts small individual coefficients as the
   generic case, so "single-neuron effects are small" stops being a finding and becomes the baseline —
   which is honest and sharpens what *is* new.
4. **The genuinely unclaimed parts survive intact:** (a) **structural estimation** of the control
   coefficient from the connectome without perturbation simulation; (b) **curve collapse** as a test of
   scalar-drive transmission in a spiking network; (c) abolition vs dominator status at single-neuron
   resolution across intensities; (d) the pair-curve prediction. None of these appear in MCA (which
   assumes you can measure enzyme activity) or in pharmacology (no network structure).

**Does the bridge kill novelty? No — but it does kill the current framing.** Three things must go from
§0, §2 and the proposal: "apparently novel" applied to the rescaling law as such; "no free parameters"
for pairs (M1); and the implication that C2 is an independent empirical confirmation (3.3).

### 5.4 Residual pre-emption risk

`novelty_prior_art.md` §0 is admirably explicit that both literature tools hit quota and that the
dominator/articulation query was **never run** `[V-abs]`. With the Kacser–Burns and receptor-reserve
connections now explicit, the highest-risk unrun searches are: "flux control coefficient" + neural
circuit / connectome; "dose ratio" or "Schild" + network model; and the dominator/articulation-point
query. These are three searches. **Run them before the novelty sentence is written**, and if they
cannot be run, state in the proposal that the positioning is a bridge, which is robust to finding more
prior art (a bridge paper is not damaged by discovering that one of its two banks is well populated).

---

## (6) External-validation design (Shiu & Sterne 2022, two concentrations)

This is the strongest part of the revised project and currently the least specified. Below is a
complete, pre-registrable design.

### 6.1 Data and labels (freeze before computing any f)

From the full text `[V-full]`: seven second-order types elicit PER on activation. GtACR1 inhibition
reduced PER **to 50 mM** sucrose in food-deprived flies for **6 of the 7** (n = 46–83 per genotype).
**At 100 mM, only Rattle and Usnea** reduced PER (n = 30–144). Third-order and premotor types: **no
effect at 50 mM** (n = 40–70). Usnea and Phantom are predicted **GABAergic**.

Three ordinal tiers:

| Tier | Types | Meaning |
|---|---|---|
| 2 | Rattle, Usnea | necessary at 50 **and** 100 mM |
| 1 | Zorro, Clavicle, Phantom, + whichever of G2N-1 / FMIn is significant at 50 mM | necessary at 50 mM only |
| 0 | the one of the seven not reduced at 50 mM | not necessary |

**Caveat to resolve first.** `fulltext_verification.md` §8 reads the per-neuron 50 mM marks from the
PDF text layer and flags G2N-1 and FMIn as ambiguous (two split-GAL4 lines each, mixed marks). The
text asserts "6 of 7". **Before the test, read Figure 1E / Figure 1—figure supplement 2 source data**
(both are named in the paper) and freeze the tier assignment. If it cannot be resolved, pre-register
the test over **both** admissible tier assignments and report both — do not choose after seeing f.
Good news: §8's table is already committed (`fdcdd0a`, 2026-11-03 01:25), which timestamps the labels
**before** any f is computed. Preserve that ordering and cite the commit hash in the pre-registration.

### 6.2 The mapping problem, and how to avoid it entirely

Choosing model intensities λ_low, λ_high so that the model reproduces the 6/7 and 2/7 pattern would be
**fitting the labels** — the circularity the PI asked me to check. The way out:

> **Put the primary external test on `f`, not on `N_k(λ)`.** Under the rescaling law `f_k` is
> **λ-independent**, and the law's prediction that survives *any* monotone concentration→rate map is
> purely ordinal: *the types still necessary at the higher concentration are those with the largest f,
> and the necessary set shrinks as concentration rises.* The primary test therefore requires **no
> concentration mapping at all** — only `f`, which is estimated from the model's own intact curve.

That single move removes the circularity. The mapping then appears only in a clearly-labelled
secondary/descriptive analysis:

- **Secondary (nesting).** With λ_low, λ_high fixed **a priori** as the intact curve's λ25 and λ75
  (defined only by the intact simulation; no behavioural data used), check the **nesting** property
  `{k : N_k(λ_high) ≥ 0.2} ⊆ {k : N_k(λ_low) ≥ 0.2}` and that the set shrinks.
- **Descriptive sensitivity surface.** Repeat over a grid of (λ_low < λ_high) pairs and report the
  **fraction of pairs** for which the surviving set is exactly {Rattle, Usnea}. Report as a
  robustness number, **never as a p-value** — scanning λ is exactly the circularity being avoided.

### 6.3 Exact statistics and chance levels (computed by exact enumeration this session)

**Primary — rank concordance.** Statistic: **Kendall τ_b** between the model's 7 f-ranks and the
3-tier label. Null: uniform random assignment of ranks to types; exact enumeration of all 7! = 5040
permutations. Computed null distribution:

| Threshold | Exact P under uniform ranking |
|---|---|
| τ_b ≥ 0.816 (the **maximum attainable** against this tier pattern) | 1/105 = **0.0095** |
| τ_b ≥ 0.7 | 0.0095 |
| τ_b ≥ 0.6 | 0.0286 |
| τ_b ≥ 0.5 | 0.0667 |

So a one-sided α = 0.05 test is attainable and requires **τ_b ≥ 0.6**. Note τ_b ≥ 0.9 is impossible
given the ties in the tier labels — pre-register the attainable maximum (0.816) so a perfect result is
not misread as τ = 1.

**Secondary — top-2.** `P(the two largest model f are exactly {Rattle, Usnea}) = 1/C(7,2) = 1/21 =`
**0.0476** under uniform ranking. Valid, one-sided, exact — this is the statistic
`fulltext_verification.md` already proposed. Keep it, but note it is a **single coarse bit with no
partial credit**: it passes at p = 0.048 or fails outright. It is the sharpest statement of the
published result, so it belongs in the pre-registration, but τ_b should be primary because it degrades
gracefully.

**Secondary — layer test.** Second-order types should have larger f than third-order/premotor types
(Shiu 2022 tested 2 third-order + 1 premotor with split-GAL4 `[V-full]`). One-sided exact Wilcoxon
rank-sum, n = 7 vs m = 3: minimum attainable p = 1/C(10,3) = **0.0083**, so significance is reachable.
This test is **free** (the types are all in `sez_neurons.pickle` `[V-src]`) and it is the one external
test with a clean directional prediction and no sign ambiguity. Do not skip it.

Holm over these three, or declare τ_b primary and the other two secondary (preferred — see M9).

### 6.4 Handling Usnea's sign

Usnea is GABAergic in the model, so the model may return `f_Usnea < 0` (silencing *raises* MN9), while
the experiment says silencing Usnea *reduces* PER at both concentrations. Pre-register all three of
the following, in this order, **before** computing f:

1. **Primary: rank on signed f.** An inhibitory Usnea with f < 0 ranks last, the test fails on that
   type, and the failure is reported. This is the falsifiable choice and must be primary.
2. **Secondary: rank on |f|.** Justified because "GtACR1 reduces PER" and "model MN9 changes
   measurably" are both necessity phenotypes. State explicitly that this version **cannot be falsified
   by a sign error** and is therefore the weaker test. Report both, always.
3. **Pre-declared interpretation (not a test).** Declare **now** that a signed-f failure **confined to
   the two GABAergic types (Usnea, Phantom)** will be read as a neurotransmitter-sign limitation of the
   model rather than falsification of the rescaling law — and that this reading is admissible **only**
   because it was declared in advance. There is published precedent to cite: Shiu 2024 itself reports
   that the model **fails** to predict that Phantom activates MN9, attributing it to Phantom being
   predicted inhibitory `[V-full]`. So the model has a *known, author-acknowledged* sign problem in
   exactly this neuron class. Cite it. A Usnea failure is expected and non-fatal; an unexpected
   failure spread across cholinergic types would be serious.

### 6.5 Two honest limitations to pre-register

1. **Ceiling/power at 100 mM.** Baseline PER at 100 mM is near-saturating, so detecting a reduction
   needs a large effect, and n ranges from 30 to 144 per genotype `[V-full]`. The "only 2 of 7" result
   could partly be a **power** pattern rather than a necessity pattern. If the source data give
   per-genotype n, check whether the non-significant types at 100 mM were the small-n ones, and report
   it. This cuts both ways and must be stated regardless of outcome.
2. **Input set and state.** Use the annotation-pure sugar GRN set for this arm (M12); Shiu 2022 used a
   different 17-GRN candidate set. Both concentrations were tested in food-deprived flies, so hunger
   state is **matched** across the two conditions (good — the model has no hunger state, and a mismatch
   would have been fatal to the comparison).

### 6.6 Why this arm is worth protecting from descoping

It is the only part of the project that bears on biology (STRATEGY §3.2; §5.7.3), it needs only ~20
named types rather than a 400-neuron screen, its labels are already frozen in a timestamped commit,
and its chance levels are exact and pre-computable. **It should be the last thing cut, not the first.**
One encouraging sign that it is not circular: ranking the seven types by **direct** sugar-GRN synapse
count (Fig. 1A: Zorro 325, Clavicle 210, G2N-1 165, Rattle 110, Usnea 75, FMIn 75, Phantom 65
`[V-full]`) puts Rattle 4th and Usnea 5th–6th. So the 100 mM result is **not** explained by direct
sensory input, and a flow-based f that recovers {Rattle, Usnea} would be a genuine, non-trivial
success.

---

## (7) Feasibility and descoping

### 7.1 The arithmetic

Measured `[V-src]`: ~5 s per 1-s trial in a persistent Brian2 process (1–1.8 s build + ~3.8 s
simulate), ~41 s/trial through the author's loky path (10 trials of `sugarR_100Hz` took 409 s), RSS
~3 GB/process, 366–385 active neurons at 150 Hz, 4 cores / 15 GB shared with other agents.

PROJECT_DESIGN §4's MVP at 5 s/trial:

| Block | Trials | CPU-h |
|---|---|---|
| Intact dense (25 λ × 30) | 750 | ≈ 1.0 |
| Single screen (400 × 8 λ × 8 trials) | 25,600 | ≈ 35.6 |
| Pair pilot (60 × 8 λ × 8) | 3,840 | ≈ 5.3 |
| Robustness (~1,500 × 8) | 12,000 | ≈ 16.7 |
| **Total** | | **≈ 59 CPU-h ≈ 20 h wall on 3 workers** |

Against ~1.5 days that must also contain: simulator validation (gates G1–G5, not yet delivered),
calibration of φ and D\*, structural predictors, all analysis, figures, the report and slides — with
3 GB/process on 15 GB capping real parallelism near 4, and the SIM agent competing for cores.
**This does not fit, by roughly 4×, and it has zero slack for a simulator that fails validation.**
D-007 ("keep the full MVP scope, work harder") is not a schedule; it is a hope. The design must carry
a pre-committed descope ladder so that tomorrow's cuts require no new decision.

### 7.2 Minimum design that still answers the core question

The core question is "can one structurally estimable number per neuron predict the whole
intensity-dependent silencing phenotype?" That needs: a dense intact curve; silenced curves over
enough λ to separate shift from gain; enough neurons for a rank correlation; and the external test.
It does **not** need 400 neurons, 8 λ or the full robustness grid.

| Block | Spec | Trials | CPU-h |
|---|---|---|---|
| Intact curve | 15 λ × 30 trials | 450 | ≈ 0.6 |
| Calibration (φ, D\*) | small | ~100 | ≈ 0.15 |
| **Tier A** screen | 80–120 neurons × **5 λ** × **12 trials** | ~6,000 | ≈ 8.3 |
| **Tier B** external | the ~20 named SEZ types (mostly ⊂ Tier A) × 5 λ × 12 | ~600 | ≈ 0.8 |
| Recruitment control (m8) | 10 GRN subsets × 5 λ × 12 | 600 | ≈ 0.8 |
| Pair pilot | **24 pairs** (12 parallel / 6 serial / 6 non-converging) × 5 λ × 12 | 1,440 | ≈ 2.0 |
| **Total** | | | **≈ 13 CPU-h ≈ 4.5 h wall on 3 workers** |

Rationale for the trade: **trials per condition matter more than neuron count for P1** (the collapse
test is per-neuron, and 8 trials at MN9 SEM ≈ 3% against effects of 5–6% is hopeless), while **neuron
count matters more than trials for P2** (a rank correlation over n_eff). Hence 12–15 trials and a
smaller, stratified neuron set — plus the archive route (C3) to recover n = 200 for P2 at no compute
cost. Tier A composition should be pre-registered as: all neurons with f^LIN-A above a stated
threshold, **plus** a stratified random sample across the f^LIN-A range, **plus** a low-rate stratum
(M5), **plus** Tier B.

Grid choice: 5 λ log-spaced to bracket λ50 (roughly 0.6–3× λ50) identifies a one-parameter shift
better than 8 levels half of which sit in saturation. Pre-register the grid from the intact curve
**before** any silencing runs.

### 7.3 Descoping order (freeze this in `DECISIONS.md` today)

Cut in this order, without further deliberation:

1. **Parameter robustness** (w_syn ± 20%, synapse threshold ≥ 5, sign flips) → report as "not run",
   pre-registered as deferred. (Shiu 2024 already published W_syn ± 30% and I:E ± 50% robustness
   `[V-full]` — cite theirs rather than redoing it. This cut is nearly free.)
2. **v630/v783 replication** → keep only if the reproduction gate already produced both (it did, for
   two conditions `[V-src]`); otherwise drop.
3. **Pair pilot (RQ4)** → drop to 12 parallel pairs only, then drop entirely. It is a pilot with one
   informative class and ~20 pairs (3.5); it cannot carry a conclusion either way.
4. **Left-input replicate** → drop (and note the drive asymmetry, m7, makes it hard to interpret
   anyway).
5. **Recruitment control** → reduce to 4 subsets at 3 λ.
6. **λ grid 5 → 4**; then **Tier A 120 → 60** (and demote P2 to secondary, per M7/4.3).

**Never cut:** the intact dense curve; Tier B (external validation, §6); the reproduction gate; the
silencing unit test (m1); the negative controls.

### 7.4 Three scheduling actions for today

1. **Fetch Shiu's Fig. 1F CSVs** (C3). This is the single highest-value hour available: it can replace
   the entire single-neuron screen with a better-powered, author-computed dataset and free tomorrow's
   compute for the external arm and pairs.
2. **Set a hard simulator cutoff.** Pre-commit a time (e.g. 18:00 today) after which, if the fast
   simulator has not passed its gates, the project runs the §7.2 minimum on **Brian2 in a persistent
   process** at 5 s/trial and the fast simulator is abandoned. An unvalidated simulator that silently
   differs is worse than a slow one; D-007's critical path currently has no fallback.
3. **Freeze notation and the primary readout** (C4, M4) — 30 minutes of editing that protects the
   pre-registration's credibility.

---

## (8) Proposal edits (`PROPOSAL_1page.md`)

Specific, line-referenced.

| Where | Current | Edit |
|---|---|---|
| Background, l.10–13 | "We found no theory that predicts from structure **how** the consequence of silencing a neuron changes with stimulus strength." | Replace with the bridge framing (§5.3): "Two mature frameworks already describe this situation — shared flux control in metabolic networks (Kacser & Burns 1981) and receptor reserve in pharmacology — but neither has been given a *structural* estimator, and neither has been tested in a spiking, signed, whole-brain connectome model. We supply both." This is both more honest and more impressive than an absence claim resting on quota-limited searches. |
| Background, l.11–13 | "the effect of silencing a neuron also varies with stimulus intensity: Shiu et al. screened single-neuron silencing at 8 sugar intensities." | Attribute the *finding*, not just the design: Shiu 2024 states that redundancy increases with stimulation `[V-full]`. Then state our contribution as making it quantitative. Current wording reads as if we noticed it. |
| H2, l.23–25 | "The dose–response curve shifts by 1/(1 − f_k) with its maximum preserved, and is abolished only when *k* is a source→target vertex cut." | "…shifts by 1/(1 − f_k) **in GRN drive** with its maximum preserved. Vertex-cut status implies no recovery at any tested intensity; the converse need not hold in a threshold network." (M2, M3 — fixes a wrong direction of implication in the one-page summary a referee will read first.) |
| H4, l.29–30 | "Pairwise interactions follow from inclusion–exclusion of flow fractions." | "Pair curves are predicted from the two single-neuron fractions plus an independently computed shared-route overlap." Delete any "no free parameters" phrasing (M1). |
| **New hypothesis** | — | **Add H5 (summation/redundancy):** "The flow fractions of neurons forming a sensory→motor cut sum to 1 for a conservative flow; the measured excess over 1 quantifies redundancy and should **fall** as stimulus intensity rises." This is the strongest addition available (§5.3 point 2): nearly free, novel, and it converts Shiu's verified qualitative statement into a quantitative test. |
| Methods, "Model and readout", l.33–36 | "the readout is the proboscis motor neuron MN9" | "the readout is the single MN9 present in v783 (contralateral to the stimulated GRNs)". Removes the L/R ambiguity and the averaging error (M4) from the document the course grades. |
| Methods, "Single-neuron screen", l.37–38 | "Every active neuron (about 400) is silenced individually across intensities" | Match the feasible design: "A pre-registered stratified set of ~100 active neurons across ~5 intensities with 12 trials each, extended to the published 200-neuron × 8-intensity archive dataset where available." Do not promise 400 (C2, C3). |
| Methods, "Fitting", l.39 | "Silenced curves are fit with shift-only vs shift-plus-gain models." | "…fit with shift-only, shift-plus-gain and free-sigmoid models, selected by cross-validated predictive error, with an absolute goodness-of-fit test against measured trial noise and an explicit 'uninformative' class." (C1 — the single most important edit in the document.) |
| Predicted outcomes, l.47–50 | Four confident bullets. | Add the informativeness caveat to bullet 1 ("among neurons whose curves can discriminate the two models") and soften bullet 3 to "no recovery within the tested intensity range is confined to vertex cuts" (M3). Four unqualified confident predictions on a one-pager invites the reviewer to find the one that cannot fail. |
| Limitations, l.55–58 | Three bullets. | Add two: (i) "`f` is a finite flux control coefficient; the contribution is its structural estimation and its dose–response consequences, not the concept"; (ii) "the model has a known neurotransmitter-sign failure in GABAergic second-order neurons (Phantom; Shiu 2024), which our external test may expose." Pre-stating the expected failure is strictly better than being asked about it. |
| Deliverables, l.63–65 | "An experimentally testable prediction: silencing shifts the PER sucrose dose–response curve by a factor set by f." | "…shifts the dose–response curve **in GRN firing rate** by 1/(1 − f); the conversion to sucrose concentration requires a published GRN dose–response and is given as a conditional corollary." (M2.) |
| Throughout | "Apparently novel" / absence claims. | Remove. The novelty report's own §0 states both search tools hit quota and that the dominator query was never run `[V-abs]`. A bridge framing does not depend on absence claims and cannot be undermined by a referee who knows one more paper. |

---

## Appendix: what I verified directly this session

| Item | Method | Result |
|---|---|---|
| Unitary PSP peak, 162 synapses, D\* = 5091 | re-derived from `model.py` parameters | theory §1 numbers correct |
| MN9 underdispersion | `04_stored_results_inspect.log` | 67.0 ± 6.6 Hz over 1 s ⇒ Fano ≈ 0.65 (not Poisson) |
| Effective n for cell-type bootstrap | v783 annotations × author's stored v630 run | 391 active ⇒ **207 types**; 347 ⇒ 186 types; 46 unannotated |
| P1 binomial power | exact binomial | 0.45 at n = 60, p = 0.6; 0.94 at n = 60, p = 0.7 |
| P2 Δρ power | SE of dependent correlation difference | 0.71–0.89 at n_eff = 200; ≈ 0.4 at n_eff = 70 |
| τ_b null for the 7-type test | exact enumeration of 7! = 5040 | max τ_b = 0.816, P = 1/105; P(τ_b ≥ 0.6) = 0.0286 |
| Top-2 and layer-test chance levels | exact combinatorics | 1/21 = 0.0476; 1/120 = 0.0083 |
| MN9_R absent from v783; L/R label flip | `08_annotations_check2.log` | confirmed; `CB0701` left = 720575940618238523 |
| Sugar-set heterogeneity | `08_annotations_check2.log` | 9 LB3c + 2 LB3b + 5 LB3d high-salt + 4 LB4b of 21 |
| `silence()` zeroes outgoing only; namespace warning | `model.py`, `04_repro_run.log` | confirmed; `w = 0` in `eq_rst` is not a neuron variable |
| Shiu 2024 redundancy statement; W_syn calibration | `literature/text/shiu2024.txt` | both confirmed `[V-full]` |
| Shiu 2022 two-concentration result; GABAergic Usnea/Phantom; Fig. 1A synapse counts | `shiu2022.txt`, `shiu2022_figs.txt` | all confirmed `[V-full]` |
| Jacobs 2024 readout is stopping neurons, not MN9 | `mmc3.txt` | confirmed `[V-full]` |
| Fig. 1F CSVs absent from uploads; Fig. 1E present | `data/shiu_archive/` | confirmed (3 files, 200 rows each) |
