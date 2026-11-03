# Feasibility report (ENG)

_Author: ENG (relaunched run). Date: 2026-11-03. Status: final for the Brian2 reference dataset and reproduction gate._

**Citation convention.** Every number is followed by the log or file it comes from. `logs/…` means
`/home/user/fly_or_fail/feasibility/logs/…`. `out/ref/…` means `/home/user/fly_or_fail/feasibility/out/ref/…`.
Code that produced a log has the same stem in `/home/user/fly_or_fail/feasibility/`. Statements marked **[not logged]**
or **[not re-verified]** are inherited from earlier documents or are interpretation, not measurements.

## 0. Summary and dataset index

* **Reproduction gate.** Strictly by the criteria fixed in `gate.py` before looking at results, the primary run (seeds 0–19)
  **FAILS** by a hair: 1 of 20 sub-criteria (per-neuron Spearman ρ = 0.9956 for the "silence 720575940617937543" condition
  against a reference 5th percentile of 0.9960) [logs/ref/20_gate.log]. Every other sub-criterion passes, including all
  10 MN9 comparisons and all 5 active-set overlaps. An independent replicate with fresh seeds 20–39 and the same criteria
  **PASSES all** [logs/ref/20_gate_rep2.log]. My judgement is that the model reproduces the authors' outputs
  (details and caveats in §4). The formal verdict on the primary set is nonetheless FAIL; the PI decides how to treat that.
* **Reference dataset.** 28 parquet files, 420 trials, 3,398,664 spike rows, 6.9 MB [logs/ref/22_manifest_totals.log],
  index in `out/ref/MANIFEST.csv` (sha256 included), schema identical to the authors' files [logs/ref/23_schema_check.log].
* **MN9 mapping.** The notebook's right MN9 (720575940645521262) is absent from v783. Its v783 counterpart is
  **720575940618238523** (cell_type CB0701, annotation side `left`, nerve PhN) [logs/ref/30_mn9_mapping.log].
* **Key engineering finding.** The "42 s per trial" seen earlier is Cython re-compilation, not simulation. Inside one
  Python process Brian2's auto-generated function names advance every trial, so the generated source changes and gets
  recompiled. Running **one fresh process per trial** avoids this (§5).

### Reference data layout

`out/ref/<version>/<exp>.parquet` with columns `t` (float64, s), `trial` (int64), `flywire_id` (int64), `exp_name` (str),
brotli-compressed, exactly as `model.run_exp` writes them [logs/ref/23_schema_check.log]. Next to each file is
`<exp>.meta.json` (seeds, input IDs, parameters, per-trial wall time, n_active, RSS, model repo HEAD, library versions).
Per-trial shards are in `out/ref/<version>/_shards/<exp>/`. Input set: Shiu's 21 right sugar GRNs for v630 and the 20 of them
present in v783 [logs/03_extract_ids.log; out/ref/v783/*.meta.json].

| Version | Experiments (file stem) | Trials each | Seeds |
|---|---|---|---|
| v630 | `sugarR_{50,100,200}Hz` | 20 | 0–19 |
| v630 | `sugarR-<id>_100Hz` for the 3 stored silencing IDs (720575940617937543, 720575940621754367, 720575940622695448) | 20 | 0–19 |
| v630 | `…_rep2` copies of the 5 gate conditions (100 Hz, 200 Hz, 3 silencings) | 20 | 20–39 |
| v630 | `sugarR_{10,20,30,40,60,75,150}Hz` | 10 | 0–9 |
| v783 | `sugarR_{50,100,200}Hz` | 20 | 0–19 |
| v783 | `sugarR_{10,20,30,40,60,75,150}Hz` | 10 | 0–9 |

(Counts and seed ranges: `out/ref/MANIFEST.csv`, [logs/ref/22_manifest.log].)

**Seeds.** The authors' `model.py` never seeds Brian2 (each trial draws OS entropy). I call `brian2.seed(seed_offset + trial)`
immediately before each unmodified `model.run_trial` (`ref_run.py`). Trial *t* of every primary condition uses seed *t*
(common random numbers across conditions, as in PROJECT_DESIGN §5.2); `_rep2` uses 20 + *t*. Seeding changes no model
semantics. It makes runs bit-reproducible: two separate processes with the same seeds gave identical spike trains
[logs/ref/00_determinism_compare.log].

**Provenance caveat (disclosed).** Trials 0–13 of v630 `sugarR_100Hz` and `sugarR_200Hz` came from a first attempt that
used a persistent process (the slow-recompile problem appeared at trial 10, so I aborted it). Trials 14–19 were run in
fresh processes. The two modes are numerically equivalent: trial 11 from the persistent process is bit-identical to a
fresh-process run with the same seed [logs/ref/02_fresh_vs_persistent_equivalence.log]. Trials 0–3 are also bit-identical
to a third, independent method (build once, `store`/`restore`) [logs/ref/05_bench_store_restore_v630_100Hz.log]. The aborted
log is kept in `logs/ref/aborted_persistent/`. The 10-trial `run_exp` outputs of the previous run in `out/v630`, `out/v783`
are unseeded, are not part of the reference set, and were not used.

## 1. Environment

| Item | Value | Source |
|---|---|---|
| Machine | Firecracker VM, Linux 6.18.44, 4 vCPU (Intel Xeon, 1 thread/core), 16,091 MB RAM, no swap, 27 GB disk free | logs/ref/00_env_now.log |
| Software | Python 3.13.18, brian2 2.11.0, numpy 2.5.4, pandas 3.1.0, scipy 1.18.1, pyarrow 26.0.0, joblib 1.6.0, g++ 13.3.0 | logs/ref/00_env_now.log |
| Brian2 code generation | target `auto` resolved to Cython (`CythonCodeObject`); first toy run incl. compile 8.96 s | logs/01_env_check.log |
| Model code | `philshiu/Drosophila_brain_model` HEAD 91bdd1e7, working tree clean (not modified) | logs/ref/00_env_now.log |
| Annotations | `flyconnectome/flywire_annotations` HEAD a83b277 | logs/ref/00_env_now.log |

The machine is **shared** with other agents. At 02:19 UTC their Brian2 jobs were running next to mine and the load average
was 8.56 on 4 cores [logs/ref/06_machine_load_snapshot.log]. A `ps` at about 01:57 showed such jobs already started at 01:49–01:50
**[not logged]**, so I use 01:49 as the cut-off for the "uncontended" window. Timings after it are inflated and are excluded
from the cost estimates (§5).

## 2. Data facts

Source: `logs/02_data_inspect.log` unless noted. The consistency checks (index↔ID agreement, no duplicate pairs, no self loops, no NaN) passed for both versions.

| Quantity | v783 | v630 |
|---|---|---|
| Neurons (completeness file) | 138,639 (all `Completed`) | 127,400 (all `Completed`) |
| Edges (min 1 synapse, no threshold) | 15,091,983 | 14,687,178 |
| Synapses | 54,492,922 | 52,793,639 |
| Synapses per edge: mean / median / max | 3.61 / 2 / 2,405 | 3.59 / 2 / 2,358 |
| Inhibitory edges / synapses | 39.97% / 40.37% | 40.08% / 40.41% |
| Neurons with out-edges / in-edges | 138,005 / 137,090 | 127,015 / 126,793 |
| Mixed-sign presynaptic neurons | 0 | 0 |

* IDs shared by v630 and v783: 106,220; only v783: 32,419; only v630: 21,180.
* Sign is a property of the presynaptic neuron (weights = `Excitatory x Connectivity`).
* v783 model sign vs annotation `top_nt` (ach, dop, ser, oct → +; gaba, glut → −): agreement **95.37%** over 129,764
  neurons. Disagreeing neurons have lower mean transmitter confidence (0.462 vs 0.689) [logs/08_annotations_check.log].
* Annotation coverage of v783: 138,625 of 138,639 neurons have an annotation row; 623 annotation rows are not in
  v783 completeness [logs/08_annotations_check.log].
* **L/R label flip.** The notebook's "left" MN9 (720575940660219265) has annotation `side = right`
  [logs/08_annotations_check2.log]. All 20 present notebook-"right" sugar GRNs are annotated `left`
  [logs/08_annotations_check.log].
* **Input-set composition (v783 annotation).** The notebook "sugar R" set (21 IDs) is 9 `sugar` (LB3c), 5
  `high_salt/heavy_metal` (LB3d), 4 `putative_attractive` (LB4b) and 2 `sugar/low_salt` (LB3b), plus 1 ID absent
  from v783 (720575940620900446). The "water R" set contains 7 annotated `sugar` (LB3c)
  [logs/08_annotations_check2.log].

## 3. Extracted IDs and paper analyses

IDs were extracted from `example.ipynb` and `figures.ipynb` (first definition of each list) and from
`sez_neurons.pickle` [logs/03_extract_ids.log; files in `ids/`]:

| Class (side as in notebook) | n | in v630 | in v783 | Notebook, cell |
|---|---|---|---|---|
| sugar GRN (right) | 21 | 21 | 20 | example.ipynb, 3 |
| sugar GRN (left) | 10 | 10 | 9 | figures.ipynb, 76 |
| water GRN (right) | 18 | 18 | 18 | figures.ipynb, 32 |
| bitter GRN (right) | 21 | 21 | 20 | figures.ipynb, 23 |
| Ir94e GRN (right) | 18 | 18 | 18 | figures.ipynb, 23 |
| JON CE / F / D_m | 70 / 60 / 16 | all | 69 / 60 / 16 | figures.ipynb, 50 |
| MN9 left / right | 1 / 1 | 1 / 1 | 1 / **0** | figures.ipynb, 17 |
| aBN1, DN1_1, DN2_l | 1 each | 1 each | 1 each | figures.ipynb, 54, 62 |
| three inhibitory silenced | 3 | 3 | 2 | figures.ipynb, 70 |
| SEZ pickle: 106 types, 369 unique IDs | 369 | 369 | 305 | sez_neurons.pickle |

No ID appears in two non-SEZ classes [logs/03_extract_ids.log].

Analyses defined by the notebooks [logs/03_notebooks_dump.log]:

* `example.ipynb` (cells 7–19): 200 Hz and 100 Hz sugar-GRN drive (30 trials each), then single silencing of the 3 most
  active neurons at 100 Hz, reading out MN9 = 720575940660219265. This is the source of the stored files used in the gate.
* `figures.ipynb`, Fig 1D: λ = 10, 20, …, 200 Hz sugar drive, top-200 neurons by rate at 200 Hz. Fig 1E: each top-200
  neuron driven alone at λ = 25…200 Hz (step 25), MN9 readout. Fig 1F: silencing each top-200 neuron at λ = 50…120 Hz
  (step 10) with sugar drive, MN9 readout. Fig 2: both MN9 IDs, SEZ types, λ = 50/100/150/200. Further figures (3A/B,
  4a–e, 5b–g + S5, S1D, S4) exist in the notebook; I read only their headings. The JON, aBN1, DN, water, bitter and Ir94e ID lists
  were taken from the cells listed in the table above.

## 4. Reproduction gate

**Comparison.** Our v630 reference runs (20 trials) against the authors' stored `results/example/` outputs (30 trials each):
`sugarR.parquet` (200 Hz), `sugarR_100Hz.parquet`, and the three `sugarR-<id>.parquet` (100 Hz, single silencing)
[logs/04_stored_results_inspect.log; logs/ref/20_gate.log]. Rate = spike count per 1-s trial. CIs are t-intervals over trials;
differences use Welch.

**Criteria, fixed in `gate.py` before looking at any result (my choice):**

* **G1** (MN9, both v630 IDs × 5 conditions = 10 comparisons): every Bonferroni-adjusted (α = 0.05/10) Welch CI of
  *ours − stored* contains 0.
* **G2** (per-neuron mean rate, union of spiking neurons, excluding the 21 Poisson-driven GRNs): Pearson r ≥ 0.95 and
  Spearman ρ ≥ 0.80 and both ≥ the 5th percentile of a stored-vs-stored reference (1000 random 15/15 trial splits of the
  authors' 30 trials), in all 5 conditions.
* **G3** (active set = neurons with mean rate ≥ 1 Hz): Jaccard ≥ 0.85 and ≥ that reference's 5th percentile, in all 5 conditions.

### Primary run (seeds 0–19) [logs/ref/20_gate.log]

| Condition | MN9_L (…265) ours [95% CI] | stored [95% CI] | Δ (ours − stored) [95% CI] | MN9_R (…262) ours [95% CI] | stored [95% CI] | Δ [95% CI] |
|---|---|---|---|---|---|---|
| 200 Hz | 92.15 [89.91, 94.39] | 93.27 [92.07, 94.46] | −1.12 [−3.61, +1.38] | 63.70 [61.95, 65.45] | 61.80 [60.21, 63.39] | +1.90 [−0.40, +4.20] |
| 100 Hz | 70.00 [68.14, 71.86] | 67.03 [64.53, 69.54] | +2.97 [−0.08, +6.01] | 50.55 [48.41, 52.69] | 48.63 [46.86, 50.41] | +1.92 [−0.79, +4.63] |
| 100 Hz, silence …937543 | 65.05 [62.21, 67.89] | 63.27 [61.47, 65.06] | +1.78 [−1.50, +5.07] | 45.35 [42.76, 47.94] | 45.67 [44.00, 47.33] | −0.32 [−3.32, +2.69] |
| 100 Hz, silence …754367 | 67.45 [65.80, 69.10] | 66.90 [64.59, 69.21] | +0.55 [−2.22, +3.32] | 49.70 [47.30, 52.10] | 49.70 [47.93, 51.47] | 0.00 [−2.91, +2.91] |
| 100 Hz, silence …695448 | 70.95 [68.21, 73.69] | 71.17 [69.49, 72.84] | −0.22 [−3.36, +2.92] | 50.15 [48.11, 52.19] | 51.00 [50.01, 51.99] | −0.85 [−3.08, +1.38] |

All values in Hz. **G1 passes in all 10 comparisons** (every Bonferroni-adjusted 99.5% CI contains 0; the widest
relative difference is +4.4%, MN9_L at 100 Hz).

| Condition | Pearson r | Spearman ρ (ref 5th pct) | Active set ours / stored / ∩ | Jaccard (ref 5th pct) |
|---|---|---|---|---|
| 200 Hz | 0.9999 | 0.9991 (0.9983) | 371 / 370 / 367 | 0.9813 (0.9516) |
| 100 Hz | 0.9993 | 0.9978 (0.9971) | 326 / 326 / 324 | 0.9878 (0.9818) |
| 100 Hz, silence …937543 | 0.9997 | **0.9956 (0.9960) — below** | 320 / 319 / 318 | 0.9907 (0.9814) |
| 100 Hz, silence …754367 | 0.9998 | 0.9986 (0.9973) | 328 / 325 / 325 | 0.9909 (0.9787) |
| 100 Hz, silence …695448 | 0.9995 | 0.9983 (0.9971) | 330 / 330 / 328 | 0.9880 (0.9818) |

* **G3 passes in all 5.** **G2 fails in one of five conditions** (ρ = 0.9956 vs 0.9960; the absolute floors r ≥ 0.95,
  ρ ≥ 0.80 pass with huge margin, and Pearson r for that condition is above the reference median).
* Diagnostic: no neuron has |z| > 3 in any condition (max |z| 1.96–2.63; ~1 expected by chance among ~400 neurons)
  [logs/ref/20_gate.log].
* **Formal primary verdict: FAIL** (G2, 1 of 5 conditions, margin 0.0004 in ρ).

### Independent replicate (seeds 20–39, same criteria) [logs/ref/20_gate_rep2.log]

**PASS on G1, G2 and G3 in all five conditions.** Ranges: Pearson r 0.9993–0.9999; Spearman ρ 0.9967–0.9993 (all above the
reference 5th percentile); Jaccard 0.9848–0.9938; MN9 Δ within ±5.6% (largest: MN9_R at 100 Hz, +2.72 Hz, +5.6%, unadjusted
95% CI [+0.35, +5.08], adjusted 99.5% CI [−0.74, +6.18]). The condition that missed in the primary run now has ρ = 0.9967
(reference 5th pct 0.9960).

### Pooled view (40 trials vs stored 30; supplementary, not a gate) [logs/ref/20_gate_pooled.log]

For the five conditions: Pearson r 0.9995–0.9999, ρ 0.9959–0.9994, Jaccard 0.9892–1.0000. The silence-…937543 condition has
ρ = 0.9959. At 100 Hz intact, our MN9 rates are slightly above the stored ones in every replicate (pooled Δ = +2.02 Hz for
MN9_L, +2.32 Hz for MN9_R, 95% CI [+0.15, +4.48]; 4–5%). The other four conditions show Δ of either sign and
|Δ| ≤ 1.46 Hz. I cannot exclude a small (≤ 5%) offset at 100 Hz intact; it is within what 30 stored trials can resolve
(stored sd ≈ 4.8–6.7 Hz) and absent from the silenced conditions.

**Reading.** The model, run with Brian2 2.11 on this machine, reproduces the authors' stored MN9 rates, per-neuron rates and
active sets to within the sampling noise of their 30 trials. I treat the reproduction as acceptable for validating SIM,
while disclosing the formal FAIL on the primary set.

## 5. Benchmark

### Measured per-trial cost

All of these use the unmodified `model.run_trial` code path. Timing summary: [logs/ref/04_trial_timing.log].

| Quantity | Value | Source |
|---|---|---|
| Phase split, persistent process, cache warm (λ = 150 Hz, v630) | build 0.99–1.16 s + prepare 0.19–0.20 s + simulate 3.74–3.79 s = 5.0–5.1 s (trial 0 includes first-use build: 7.1 s) | logs/04_probe_one_trial_v630_split.log |
| Fresh-process trial, **uncontended** (n = 186, trial 0 of each job excluded) | `run_trial` median 6.45 s, mean 6.64 s, p95 9.78 s; full cost incl. interpreter start-up (gap between consecutive trial outputs, 2 concurrent workers) **median 7.92 s**, p95 11.52 s | logs/ref/04_trial_timing.log |
| Peak RSS per process | median 2,715 MB, max 3,417 MB | logs/ref/04_trial_timing.log |
| Authors' `run_exp(n_proc=1)` re-run today, 3 trials | 19 s total, 6.5 s/trial | logs/ref/01_bench_runexp_v630_100Hz_3tr.log |
| Build once + `store`/`restore` | build+prepare once 8.8 s; `restore` 0.03–0.05 s; restore + run 5.0–6.3 s per trial **under load**; spike trains for 4/4 trials identical to the reference | logs/ref/05_bench_store_restore_v630_100Hz.log |
| One-time cost of a new λ (first trial, cold cache) | 40.6–74.7 s (v630, λ = 10, 20, 30, 40, 50, 60, 75 Hz; part of this was under load) | logs/ref/04_trial_timing.log |

Later jobs (λ = 60, 75, 150 Hz, the `_rep2` runs) show `run_trial` medians of 10–27 s because other agents' jobs were
running (load average 8.5 on 4 cores) [logs/ref/04_trial_timing.log; logs/ref/06_machine_load_snapshot.log]. Those
timings measure contention, not the model, and are not used in the budget. The `store`/`restore` per-trial figure
(5.0–6.3 s) was also taken under load, so it is an upper bound. The uncontended simulate-only cost is 3.6–3.8 s
[logs/04_probe_one_trial_v630_split.log]. A clean store/restore timing still has to be made on an idle machine.

### Why 5 s per trial in one place and 42 s in another

Observed values:

* Previous run, authors' `run_exp(n_proc=1)`, 10 trials: v630 200 Hz 418 s, v630 100 Hz 410 s, v783 200 Hz 361 s, v783
  100 Hz 368 s (36–42 s/trial), but the single-silencing run took 51 s (v630) and 53 s (v783), i.e. 5 s/trial
  [logs/04_repro_run.log].
* Persistent probe, first attempt at the reference runs (v630 100 Hz): trials 0–9 averaged 5.70 s and trials 10–13 averaged
  41.93 s (200 Hz: 5.78 s and 42.05 s) [logs/ref/04_trial_timing.log; logs/ref/aborted_persistent/].

**Mechanism (verified).** Time tracks Cython compilation, not simulation:

1. Controlled test with a never-used λ (77 Hz), one persistent process, 4 trials: 68.4, 63.3, 65.4, 59.4 s per trial, with
   42, 40, 36 and 25 new Cython extensions compiled in those trials [logs/ref/03_bench_naming_pass1_v630_77Hz.log].
   The identical sequence run again (cache warm): 14.3, 9.1, 8.3, 8.0 s with **0** compilations
   [logs/ref/03_bench_naming_pass2_identical_v630_77Hz.log] (under load; see above).
2. The cause of the changing source: in a persistent process, the name of the last `PoissonInput`'s binomial function advances
   by 21 per trial (`poissoninput_binomial_20`, `_41`, `_62`) [logs/ref/03_bench_naming_pass3_names_v630_77Hz.log]. The
   function name is part of the generated Cython source, so every trial in the same process gets new source and a new
   compile (about 21 extensions). A new process restarts the counter at 0, so its code is found in the on-disk cache
   (`~/.cython/brian_extensions`).
3. The rate λ is baked into the generated code, so every new λ costs one cold compile (40–75 s, shared by v630 and v783,
   because the code does not depend on N: v783 first trials at λ = 10, 20, 30, 50 were 6.0–8.1 s once the v630 job at that λ had finished)
   [logs/ref/04_trial_timing.log]. Silenced neuron IDs do not trigger compiles: trial 0 of the three silencing jobs
   took 5.0–5.2 s [logs/ref/04_trial_timing.log].

So:

* **5 s/trial** = warm cache; sim 3.7 s + build ~1 s + prepare 0.2 s.
* **42 s/trial** = cold or advancing names, i.e. recompilation.
* Previous run (inference consistent with the data above): the first two experiments per version compiled, and the silencing
  run reused cached code. The same reasoning explains why the earlier "5 s" persistent probes (2–3 trials) looked fast once the
  cache was warm.

Minor contributors:

* **Process start-up**: about 1.5 s per fresh process (median gap 7.92 s minus run_trial 6.45 s) [logs/ref/04_trial_timing.log].
* **First-touch memory**: this VM costs 2.2–3.3 s per GB on the first touch of never-used memory and 0.15 s afterwards
  [logs/05_mem_touch_test.log]. At most a few seconds once per process (trial 0 in cache-warm fresh processes is 5.0–9.4 s vs
  about 6 s typical); it cannot explain 40 s on every trial of a process whose RSS is stable.
* **First compile ever**: 8.96 s for a toy network [logs/01_env_check.log].

**Production recipe used here.** One fresh process per trial (`ref_queue.sh`), 2 workers. Alternative, not yet fully
validated: build once and `store`/`restore` (exact on the 4 trials tested; restore and run in the same process; no
re-compilation since no new objects are created). Not tested: silencing after `restore`, and clean timing.

## 6. Active set and I/O curve

Source: `out/ref/analysis/active_io_summary.csv`, [logs/ref/21_active_io.log]. "≥ 1 Hz" = mean count per 1-s trial ≥ 1.
"≥ 1 spike" = any spike in any trial. The 10-trial and 20-trial runs are not directly comparable for "≥ 1 spike"
(e.g. v630 100 Hz: 387 in the first 10 trials, 402 in 20), so the log also gives the first-10-trial count. The driven GRNs
are included in the counts unless stated.

| λ (Hz) | trials | v630 ≥ 1 spike | v630 ≥ 1 Hz (excl. 21 GRNs) | v783 ≥ 1 spike | v783 ≥ 1 Hz (excl. 20 GRNs) |
|---|---|---|---|---|---|
| 10 | 10 | 39 | 28 (7) | 30 | 24 (4) |
| 20 | 10 | 63 | 45 (24) | 61 | 42 (22) |
| 30 | 10 | 131 | 61 (40) | 76 | 62 (42) |
| 40 | 10 | 218 | 107 (86) | 214 | 92 (72) |
| 50 | 20 | 363 | 235 (214) | 330 | 207 (187) |
| 60 | 10 | 372 | 279 (258) | 350 | 269 (249) |
| 75 | 10 | 393 | 333 (312) | 380 | 318 (298) |
| 100 | 20 | 402 | 347 (326) | 401 | 346 (326) |
| 150 | 10 | 426 | 364 (343) | 398 | 365 (345) |
| 200 | 20 | 445 | **392 (371)** | 441 | **391 (371)** |

At λ = 200 Hz about 391–392 neurons exceed 1 Hz, which matches the design assumption "about 400 candidates"
(PROJECT_DESIGN §5.2). Mean spikes per trial: 243 (10 Hz) to 16,967 (v630 200 Hz) [logs/ref/21_active_io.log].

**MN9 rate vs λ** (Hz, mean over trials [95% CI], trials with ≥ 1 spike in brackets). v783 "partner" is …523 (§7).

| λ | v630 MN9_L (…265) | v630 MN9_R (…262) | v783 MN9_L (…265) | v783 partner (…523) |
|---|---|---|---|---|
| 10 | 0.00 (0/10) | 0.00 (0/10) | 0.00 (0/10) | 0.00 (0/10) |
| 20 | 0.00 (0/10) | 0.00 (0/10) | 0.00 (0/10) | 0.00 (0/10) |
| 30 | 0.80 [−0.08, 1.68] (5/10) | 0.20 [−0.25, 0.65] (1/10) | 0.00 (0/10) | 0.00 (0/10) |
| 40 | 3.70 [1.85, 5.55] (10/10) | 2.60 [1.08, 4.12] (9/10) | 2.80 [1.55, 4.05] (10/10) | 2.40 [1.32, 3.48] (10/10) |
| 50 | 18.20 [15.43, 20.97] | 13.40 [11.30, 15.50] | 12.90 [11.16, 14.64] | 10.40 [8.70, 12.10] |
| 60 | 35.20 [31.88, 38.52] | 27.20 [23.54, 30.86] | 28.30 [24.42, 32.18] | 23.00 [19.40, 26.60] |
| 75 | 53.10 [51.09, 55.11] | 38.30 [35.52, 41.08] | 43.30 [40.28, 46.32] | 36.90 [33.91, 39.89] |
| 100 | 70.00 [68.14, 71.86] | 50.55 [48.41, 52.69] | 59.85 [57.99, 61.71] | 46.50 [44.55, 48.45] |
| 150 | 85.00 [81.87, 88.13] | 58.30 [55.84, 60.76] | 80.40 [75.92, 84.88] | 58.80 [55.68, 61.92] |
| 200 | 92.15 [89.91, 94.39] | 63.70 [61.95, 65.45] | 90.25 [88.26, 92.24] | 62.70 [60.62, 64.78] |

(50, 100, 200 Hz: 20 trials, all with ≥ 1 spike; 60, 75, 150 Hz: 10 trials, all with ≥ 1 spike [logs/ref/21_active_io.log].)

**Threshold.** No MN9 spike in 10 trials at 10 and 20 Hz. At 30 Hz v783 is still silent (0/10 trials), v630 is marginal
(MN9_L 5/10 trials, 0.8 Hz). All four neurons fire in 9–10 of 10 trials at 40 Hz (2.4–3.7 Hz). The rate then rises about
5× from 40 to 50 Hz and again about 2× from 50 to 60 Hz (v630 MN9_L 3.7 → 18.2 → 35.2), flattening above 150 Hz (85.00 → 92.15 Hz for v630 MN9_L).
The onset sits between 30 and 40 Hz and the steep part between 40 and 75 Hz. For v630 MN9_L the half-value of the 200 Hz rate
(46.1 Hz) lies between the 60 Hz and 75 Hz points (35.2, 53.1). The curve is steep around the default regime, so
λ-dependent contrasts will be sensitive to the λ grid; grid density between 40 and 100 Hz matters. v783 is shifted to
higher λ and lower rates than v630 for the shared MN9 (…265): 59.85 vs 70.00 Hz at 100 Hz.

## 7. MN9 ID mapping

* The notebook's right MN9, **720575940645521262**, is in v630 but **not in v783** and not in the annotation file
  [logs/ref/30_mn9_mapping.log].
* The annotation file has exactly two `CB0701` neurons (super_class motor, ingestion motor neuron, nerve PhN, acetylcholine)
  in v783: 720575940660219265 (side `right`, the notebook's "left" MN9: the known L/R label flip) and
  **720575940618238523** (side `left`). The latter is absent from v630 [logs/ref/31_mn9_membership.log], so it is a root ID
  created after v630, consistent with the old root ID …262 having been superseded.
* Independent connectivity evidence (`mn9_map.py`): cosine similarity of the synapse-count input vector of v630 …262 to
  every v783 neuron. Top hit is …523 with cos 0.673 (210 shared presynaptic partners; 242 v630 inputs, 241 v783 inputs);
  the next best is 0.433 (a CB0871 motor neuron). The cross-lateral pairing …262 vs v783 …265 gives 0.193.
  Positive control: the notebook's left MN9 (…265, present in both versions) matches itself best at 0.727 (next 0.453), so
  ~0.7 is the ceiling to expect across materializations [logs/ref/30_mn9_mapping.log].
* **Mapping: v630 …262 → v783 …523.** v783 MN9 pair = {…265, …523}. Evidence is annotation (type, side, nerve) plus input
  connectivity; I could not confirm it through FlyWire edit history (network blocked), so it remains inferred.
* Rates for the mapped neuron: 46.50 Hz at 100 Hz and 62.70 Hz at 200 Hz (v783), against 50.55 and 63.70 Hz for …262 in
  v630 [logs/ref/21_active_io.log].

## 8. Structural quick facts (from logs/07)

The original `logs/07_structural_v783.log` held only a header line (interrupted run); it is kept as
`logs/07_structural_v783_interrupted_prior_run.log`. I re-ran `structural.py` and **fixed two bugs in it**: (i) a numpy-int32
overflow inside networkx, which crashed the run [logs/07_structural_v783_crashed_run.log]; (ii) the target node's capacity was
1, which forced every max-flow value to be ≤ 1. Both fixes are marked in the script. The output of the buggy intermediate run was
discarded. Final logs: `logs/07_structural_v783.log`, `logs/07_structural_v630.log`. v783 also reports the mapped partner …523.

* **Hop distance** from the sugar-GRN set to each MN9 is **2** in both versions and for both MN9 IDs, on the unsigned and the
  excitatory-only graph [logs/07_structural_v783.log; logs/07_structural_v630.log].
* **Downstream reach (unsigned)**, neurons within ≤ k hops, excluding seeds. v783: k = 1: 265; 2: 10,350; 3: 96,076 (69.3% of the
  brain); 4: 134,116 (96.7%). v630: 265; 10,296; 93,986 (73.8%); 125,905 (98.8%).
* **Excitatory-only**: v783 k = 2: 8,662; 3: 64,009 (46.2%); 4: 130,089 (93.8%). v630 k = 2: 8,611; 3: 61,751 (48.5%); 4: 122,789 (96.4%).
* **Node-disjoint paths** (Menger; unit node capacities, sugar-GRN set → MN9, unsigned graph restricted to nodes on walks of
  length ≤ L): v783 MN9_L: 12 (L = 2), 20 (L = 3, 4); v783 partner …523: 20 at L = 2, 3, 4. v630 MN9_L: 12, 21, 21; v630
  MN9_R: 21, 21, 21. For the MN9 with all inputs reachable the count equals the number of input GRNs (20 or 21): there are as
  many vertex-disjoint input→MN9 routes as inputs, so the minimum vertex cut in this unsigned graph is not smaller than the
  input set.
* **Cost of the structural computation**: scipy max-flow 0.2–16.7 ms per MN9 and L; networkx 2–124 ms (skipped above 300,000
  edges; L = 4 subgraphs have about 3,600–3,700 nodes and 355,000–365,000 edges). The whole script takes about 8 s (v783) and 11 s (v630).
  Per-neuron vertex-cut/dominator predictors on subgraphs of this size are therefore cheap (milliseconds each).

## 9. Resource availability

* **Compute here**: 4 vCPU, 16 GB RAM, no GPU [logs/ref/00_env_now.log]. A Brian2 process needs 2.7–3.4 GB resident
  [logs/ref/04_trial_timing.log], so RAM allows at most 4 concurrent processes; with the other agents active,
  2 is what I could use.
* **Public data bucket** `gs://lee-lab_brain-and-nerve-cord-fly-connectome/` is reachable with gsutil; `compiled_data/`
  lists three datasets [logs/08_banc_gcs.log]:
  * `banc_888`: 37.69 GiB.
  * `malecns_09`: 15.7 GiB; the simple edge list is 3,404,193,362 bytes.
  * `fafb_783`: 21.41 GiB; the simple edge list is 302,625,658 bytes.
* **Hemibrain**: `gs://hemibrain/` lists v1.0, v1.1, v1.2 [logs/08_gcs_banc_probe1.log]. The earlier note that it lacks most of the SEZ
  is **[not re-verified]**.
* **Authors' raw simulation archive** (Edmond, doi:10.17617/3.CZODIW): reported as blocked in PROJECT_DESIGN §4
  **[not re-verified here, not logged]**.
* **Stored outputs available locally**: 5 parquet files, 30 trials each [logs/04_stored_results_inspect.log].
* **Disk**: 27 GB free [logs/ref/00_env_now.log]. The on-disk Cython cache (`~/.cython/brian_extensions`) grows by 25–42
  extensions per cold trial [logs/ref/03_bench_naming_pass1_v630_77Hz.log]; its total size (about 340 MB when I looked)
  **[not logged]**.

## 10. Compute budget table

Trial counts are the PROJECT_DESIGN §4 blocks (750 + 25,600 + 3,840 + 12,000 = 42,190 trials; the design's "≈ 60 CPU-h" at
~5 s/trial corresponds to this count). Costs are recomputed from measured per-trial figures [logs/ref/40_budget.log]:

* **7.92 s** = measured fresh-process cost, uncontended [logs/ref/04_trial_timing.log];
* **6.45 s** = `run_trial` only [same log];
* **3.8 s** = simulate-only lower bound [logs/04_probe_one_trial_v630_split.log]; an upper bound for store/restore is the loaded
  5.0–6.3 s of §5.

| Block | Trials | CPU-h @ 7.92 s | CPU-h @ 6.45 s | CPU-h @ 3.8 s (bound) |
|---|---|---|---|---|
| Intact curve, 25 λ × 30 trials | 750 | 1.6 | 1.3 | 0.8 |
| Single-neuron curves, ~400 neurons × 8 λ × 8 trials | 25,600 | 56.3 | 45.9 | 27.0 |
| Pair pilot, 60 pairs × 8 λ × 8 trials | 3,840 | 8.4 | 6.9 | 4.1 |
| Robustness, ~1,500 conditions × 8 trials | 12,000 | 26.4 | 21.5 | 12.7 |
| **Total** | **42,190** | **92.8** | **75.6** | **44.5** |

| Workers | Wall-clock @ 7.92 s | @ 6.45 s | @ 3.8 s |
|---|---|---|---|
| 2 | 46.4 h | 37.8 h | 22.3 h |
| 3 | 30.9 h | 25.2 h | 14.8 h |
| 4 | 23.2 h | 18.9 h | 11.1 h |

Throughput per worker: 455 trials/h @ 7.92 s, 558 @ 6.45 s, 947 @ 3.8 s [logs/ref/40_budget.log]. The table assumes no
contention and ignores the one-time ~40–75 s compile per new λ.

**Implication for the 2026-11-05 deadline.** With the original Brian2 code, the full MVP screen needs ≈ 93 CPU-h, i.e. 23–46 h
of wall-clock on 2–4 dedicated workers (and the cores are shared). It is **not feasible with the original code at the planned
scope** unless the fast re-implementation (SIM) is validated and used for the screens, or the screen is cut. Note that the
design table's own estimate (≈ 60 CPU-h, ~20 h on 3 workers) assumed 5 s/trial, which a fresh-process trial does not reach.

## 11. Risks

1. **Formal gate miss.** The primary set fails G2 in 1 of 5 conditions by 0.0004 in ρ. The replicate passes. The
   pre-specified thresholds are my choice (stored-vs-stored 15/15 splits; absolute floors), not an external standard.
   A reviewer may prefer a different criterion. A small positive offset (≤ 5%) of our MN9 rates at 100 Hz intact is not
   excluded (§4).
2. **Persistent-process trap.** Any driver that loops over trials in one process (the authors' `run_exp(n_proc=1)` with a cold
   cache, or a custom loop) pays ~35–70 s per trial in compilation (§5). Use one process per trial, or `store`/`restore`.
3. **λ change = cold compile** (40–75 s once per λ). A dense λ grid in a screen costs ~1 min per new λ the first time.
4. **Shared, oversubscribed machine.** Timings fluctuated 2–4× (load average 8.5 on 4 cores). Budget estimates use only the
   uncontended window; wall-clock projections can be off by a factor of 2–3 when other jobs run.
5. **Memory.** 2.7–3.4 GB per process; 4 processes already approach 13 GB. Mixed with other agents' jobs (about 3–4 GB each),
   the 15.7 GB limit is reachable.
6. **Version dependence.** v783 gives lower MN9_L rates than v630 at the same λ (59.85 vs 70.00 Hz at 100 Hz) and a shifted
   onset (v783 silent at 30 Hz). Conclusions drawn on one version must be checked on the other (design §5.5).
7. **MN9 mapping is inferred** (§7), by annotation plus connectivity cosine 0.673, not through FlyWire edit history.
8. **Input set purity.** 11 of the 20 present "sugar" GRNs are annotated other than plain `sugar` (5 `high_salt/heavy_metal`, 4
   `putative_attractive`, 2 `sugar/low_salt`) [logs/08_annotations_check2.log]; "left/right" labels in the notebooks are
   flipped relative to the annotations.
9. **Active-set definitions depend on trial count** (≥ 1 spike grows with n; ≥ 1 Hz is stable). Use ≥ 1 Hz and a fixed number
   of trials when defining the candidate set. Per-condition counts are in `out/ref/analysis/active_io_summary.csv`.
10. **Common random numbers.** All primary conditions share seeds 0–19, so conditions are positively correlated trial by trial;
    this is intended for paired contrasts but unsuitable for treating conditions as independent samples. Independent seeds are in `_rep2`.
    SIM's implementation cannot match spike trains trial by trial (different RNG); validation can be distributional only.
11. **Transmitter-sign uncertainty.** 4.6% of model neuron signs disagree with the annotated transmitter (§2); the design plans a sign-flip
    robustness slice.
12. **Not verified here:** FlyWire edit history for the MN9 root ID; the Edmond archive; the hemibrain SEZ coverage claim; a clean
    (idle-machine) store/restore benchmark; silencing after `restore`.

## Appendix: scripts and logs created or modified in this run

Scripts (`/home/user/fly_or_fail/feasibility/`): `ref_run.py` (runner), `ref_queue.sh`, `ref_queue2.sh`, `ref_jobs*.txt`,
`gate.py`, `gate_pooled.py`, `active_io.py`, `mn9_map.py`, `timing_summary.py`, `budget.py`, `make_manifest.py`,
`bench_runexp.py`, `bench_naming.py`, `bench_store_restore.py`, `names_probe.py`, `run_benches.sh`; `structural.py` modified
(two bug fixes, original behaviour kept in `structural_orig_crashed.py.bak`). Logs: `logs/ref/*`, `logs/07_*`.
The model repo was not modified (working tree clean). Nothing was committed.
