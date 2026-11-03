# RESULTS v783: pre-registered analysis (PROJECT_DESIGN v1.0, D-009, D-010)

Generated from `analysis/out/results_v783.json` (`run_analysis.py fit | boot | stats`). The inputs are the frozen
files in `analysis/out/FROZEN_MANIFEST.md5`. Primary readout: contralateral MN9 `720575940660219265`.
Input: S_shiu (20 GRNs) for the single screen; S_pure (33 GRNs) for the cell-type screen.

## Sample

- 573 single-neuron candidates (active in the intact runs; S and both MN9s excluded), 337 cell-type clusters
  (2 unannotated singletons). That is more than the ~200 assumed in the power estimate.
- 70 of 573 neurons are effect-bearing (§6.1 with Holm across λ); 503 are class `none`. All 70 are informative.
- f̂ spans −0.88 to 0.33; 24 neurons have f̂ > 0.05 and 15 have f̂ < −0.05 (net-inhibitory contribution).

## Controls

| Control | Result |
|---|---|
| Silence MN9 (T) | f̂ = −0.008, class `none` (D-010) |
| Silence all S | no MN9 output at any λ |
| Each GRN alone | f̂ 0.03–0.08; Spearman with the structural share f^LIN-S across the 20 GRNs: ρ = 0.68 |
| No S→T path | structural f = 0 exactly (STRUCT) |

## Primary test (P-A): passed

Δρ = ρ_s(f^LIN-A, f̂) − max over L0 of ρ_s(X, f̂), grouped bootstrap over cell types, B = 2,000, competitor re-selected
in every resample, seed-level f̂ replicates nested.

| Quantity | Value |
|---|---|
| ρ_s(f^LIN-A, f̂) | 0.369 |
| Best L0 competitor (point estimate) | k-core, ρ = 0.068 (all eight L0 measures lie between −0.10 and 0.07) |
| Δρ | **0.302** |
| One-sided 95% lower bound (5th pct.; decision) | **0.083 > 0 → H3 supported** |
| 2.5th percentile (reported, D-009) | 0.054 |
| Two-sided 95% CI | [0.054, 0.388]; one-sided bootstrap p = 0.006 |
| Williams t / Steiger z vs k-core (n = 337 types) | t = 3.95, z = 3.89, one-sided p ≈ 5 × 10⁻⁵ |
| Shift class only (n = 27) | ρ = 0.77, Δρ = 0.57, lower bound 0.20 |
| Partial ρ given hop distance and baseline rate | 0.38 (p = 3 × 10⁻²¹) |

**Reliability caveat.** The split-half reliability of f̂ is high on the raw scale (Pearson 0.96) but modest on ranks
(Spearman 0.43; Spearman–Brown 0.60), because 503 neurons have f̂ ≈ 0, where ranks are set by noise. The disattenuated
ρ(f^LIN-A, f̂) is 0.48. The effect size is below the pre-registered MEI of 0.15 at the lower bound but well above it at the
point estimate.

**Interpretation caveat.** The active linearization behind f^LIN-A is unstable at λ50 (ρ(A) = 3.19, max Re λ = 2.99;
LOG 2026-11-03), so f^LIN-A is an exact linear-response ratio, not a convergent walk sum.

## Secondary family (Holm, α = 0.05): none rejected

| Test | Statistic | p (raw) | p (Holm) | Result |
|---|---|---|---|---|
| S1 f^LIN-A vs baseline rate | Δρ = 0.63 (ρ_rate = −0.26), lower bound 0.11 | 0.019 | 0.076 | not rejected |
| S2 f^LIN-S (structure only) vs L0 | Δρ = 0.21, lower bound −0.03 | 0.083 | 0.249 | not rejected |
| S3 dominators → no-recovery | 0 dominators in the excitatory active graph; no neuron is `no-recovery` | — | — | dropped from the family (< 5 dominators, D-009) |
| S4 type-level f̂ vs experimental tiers | τ_b = −0.35 | 0.876 | 1.0 | not rejected (opposite direction) |
| S5 second-order > downstream layer | W = 38 | 0.583 | 1.0 | not rejected |

### External cell types (S_pure input, whole-type silencing)

| Type | Tier (frozen) | f̂ | Class |
|---|---|---|---|
| Rattle | 2 | 0.017 | shift |
| Usnea | 2 | −0.077 | other |
| Zorro | 1 | 0.064 | other |
| Clavicle | 1 | 0.379 | other |
| G2N-1 | 1 | 0.147 | gain |
| FMIn | 1 | −0.002 | none |
| Phantom | 0 | 0.049 | gain |
| Bract | downstream | 0.013 | gain |
| Fdg | downstream | 0.001 | none |
| Roundup | downstream | **0.826** | other |

The model does not reproduce the experimental ordering. The failure is not confined to the GABAergic types (Usnea,
Phantom), so by the pre-declared rule (§7.2) it counts against external validity. The largest discrepancies are
cholinergic: Rattle (experimentally strongest) has almost no model effect, and Roundup (no experimental effect) is the
strongest model effect of all ten types. The latter matches the authors' own archive runs, where silencing Roundup R
lowered MN9 from about 63 to 45.5 Hz (LOG). S4 variants: |f̂| τ_b = 0.00 (p = 0.56); sensitivity tiers τ_b = −0.21
(p = 0.77); top-2 indicator 0 (p = 1).

## RQ2: rescaling law (estimation)

| Class | n |
|---|---|
| none | 503 |
| shift (collapse holds) | 27 |
| gain | 32 |
| other | 11 |
| no-recovery / uninformative | 0 / 0 |

Collapse fraction 27/70 = **0.39 (95% cluster CI 0.27–0.51)**. The pre-registered falsifier (upper bound < 0.5) is
narrowly not met, but the point estimate says the pure shift describes a minority of effect-bearing neurons; the
shift-plus-gain model is the most common class.

## RQ1: centrality vs necessity across intensities

Per-λ Spearman with N_k(λ): f^LIN-A 0.21–0.33 at every grid level; f^LIN-S 0.11–0.26; output synapse count (the
Minnick 2026 competitor) −0.06 to 0.04; k-core −0.09 to 0.13; baseline rate changes sign across λ (−0.50 to 0.20).
Full table: `out/results_rq1_per_lambda.csv`.

## S6: summation over the direct-output cut C1 (estimation)

C1 has 265 neurons, 107 active. The pointwise sum Σ f_k(λ) is defined for all 107 only at 3 of 10 λ (−0.85, −0.60,
0.24 at 71, 91, 117 Hz); it is far from 1 and has no detectable trend (slope CI −3.5 to 9.8). Large opposite-signed
contributions from inhibitory members dominate. The summation prediction is not supported in its simple form.

## Not yet run

Pair pilot (§6.5), recruitment control (§6.6), v630 / left-input / W_syn replications, and the replication on the
authors' archive runs (`data/shiu_archive/`).
