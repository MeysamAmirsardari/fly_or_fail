# fastlif: validation of the fast re-implementation of the Shiu et al. 2024 LIF model

_SIM, 2026-11-03. Code: `sim/fastlif.py` (simulator), `sim/reduce.py` (exact reduction), validation scripts
`sim/g0_brian2_exact.py`, `sim/g3_reduction.py`, `sim/g12_compare.py`, `sim/g1_power.py`, `sim/g4_g5.py`,
`sim/brian2_extra.py`. Logs: `sim/logs/`. Arrays: `sim/out/` (git-ignored)._

## 0. Verdict

fastlif reproduces the original Brian2 model **spike for spike** when given the same input trains (G0). The exact network reduction is
**bit-identical** to the full network (G3). CRN works as specified (G4). One 1-s trial of one condition costs about
0.1–0.25 core-seconds, against about 6–13 s for Brian2 (G5). **The simulator is usable for the production runs.**

| Gate | What | Result |
|---|---|---|
| G0 (extra) | Original Brian2 objects + identical input trains vs fastlif, full network, 9 cases | **PASS**: 9/9 spike trains identical (0 differing spikes out of 149,481) |
| G1 | vs ENG Brian2 refs (20 trials each), λ = 50/100/200, v630 + v783, + 3 v630 silencings at 100 Hz | **PASS on r (≥ 0.9989), slope (0.985–1.003) and active set in 9/9.** MN9-in-CI strict check: 2 misses of 15 (MN9_L at 100 Hz in both versions, in opposite directions). Re-tested with 90 / 55 Brian2 trials vs 2,000 fastlif trials: **both within CI (p = 0.21, 0.16)**. Verdict: PASS with documented re-test |
| G2 | vs the authors' stored outputs (30 trials; 200 Hz, 100 Hz, 3 silencings at 100 Hz; v630) | **PASS** 5/5 (r ≥ 0.9997, MN9 L+R within CI) |
| G3 | closure vs full network inside fastlif, 116 jobs/version (intact + 27 silencing conditions), v630 + v783 | **PASS**: bit-identical spike trains; the boundary check fired and expanded correctly; a deliberately truncated closure also converges to identical results |
| G4 | CRN sanity | **PASS** (all 5 sub-checks) |
| G5 | speed | Measured with 4 threads on the grown closures (18.5–19.3k neurons) under load average about 7 (other agents' jobs): **0.13–0.17 s per 1-s trial per condition**. Projected 3,200×8 = 25,600 jobs: **≤ 73 min**; 480×8 = 3,840 jobs: **≤ 11 min** (about 2–3× less on an idle machine). Brian2: 5.8–13.5 s per trial per process at about 3 GB |

## 1. Model semantics replicated, with sources

All verified against `/home/user/external/Drosophila_brain_model/model.py` (commit 91bdd1e7) and the code that
Brian2 2.11.0 actually generates for it (default Cython target; dump in `sim/logs/00_probe_brian2_codegen.log`).
The Brian2 source files are under `venv-fly/lib/python3.13/site-packages/brian2/`.

| # | Semantics | Source |
|---|---|---|
| S1 | dt = 0.1 ms (Brian2 default clock); 1-s trial = 10,000 steps, s = 0…9999 | Brian2 defaults; `t_run` in model.py |
| S2 | dv/dt = (v_0 − v + g)/t_mbr, dg/dt = −g/tau, both `(unless refractory)`, method `linear`. Update: `g ← L2·g; v ← L8 + (L9·g_old + L10·v)` with Brian2's own loop invariants (L2 = e^{−dt/τ}, L10 = e^{−dt/τm}, L8 = v_0 − v_0·L10, L9 = τ/(τm−τ)·(e^{dt/τ} − e^{dt/τm})·e^{−dt/τm}·e^{−dt/τ}) evaluated in the same float64 operation order | generated stateupdate code (`_lio_*`) |
| S3 | Parameters: v_0 = v_rst = −52 mV, v_th = −45 mV, t_mbr = 20 ms, τ = 5 ms, t_rfc = 2.2 ms (0 for Poisson targets), delay 1.8 ms, w_syn = 0.275 mV, Poisson weight 68.75 mV (= w_syn·f_poi, f_poi = 250) | `default_params`, `poi()` |
| S4 | Refractoriness: `not_refractory = timestep(t − lastspike) ≥ timestep(rfc)`, timestep(x) = int((x + 1e-3·dt)/dt), so **22 steps**. During refractoriness v and g are frozen. lastspike starts at −1e4 s | `groups/neurongroup.py` l.223, `core/functions.py` l.798, l.695 |
| S5 | Threshold: `(v > v_th) and not_refractory`; on a spike, not_refractory ← False and lastspike ← t immediately | `neurongroup.py` l.395; threshold template |
| S6 | **Conditional write.** Because v and g are `(unless refractory)`, every write from another code object is executed only if `not_refractory`. Synaptic `g += w` and Poisson `v += …` are therefore **discarded** for a refractory target, and also in the step in which the target spikes. The resetter is exempt | `neurongroup.py` l.846–853 (`set_conditional_write`), l.422 (`override_conditional_write` for the resetter); generated code `if not_refractory: g += w` |
| S7 | Reset `v = v_rst; w = 0; g = 0 mV`: **`w = 0` is a no-op.** w is not a neuron variable, so the code generator declares a local temporary `cdef int64_t w = 0` | generated reset code |
| S8 | Delay: `(int)(1.8 ms/dt + 0.5)` = **18 steps**, a homogeneous spike queue. A spike emitted in step s is delivered in the synapses slot of step s + 18 | `synapses/spikequeue.h` l.85–90, push/peek/advance |
| S9 | Within-step schedule: groups (stateupdate) → thresholds (thresholder, SpikeMonitor) → synapses (pathway, order −1; PoissonInputs, order 0) → resets | `Network.scheduling_summary()` in the probe log |
| S10 | Delivery order: spiking neurons in ascending index, then synapses in creation order (= connectivity file row order) | spike queue push; thresholder loop |
| S11 | PoissonInput(N = 1): the binomial inversion sampler with n = 1 returns 1 iff U > 1 − p, i.e. exactly Bernoulli(p = rate·dt) per step | `input/binomial.py` |
| S12 | Weights w = `Excitatory x Connectivity` · w_syn (int64 · float). No duplicate (pre, post) pairs, no zero weights. Indices = completeness csv row order (checked: ID↔index consistent in both versions). The sign is constant per presynaptic neuron | `create_model`; `sim/out` checks |
| S13 | Silencing = outgoing weights set to 0 (`syn.w['k == i'] = 0`). fastlif skips delivery of silenced neurons' spikes, which is identical because x + 0.0 = x | `silence()` |
| S14 | No background input; initial v = v_0, g = 0 | `create_model` |

Consequences that the theory note (§1) does not state (**please add**):
- Synaptic input arriving during a neuron's 2.2-ms refractory period, or in its spike step, is lost (S6).
- A stimulated GRN fires in the step *after* each Poisson event. An event falling in the GRN's own spike step is
  lost, so the GRN rate is ≈ λ(1 − λ·dt): 99 Hz at 100 Hz input, ≈ 384 Hz at 400 Hz. Measured: 99.07 Hz in fastlif,
  99.23 Hz in Brian2.

## 2. CRN design (deliverable 1)

The Poisson drive of stimulated neuron *f* (FlyWire id) in trial seed *t* is

u[f, t, s] ~ U[0, 1) from `numpy PCG64(SeedSequence([salt, t, f]))`, s = 0…9999,

with an input event at step s iff u < rate·dt. Properties:

- Identical across all conditions sharing (t, f, rate).
- Independent of which other neurons are stimulated (this matters for the 50%-GRN recruitment control), of silencing,
  of network size or closure, of batch composition and order, and of thread count.
- **Nested across λ.** The events at λ1 < λ2 are a subset of those at λ2, i.e. exact thinning of the highest-rate
  train with uniform marks.
- The marginal distribution equals Brian2's (S11).

`salt` (default 0) lets later experiments use fresh streams. The RNG streams themselves differ from Brian2's, which
is unavoidable and harmless (G1/G2 are statistical tests for exactly this reason).

## 3. Exact reduction (deliverable 2)

**Construction (`reduce.py build`).** On the FULL network, intact, at λ ∈ {50, 100, 200, 300, 400} Hz × 8 trials,
let A be the neurons that spiked at least once. Then

C0 = stimulated ∪ A ∪ exc_out(A),

where exc_out = targets of synapses with w > 0.

| | v630 | v783 |
|---|---|---|
| A (active) | 498 | 494 |
| C0 | 8,216 neurons / 852k synapses | 8,316 / 868k |
| current C (after runtime expansions during validation) | 19,317 / 1.82M | 18,484 / 1.62M |
| full network | 127,400 / 14.69M | 138,639 / 15.09M |

C is stored in `sim/out/closure_<ver>.npz` and only grows; concurrent writers take the union.

**Theorem (exactness).** Fix stimulus, silencing set and input trains. Let C contain every stimulated neuron.
Simulate the restriction of the model to C (synapses with both ends in C, original order). Suppose that during the
run no neuron that spikes, and whose output is not silenced, has a synapse with w > 0 onto a neuron outside C (the
*boundary condition*). Then:

- (i) the full-network run performs, for every neuron in C, exactly the same floating-point operations in the same
  order as the reduced run, so the spike trains are bit-identical;
- (ii) no neuron outside C ever spikes in the full run.

*Proof.* Construct a candidate full trajectory: neurons in C follow the reduced run; each neuron j ∉ C starts at
(v_0, 0). j receives no Poisson input (the stimulated neurons are in C) and receives deliveries only from neurons that
spike, all of which are in C. By the boundary condition, every weight delivered to j is ≤ 0, so

g_j(s) = L2·g_j(s−1) + Σ(w ≤ 0) ≤ 0 for all s.

Then v_j(s) = L8 + L9·g_j + L10·v_j ≤ L8 + L10·v_j. Because L8 = v_0(1 − L10), v_j stays within a few ulp of v_0 or
below it, far from v_th (7 mV away), so j never spikes. Hence j never delivers anything into C, and the inputs of
every C-neuron are exactly the deliveries of the reduced run. Those deliveries come in the same order because C is
sorted by global index (S10), and silenced and zero-weight terms contribute x + 0.0 = x. The candidate therefore
satisfies the full model's update rules step by step, and since the update is deterministic it **is** the full
trajectory. ∎

Remarks:
- Purely inhibitory out-neighbours never need to be in C.
- Output-silenced neurons never violate the condition.
- The `inout` mode (also drop input *to* silenced neurons) only removes deliveries, so the same argument holds.

**Runtime boundary check.** Each neuron of C carries `leak[i]` = "has an excitatory synapse leaving C". The kernel
counts, per job, the spikes of non-silenced neurons with `leak`. `reduce.run_exact` then:

1. adds exc_out of all such neurons to C (and persists it);
2. re-runs only the flagged jobs;
3. iterates until no job flags.

A job that did not flag is exact for *any* C ⊇ stimulated, so earlier results stay valid when C grows; they are
zero-padded, which is exact by (ii).

Why C grows beyond C0: under silencing, or in long runs (≥ 200 trials), rarely spiking neurons (≈ 0.05–0.2 Hz)
appear. Some have very large excitatory out-degree, and one expansion step can add about 4,000 neurons. This costs
speed (linear in |C|), not exactness.

## 4. Validation gates

### G0 (added). Trajectory-level equivalence with Brian2

`g0_brian2_exact.py` builds the network with the **unmodified** `model.create_model` (and `model.silence`). For each
stimulated neuron it sets rfc = 0 exactly as `model.poi` does, and replaces the random PoissonInput by a
deterministic code runner with the *same* code, slot and conditional write:
`v += 68.75*mV * ta_k(t)` in `when='synapses', order=0`, where `ta_k` is fastlif's CRN Bernoulli train. Brian2's
float constants were asserted equal to fastlif's.

| ver | λ (Hz) | trial seed | silenced | Brian2 spikes | fastlif spikes | differing spikes | active neurons |
|---|---|---|---|---|---|---|---|
| v630 | 100 | 0 | — | 9610 | 9610 | 0 | 363 |
| v783 | 100 | 0 | — | 8672 | 8672 | 0 | 353 |
| v630 | 200 | 1 | — | 16733 | 16733 | 0 | 391 |
| v783 | 200 | 2 | — | 16385 | 16385 | 0 | 401 |
| v630 | 400 | 3 | — | 26917 | 26917 | 0 | 438 |
| v630 | 100 | 4 | 720575940622695448 (inh) | 10310 | 10310 | 0 | 366 |
| v783 | 100 | 5 | 720575940627383685 (inh) | 9144 | 9144 | 0 | 373 |
| v630 | 100 | 6 | 720575940617937543 (exc) | 9232 | 9232 | 0 | 339 |
| v783 | 400 | 7 | 720575940619973712 (inh) | 25878 | 25878 | 0 | 450 |

All 9 cases have identical spike trains, (step, neuron) for every spike. This verifies S1–S14 jointly, including
the conditional-write rule S6, which a rate comparison alone could miss. (Logs: `01_g0_*.log`, `02_g0_suite.log`.)

### G1. vs ENG's Brian2 references (original code path, `brian2.seed(t)` per trial, 20 trials)

fastlif: 200 trials (seeds 1000–1199), closure network with `run_exact`.

- r and slope are computed over neurons > 5 Hz in either simulator; the slope is OLS of fastlif on Brian2.
- "Active set" means every neuron ≥ 1 Hz in one simulator spikes in the other.
- The MN9_R id 720575940645521262 does not exist in v783, so MN9_R is N/A for v783.

| ver | λ | condition | r | slope | n > 5 Hz | MN9_L fastlif vs Brian2 [95% CI] | MN9_R | active-set violations (max rate of one-sided neurons) | strict |
|---|---|---|---|---|---|---|---|---|---|
| v630 | 50 | intact | 0.99898 | 0.985 | 135 | 19.79 vs 18.20 [15.43, 20.97] in | 15.32 vs 13.40 [11.30, 15.50] in | 0 (0.14 Hz) | PASS |
| v630 | 100 | intact | 0.99925 | 0.998 | 274 | 67.13 vs 70.00 [68.14, 71.86] **OUT** | 49.04 vs 50.55 [48.41, 52.69] in | 0 (0.09 Hz) | **FAIL** |
| v630 | 200 | intact | 0.99980 | 1.001 | 334 | 93.24 vs 92.15 [89.91, 94.39] in | 63.15 vs 63.70 [61.95, 65.45] in | 0 (0.07 Hz) | PASS |
| v630 | 100 | sil 720575940617937543 | 0.99967 | 1.000 | 271 | 64.64 vs 65.05 [62.21, 67.89] in | 45.65 vs 45.35 [42.76, 47.94] in | 0 (0.09 Hz) | PASS |
| v630 | 100 | sil 720575940621754367 | 0.99956 | 1.000 | 270 | 67.32 vs 67.45 [65.80, 69.10] in | 49.73 vs 49.70 [47.30, 52.10] in | 0 (0.09 Hz) | PASS |
| v630 | 100 | sil 720575940622695448 | 0.99943 | 1.003 | 276 | 70.92 vs 70.95 [68.21, 73.69] in | 51.29 vs 50.15 [48.11, 52.19] in | 0 (0.09 Hz) | PASS |
| v783 | 50 | intact | 0.99898 | 0.995 | 101 | 13.12 vs 12.90 [11.16, 14.64] in | n/a | 0 (0.18 Hz) | PASS |
| v783 | 100 | intact | 0.99901 | 0.995 | 262 | 62.14 vs 59.85 [57.99, 61.71] **OUT** | n/a | 0 (0.09 Hz) | **FAIL** |
| v783 | 200 | intact | 0.99977 | 0.999 | 324 | 89.52 vs 90.25 [88.26, 92.24] in | n/a | 0 (0.07 Hz) | PASS |

Across all 9 comparisons, r ≥ 0.9989 and slope ∈ [0.985, 1.003]. All neurons that fire in only one simulator have
rates ≤ 0.18 Hz, and they come almost entirely from fastlif's 10× larger trial count.

#### 4.1 Diagnosis of the two MN9_L misses

A "fastlif inside Brian2's 95% CI" test fails by chance about 5–8% of the time even for identical models. fastlif's
own sampling error adds to that. With 15 such checks, 1–2 misses are expected. The misses also go in **opposite
directions** (v630: fastlif lower; v783: fastlif higher). G0 shows that, given identical inputs, the dynamics are
bit-identical, and S11 shows the input distribution is identical, so there is no mechanism for a bias. I tested this
with more data rather than assuming it:

**v630, 100 Hz (`g1_power.py`, log `10_g1_power_v630.log`).**
- fastlif: 2,000 trials (seeds 5000–6999).
- Brian2: all 90 independent trials available. ENG 20 (seeds 0–19), 30 new ones from the original `model.run_trial`
  path (`brian2_extra.py`, seeds 100–129), the feasibility repro 10, and the authors' stored 30.
- MN9_L: fastlif **67.62 ± 0.11** vs pooled Brian2 **68.33 [67.23, 69.44]**, within the CI (Welch p = 0.21).
- MN9_L by Brian2 set: ENG 70.0, new 68.67, repro 67.9, authors 67.03. The sets do not differ from each other
  (ANOVA p = 0.27). ENG's 20-trial mean was simply on the high side, and fastlif's first 200-trial mean (67.13) on
  the low side.
- MN9_R: 49.54 vs 49.48 [48.52, 50.44].
- GRN output rate: 99.07 vs 99.23 Hz.
- Over 271 neurons > 5 Hz: r = 0.9999, slope = 0.9985; 2.6% of |z| > 1.96, 0.4% > 2.58. The per-neuron z-scores are
  strongly correlated across neurons through shared trial-level fluctuations, which explains their mean of −0.50 and
  SD of 0.75.
- **PASS.**
- Intermediate result, for transparency: fastlif's first 200-trial sample (67.13 ± 0.34) against ENG + new (50 trials,
  69.20 [67.98, 70.42]) was also outside (p = 0.004). With the 30 new trials alone it was inside (68.67
  [67.00, 70.34], p = 0.09). The 2,000-trial estimate shows that the 200-trial sample was low by about 1.4 SE.

**v783, 100 Hz.** See 4.2.

#### 4.2 v783, 100 Hz follow-up

Same procedure (log `10_g1_power_v783.log`). fastlif: 2,000 trials. Brian2: 55 trials. ENG 20, 25 new ones from
the original path (seeds 100–124; the run was OOM-killed twice by other jobs in the shared cgroup and resumed from
per-trial shards, and 25 of the planned 30 were used), and the feasibility repro 10. The authors stored no v783 files.

- MN9_L: fastlif **61.79 ± 0.11** vs pooled Brian2 **60.76 [59.33, 62.19]**, within the CI (Welch p = 0.16).
- MN9_L by Brian2 set: ENG 59.85, new 60.72, repro 62.70 (ANOVA p = 0.39).
- GRN rate: 99.08 vs 99.14 Hz.
- Over 261 neurons > 5 Hz: r = 0.99976, slope = 0.996. z mean +0.11, SD 1.14; 11.1% of |z| > 1.96 but only 0.8% of
  |z| > 2.58. The excess at 1.96 is not matched in the tail, and v630 showed 2.6%. With z correlated across neurons
  and Brian2 SEs estimated from 55 trials, I read this as noise. There is no mechanism for a difference: G0 is
  bit-identical on v783 in 3 cases. The largest |z| was 2.94 (27.9 vs 28.6 Hz).
- **PASS.**

**G1 summary.**
- The pre-specified strict criterion passes in 7/9 comparisons. The two MN9_L misses are explained by reference
  sampling noise.
- Both pass when re-tested at higher power (v630: 90 Brian2 vs 2,000 fastlif trials; v783: 55 vs 2,000).
- r, slope and active-set criteria pass in 9/9.
- I call G1 **PASS (with the documented re-test)**. The PI may prefer to record it as "7/9 strict + 2 re-tested".

### G2. vs the authors' stored outputs (`results/example/`, v630, 30 trials each)

| file | λ | silenced | r | slope | MN9_L fastlif vs Brian2 [CI] | MN9_R | active-set violations | result |
|---|---|---|---|---|---|---|---|---|
| sugarR | 200 | — | 0.99984 | 0.997 | 93.24 vs 93.27 [92.07, 94.46] in | 63.15 vs 61.80 [60.21, 63.39] in | 0 (≤ 0.05 Hz) | PASS |
| sugarR_100Hz | 100 | — | 0.99972 | 1.002 | 67.13 vs 67.03 [64.53, 69.54] in | 49.04 vs 48.63 [46.86, 50.41] in | 0 | PASS |
| sugarR-720575940617937543 | 100 | that GRN | 0.99972 | 1.000 | 64.64 vs 63.27 [61.47, 65.06] in | 45.65 vs 45.67 in | 0 | PASS |
| sugarR-720575940621754367 | 100 | that GRN | 0.99970 | 0.992 | 67.32 vs 66.90 [64.59, 69.21] in | 49.73 vs 49.70 in | 0 | PASS |
| sugarR-720575940622695448 | 100 | that inh. neuron | 0.99978 | 1.005 | 70.92 vs 71.17 [69.49, 72.84] in | 51.29 vs 51.00 in | 0 | PASS |

The authors' stored files were produced with an older Brian2 version, so this also checks that the semantics are
stable across Brian2 versions. (Log: `07_g2.log`.)

### G3. Reduced vs full network inside fastlif (`g3_reduction.py`, logs `04_g3_*.log`)

Jobs:
- intact at λ = 50/100/200/400 × 2 trials;
- 27 silencing conditions × λ = 100/400 × 2 trials: 8 random excitatory singles, 8 random inhibitory singles, the 3
  most active inhibitory neurons, the top-5 inhibitory set, 4 random pairs, 2 random 5-sets, and the top-20
  inhibitory set (strong disinhibition).

Total: 116 jobs per version. Every spike (step, neuron) was compared.

| ver | test | closure start → end | expansions | spike trains identical | spikes outside C in the full run | residual violations | spikes compared |
|---|---|---|---|---|---|---|---|
| v630 | real closure | 8,216 → 9,059 | 1 (17 jobs flagged) | **yes** | 0 | 0 | 2,117,425 |
| v630 | truncated C = stim ∪ A (456) | 456 → 9,059 | 2 | **yes** | 0 | 0 | 2,117,425 |
| v783 | real closure | 8,316 → 18,178 | 4 | **yes** | 0 | 0 | 2,027,711 |
| v783 | truncated (458) | 458 → 18,002 | 5 | **yes** | 0 | 0 | 2,027,711 |

**PASS.** The boundary check fires when it must (including the truncated-closure stress test) and expansion always
converges to the bit-identical full-network result.

### G4. CRN sanity (`g4_g5.py`, log `06_g4_g5_v630_2threads.log`)

| check | result |
|---|---|
| input uniforms invariant to trial/neuron order in generation | PASS |
| invariant to the stimulated subset (recruitment control) | PASS |
| nested thinning: events(50) ⊂ events(100) ⊂ events(200) ⊂ events(400) | PASS; realized event rates 49.1 / 100.5 / 202.0 / 404.6 Hz (sample of 2 trials × 21 GRNs) |
| same seeds + conditions → identical counts and spike trains, with jobs permuted, trial list permuted, 2 threads vs 1 thread | PASS (42 jobs) |
| GRN *output* spike trains identical across 7 conditions within a trial (intact + 6 silencings) | PASS (observed; 689 synapses onto the GRNs exist in C, so this is an empirical, not a guaranteed, property) |

### G5. Speed

| setting | wall per 1-s trial per condition |
|---|---|
| Brian2, original path, 1 process (ENG meta files) | 5.8–13.5 s per trial (incl. network construction), about 2.7–3.4 GB RAM per process |
| fastlif, full network (127k neurons), 2 threads | 0.75–0.81 s/job amortized |
| fastlif, closure 9.2k neurons, 2 threads, 512 jobs | **0.048 s/job (100 Hz), 0.051 s/job (400 Hz)** amortized |
| fastlif, grown closure 19.3k (v630) / 18.5k (v783), 1 thread | 0.235–0.282 s/job (measured under load average 7 on 4 cores) |

| fastlif, grown closure, **4 threads**, 400 single-silencing jobs (50 neurons × 8 trials), load average 6.5–7.8 | v630: 0.171 (100 Hz), 0.132 (400 Hz); v783: 0.136 (100 Hz), 0.138 (400 Hz) s/job |

**Projections** (worst measured 0.171 s/job, contended):
- 3,200 conditions × 8 trials = 25,600 jobs → **73 min**;
- 480 pair conditions × 8 trials = 3,840 jobs → **11 min**.

On an idle machine (single-thread 0.24 s/job ÷ 4) these become about 26 min and 4 min. Add a few % for boundary
re-runs: at 400 Hz, 4–18% of jobs flagged against the current closure in this benchmark. Each flagged job is re-run
once after expansion, and the closure persists, so this rate falls over time.

**Speed-up.**
- Per core: Brian2 about 6 core-s per trial vs fastlif 0.05–0.24 core-s, i.e. **≈ 25× (19k closure) to ≈ 100×
  (9k closure)**.
- At machine level: Brian2 can run at most about 4 processes in the 15 GB cgroup (≈ 1.5–3 s/job amortized at best)
  vs fastlif 0.13–0.17 s/job under contention. That is about **10–20×**, and fastlif uses about 1 process and
  < 4 GB.

Logs: `06_g4_g5_v630_2threads.log`, `09_g5_single_thread.log`, `11_g5_4threads.log`.

## 5. Deviations from the original and known limitations

1. **RNG.** fastlif uses its own CRN streams (PCG64) instead of Brian2's global MT19937. The distributions are
   identical (S11), so results are statistically, not bitwise, comparable to Brian2 runs. Given identical input
   trains they are bitwise identical (G0).
2. **Floating point.** The arithmetic mirrors Brian2's generated Cython (same constants and operation order, no
   fastmath). G0 shows identical spike trains over 149k spikes. Platform libm differences in `exp` could in principle
   change L2/L8–L10 by an ulp on other machines; constants are asserted against Brian2 in `g0_brian2_exact.py`.
3. **MN9_R** has no v783 id in `feasibility/ids` (the right MN9 changed id between versions). It is reported as N/A
   for v783; identifying its v783 successor is a data task, not a simulator issue.
4. **`inout` silencing** (also drop input to silenced neurons) is an extension for the design's sensitivity check,
   not original behavior. The default is outgoing-only, as in `model.silence`.
5. Only Brian2's default (Cython runtime) target was compared; this is what the authors and ENG use.
6. The closure grows with the number of trials and conditions run. Speed is linear in |C|; exactness is unaffected.
7. Memory: one process holds the full network (about 0.3 GB) plus an (n_jobs × |C|) int32 count array. A 2,000-job
   call peaked at 3.9 GB, so use ≤ 1,000 jobs per call when other Brian2 jobs share the 15 GB cgroup. The OOM killer
   was active during validation and killed two Brian2 reference runs, which were resumed.

## 6. CLI usage

```bash
PY=/home/user/venv-fly/bin/python; cd /home/user/fly_or_fail/sim
# (once per version) build the closure set from intact activity at the planned intensities
$PY reduce.py build --ver v630 --rates 50,100,200,300,400 --trials 0-7 --threads 4
$PY reduce.py info  --ver v630
# run conditions x rates x trials on the closure, with automatic boundary check + exact expansion
#   conditions.json: [{"name": "intact", "silence": []}, {"name": "k1", "silence": [7205759406...]},
#                     {"name": "half_grn", "silence": [], "stim": [<subset of sugar-right GRN ids>]}]
$PY fastlif.py --ver v630 --conditions conditions.json --rates 100,200,400 --trials 0-7 --threads 4 \
    --out out/batch_001.npz            # add --record 720575940660219265 to save MN9 spike steps; --inout; --salt
```

Output `.npz` (one row per job, job = condition × rate × trial):
- `counts` (n_jobs × |C|, uint16), `fid` (column FlyWire ids);
- `job_cond`, `job_rate`, `job_trial`, `nviol` (must be 0), `n_expansions`;
- optional `spk_job` / `spk_step` / `spk_fid` (spike time = step × 0.1 ms).

The default stimulus is the sugar-right GRNs present in the version (21 in v630, 20 in v783), as in `simlib.sugar_right`.

Python API: `reduce.run_exact(ver, stim_fids, jobs, threads=4, record=..., inout=...)`, where
`jobs = [{'rate': Hz, 'trial': seed, 'silence': [fids], 'stim': [fids] or None}, ...]`.
Trial *t* always uses CRN seed *t*: the same seed in every condition is the paired design of PROJECT_DESIGN §5.2.
