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
