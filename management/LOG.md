# RESEARCH LOG

_Append-only, newest entries at the bottom. Times are 2026-11-03 session times (UTC, container clock)._

## 2026-11-03: Phase 0 (setup)

- **Inputs.** The user brief (project idea, 7 requested deliverables, zero-tolerance quality bar)
  and the course syllabus PDF. Two uploads with the same md5, `b6630e33…`, so they are the same file.
- **Course facts (from the syllabus).** The final project is worth 30%: proposal 7%,
  presentation 10%, final report 13%. Presentations are 2026-12-10. The final project
  requirements were released 2026-11-03. The course emphasizes network models (SEM, DCM, Granger,
  DNNs) and brain dynamics.
- **Compute.** 4 vCPU, 15 GB RAM, no GPU, about 31 GB free disk. Python 3.13 with numpy 2.5 and
  pandas 3.0. brian2 and pyarrow are not installed yet.
- **Network.** Only the following were reachable:

  | Host or tool | Status |
  |---|---|
  | `github.com` via git | OK |
  | `raw.githubusercontent.com` | OK |
  | `pypi.org` | OK |
  | Server-side `WebSearch` | OK |
  | `mcp__Consensus__search` (abstract-level paper index) | OK |

  Blocked (proxy 403 / DNS): zenodo.org, codex.flywire.ai, flywire.ai, biorxiv (www and api),
  eutils/PMC, europepmc, openalex, semanticscholar, arxiv, crossref, doi.org, nature.com,
  elifesciences.org, cell.com, science.org, pnas.org, plos, frontiers, neuprint.janelia.org,
  janelia.org, huggingface.co, figshare, osf, dataverse, edmond.mpg.de, banc.community.
  WebFetch runs from inside the container, so it is blocked for the same hosts.

  The bio-research plugin MCP servers (pubmed, biorxiv, consensus-plugin, …) failed to connect
  (proxy tunnel 403).
- **Consequence.** Paper full texts cannot be read. Literature evidence is at abstract or snippet
  level, plus primary code and data in GitHub repos. This is recorded as a limitation and enforced
  through evidence tags.
- **Model repo.** Cloned `philshiu/Drosophila_brain_model` at commit `91bdd1e7…` (2024-09-14) to
  `/home/user/external/Drosophila_brain_model`. It contains `Connectivity_783.parquet` (100.8 MB),
  `Completeness_783.csv`, the v630 equivalents, `model.py` (Brian2 LIF), `figures.ipynb` and
  `example.ipynb`.
  - Model facts read from the source `[V-src]`: v_rest = v_reset = −52 mV, v_th = −45 mV,
    τ_m = 20 ms, synaptic τ = 5 ms, refractory period 2.2 ms, delay 1.8 ms,
    w_syn = 0.275 mV per synapse (free parameter), Poisson drive at 150 Hz with weight
    250 × w_syn, 30 trials of 1 s.
  - Silencing (`silence()`) sets **outgoing** synaptic weights of the silenced neurons to 0.
    The README says "to and from"; the code only zeroes rows where the neuron is presynaptic.
  - There is no spontaneous or background activity, so a neuron that never spikes has an
    in-silico silencing effect of exactly zero.
- **Initial PI analysis.** Wrote seed hypotheses H-A…H-E into STRATEGY.md §4 as inputs for scrutiny.
- **Office.** Roster and model/effort rationale are in OFFICE.md. Phase 1 launches five agents in parallel.

## 2026-11-03: Phase 1 launched; PI theory work

- **Launched in parallel (background):**
  - LIT-A (Sonnet/high)
  - LIT-B (Sonnet/high)
  - LIT-C (Sonnet/high)
  - NOV (Opus/high)
  - ENG (Sonnet/high)

  Each agent writes only to its own output file. The PI commits.
- **Parameter-derived scales** (computed in a scratch script; values from the `model.py` constants):
  - Unitary PSP peak: 0.043 mV per synapse, at t* = 9.24 ms.
  - About 162 synchronous synapses are needed to fire a neuron from rest.
  - Mean-drive threshold: D* = Θ/(τ_s·w_syn) ≈ 5,091 synapse·Hz.
  - A single edge is sufficient at r_pre = 150 Hz when it has more than about 34 synapses.
  - The Poisson jump of 68.75 mV is applied directly to v, so stimulated GRNs fire as Poisson at exactly λ.
- **Theory draft.** Wrote `docs/design/theory_note.md` (v0.1) with:
  - a ladder of predictors L0 to L5;
  - two asymptotic regimes, predicting a crossover from weighted-influence predictors near
    threshold to vertex-cut/dominator predictors at high drive (P1);
  - the flow-fraction law of EC50 shift, λ50′/λ50 = 1/(1 − f_k) (P2);
  - pairwise epistasis predictions by structural relation, including a closed form for synergy in EC50 space (P3).
- **Caveat.** These are mean-field approximations. The transfer function and D* must be
  calibrated empirically before any predictor is used (theory note §8).

## 2026-11-03: Phase 1 results (4 of 5) and synthesis

- **Reports in:** LIT-A, LIT-B, LIT-C and NOV are in `docs/research/`. ENG is still running.
- **Budget exhaustion.** WebSearch hit the shared limit and Consensus ran out of free credits
  (they reset 2026-12-01) during Phase 1. Absence-of-prior-art claims are therefore weaker than
  planned. This is logged as a limitation in PROJECT_DESIGN §1.2.
- **PI verification of decision-critical claims:**
  - **Jacobs et al. 2024, Cell Reports 43:114782.** Confirmed by the abstract (`[V-abs]`, via
    WebSearch): "connectome-based simulations ... predict that second-order sugar neurons act
    synergistically". The "all pairs" design is snippet-level only.
  - **Shiu `figures.ipynb`** (`[V-src]`, read by the PI):
    - sugar silencing screen at freqs = [50, 60, …, 120] Hz on the top 200 neurons, ranked by rate at 200 Hz;
    - water at 160–220 Hz;
    - JON at 140–180 Hz;
    - intact sugar curve at 10–200 Hz.
  - **Shiu & Sterne et al. 2022 eLife** (`[V-abs]`, peer-review text): only a subset of second-order
    neurons, and none of the third-order or premotor neurons tested, are required for sugar PER.
  - **Not verified:** whether Shiu 2024's text states that "redundancy increases with stimulation".
    Snippet-level only.
- **Decision (DECISIONS D-006).** Re-frame the project around the input-rescaling law (theory v0.2).
  Drop "operating-point dependence" and "neural epistasis" as novelty claims.
- **Drafts written:** `docs/design/PROJECT_DESIGN.md` v0.9 and `docs/design/PROPOSAL_1page.md` v0.9.
- **Public bucket found by ENG.** `gs://lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/`
  holds BANC, male CNS and FAFB-783 compiled data. This enables cross-connectome work in the paper
  extension.

## 2026-11-03: User inputs, push to main, Phase 3 and Phase 6 launched

- **Pushed to `main`** at the user's request: a fast-forward from e8fd470 to 005dc97, under the user's identity.
- **User answers:**
  - compute: here first, then Colab, then MacBook Pro M5;
  - finish by 2026-11-05;
  - keep a small pair pilot;
  - the user will upload full texts from the links provided (Shiu 2024, Jacobs 2024, Shiu 2022 and its
    source data, the Edmond archive listing, An 2026, Chen 2025, arXiv 2610.33881, Towlson 2020,
    male CNS 2026).
- **Launched:**
  - RED (Fable 5.1/high): adversarial review. Asked specifically about metabolic control analysis
    (Kacser–Burns flux control coefficients) as possible prior art for f_k.
  - SIM (Opus/high): batched numba simulator with common random numbers and exact network
    reduction, validation gates G1–G5 against Brian2. The model choice is deliberate: an incorrect
    simulator would invalidate every result.
- **ENG timing.** The per-trial discrepancy (about 5 s vs about 42 s) is consistent with the
  feasibility logs: first-touch memory allocation in this VM is slow (2–3 s per GB), and joblib loky
  workers rebuild and compile per process. A persistent process costs about 5 s per trial
  (stateupdate 1.9 s and threshold 0.6 s over 127k neurons). That makes network reduction the main
  speed-up.

## 2026-11-03: Full texts received; agents relaunched

- **Uploads.** The user uploaded 9 PDFs and 3 Fig. 1E CSVs from the Shiu archive. They are stored
  locally in `literature/pdfs/` and `data/shiu_archive/` (git-ignored: copyright and size), with
  text extracted into `literature/text/`.
- **Verified against full text** (`docs/research/fulltext_verification.md`):
  - Shiu 2024 explicitly states that redundancy increases with stimulation. **The qualitative H-B is
    pre-empted**, which confirms D-006.
  - W_syn is calibrated so that 100 Hz input gives about 80% of maximal MN9.
  - **Shiu & Sterne 2022 is a two-concentration silencing dataset.** At 50 mM, 6 of 7 second-order
    neurons reduce PER; at 100 mM, only Rattle and Usnea; third-order and premotor neurons have no
    effect at 50 mM. This is a new external test for the f-ranking. LIT-C missed it at abstract level.
  - Jacobs 2024: singles and pairs at 50/100/200 Hz, read out at stopping neurons, descriptive only.
  - Male-CNS Cell 2026 uses population-level max-flow.
  - Minnick 2026: output synapses predict single-type silencing effects (ρ = 0.78), joint silencing
    is supra-additive.
- **Agents stopped.** The user's interrupt stopped ENG, RED and SIM before they delivered. With the
  user's explicit approval, all three were relaunched:
  - ENG (Sonnet/high): Brian2 reference dataset, reproduction gate, MN9 ID mapping, report.
  - SIM (Opus/high): fast batched simulator plus gates G1–G5, using ENG's references.
  - RED (Fable/high): review, now including the full-text facts and an external-validation design for
    the two-concentration data.
- **CPU split:** ENG ≤ 2 processes, SIM ≤ 2 cores while ENG is running.

## 2026-11-03: SIM interim result; STRUCT launched

- **SIM interim** (agent message):
  - G0: the original Brian2 objects, with SIM's common-random-number (CRN) input trains injected,
    reproduce fastlif spike-for-spike in 9 of 9 cases (v630 and v783; 100/200/400 Hz; silencing
    included).
  - G3: the closure network (v630: 9,237 neurons, 995k synapses) is bit-identical to the full
    network in 116 jobs.
  - G4: CRN passes.
  - G5: 0.05 s per trial-condition at 2 threads, about 100× faster than Brian2.
  - G1 at 100 Hz: r = 0.9993. MN9_L 67.1 vs ENG 70.0 [68.1, 71.9] is a strict failure. The 60 pooled
    Brian2 trials give 68.2 [66.7, 69.6], which contains fastlif's 67.1. Diagnosed as sampling noise
    in the reference; accepted provisionally given G0.
  - Brian2 semantics confirmed: synaptic and Poisson input is dropped while a neuron is refractory and
    in its spike step.
- **Consequence.** Compute is no longer binding: the full single-neuron screen takes about 11–22 min.
  The design can afford more trials, a finer λ grid, all active neurons and more pairs, with the
  same plan and higher power.
- **STRUCT launched** (Opus/high): the structural-predictor pipeline (exact Sherman–Morrison and
  Woodbury walk-sum fractions, max-flow, dominators, empirical gains) and the intact λ-curve.
  Intact runs only.

## 2026-11-03: Red-team review, pre-registration freeze

- **RED verdict:** major revision. Key problems:
  - C1: P1 could not fail;
  - C4: notation clash between documents;
  - C5: likelihood mis-specified (MN9 is under-dispersed, Fano ≈ 0.65);
  - M3: abolition ⇏ cut;
  - M4: averaging the two MN9 outputs manufactures a law violation;
  - M7: n_eff ≈ 207 cell types, not ~400 neurons;
  - M13: MCA bridge needed.

  All were adopted (D-008).
- **Labels corrected by the PI.** Reading the Shiu 2022 figure images corrected a text-layer error:
  Phantom has no 50 mM phenotype; G2N-1 and FMIn are significant in one of two lines. The tiers were
  frozen in `fulltext_verification.md` §8 before any f was computed.
- **Pre-registration v1.0** committed as `e051e088` and pushed to the working branch and `main` (milestone).
- **ANALYSIS launched** (Opus/high): pre-registered fitting and statistics code, validated on
  synthetic data.
- **STRUCT updated by message:** primary T is the single contralateral MN9; S_pure input set;
  set-level structural f for the 10 external types; dominators and min-cut counts.

## 2026-11-03: Shiu archive Fig. 1F data received (partial)

- **Received:** `fig_1f_{50,60,70,80,90}_hz_rate.csv` and the matching `_std.csv` files, in
  `data/shiu_archive/` (git-ignored). The user's zip contained exactly these 10 files, byte-identical
  to the individual uploads. The 100, 110 and 120 Hz files were not included.
- **Content:** per-condition MN9 (`720575940660219265`) mean and SD over 30 trials, for 200
  single-neuron silencings, v630, Shiu's Brian2 runs.
- **Use (PROJECT_DESIGN §10, C3):** independent replication of RQ2 and RQ3 on the authors' own
  simulations. Not part of the confirmatory family.
- **Sanity checks seen while saving:**
  - silencing MN9 itself gives an unchanged MN9 rate at 90 Hz (63.5 Hz; f = 0 as required);
  - silencing 720575940607272649 (Roundup R, per `sez_neurons`) gives 45.5 Hz vs about 63 Hz for most
    other conditions.

  Treat these as observations only. No analysis has been run yet.
- **Transparency note.** When uploaded, the 80/90 Hz rate files and the 70–90 Hz std files were
  displayed in full to the PI. This happened **after** the pre-registration freeze (e051e088). No
  hypothesis, label, threshold or analysis choice was changed afterwards; any later deviation will be
  logged in DECISIONS.md.
- **Update.** A second zip added `fig_1f_{100,110,120}_hz_rate.csv` and `_std.csv`. The Fig. 1F
  archive set is now **complete**: 8 intensities (50–120 Hz) × 200 silencings, mean and SD over 30
  trials. These files were not displayed; they were extracted with a script only.
- **ENG done** (`feasibility_report.md`):
  - Reproduction gate: 1 strict sub-criterion missed on the primary seeds (Spearman 0.9956 vs a 0.9960
    floor); the independent replicate passes every criterion.
  - Accepted, with the ≤5% MN9 offset noted as a limitation.
  - MN9 onset is between 30 and 40 Hz.
  - Ipsilateral MN9 in v783 = 720575940618238523, as pre-registered (inferred by connectivity cosine).
  - Original Brian2 cannot run the screen in time (≈93 CPU-h), so SIM's fast simulator is required.
