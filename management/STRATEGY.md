# STRATEGY: From Structural Importance to Functional Necessity

_Living document. Owner: PI-coordinator (main session). Last updated: 2026-11-03 (Phase 0)._

## 1. Mission

Find the strongest research question about the link between connectome structure and the
consequences of perturbing neurons in a connectome-constrained *Drosophila* brain model,
and write a defensible experimental design for it **before any analysis code is written**.

- **Short term (course, BIOE689N/NACS728Z):** 1-page proposal, presentation on **2026-12-10**, and a
  3–5 page final report. That leaves about 5 weeks from 2026-11-03, with Thanksgiving (2026-11-26) off.
- **Long term (paper):** a standalone study with its own conceptual contribution and some form of
  independent validation.

## 2. Hard constraints

| Constraint | Consequence for design |
|---|---|
| Public data and models only, no new experiments | FlyWire v783 plus the Shiu et al. 2024 LIF model are the core. Validation has to come from published experiments or internal replication (left–right homologs, other connectomes). |
| About 5 weeks | The minimum viable project (MVP) must be one circuit, one model, and a bounded perturbation budget. |
| Hypothesis-driven, mathematically grounded | Prefer an analytic account (threshold, flow and linear-response theory) to pipeline complexity. |
| Compute: this container has 4 CPUs, 15 GB RAM and no GPU; the user's own machine is unknown | Simulation counts must be budgeted from measured runtimes (see the feasibility report). |
| Network: only GitHub and PyPI are reachable from the container; literature comes from server-side web search and the Consensus index | Paper full texts **cannot** be read here. Claims about paper *details* need an evidence tag (see §5). |

## 3. Scientific stance (non-negotiables)

1. **Model necessity is not biological necessity.** Every claim says which system it is about.
2. **Circularity check.** The LIF model is built from the same weight matrix W as the structural
   predictors, so "structure predicts model necessity" is partly true by construction. The real
   question is *which compressions of W are sufficient, and when the operating point and
   nonlinearity break them*. Only external data (published perturbation experiments, other
   connectomes) can break the circularity.
3. **Activity is not necessity.** A neuron with zero baseline activity has zero in-silico silencing
   effect by construction (the Shiu model has no spontaneous activity). Baseline activity must be
   a *baseline predictor* that structure has to beat. It cannot be a silent filter.
4. **No novelty inflation.** Every novelty claim names the closest prior art and the searches run.
5. **Pre-registration.** Hypotheses, metrics and tests are committed to git before the perturbation
   screens run. The commit hash serves as the timestamp.

## 4. Seed hypotheses (to be stress-tested, NOT conclusions)

These come from the initial PI analysis. They are inputs to the literature, novelty and red-team
agents, which may kill, merge or sharpen them.

- **H-A (model ladder):** Single-neuron necessity is predicted poorly by global centrality
  (degree, betweenness, PageRank). It is predicted better by task-specific source→target path and
  flow structure. It is predicted best by operating-point-aware linear response, i.e. structure plus
  baseline activity, (I − DW)⁻¹-type. The remaining gap measures nonlinear (threshold) effects.
- **H-B (threshold-margin theory of redundancy):** In a thresholded network, whether a neuron is
  necessary depends on how large its contribution is relative to the postsynaptic *margin above
  threshold*. Necessity and redundancy therefore depend on the operating point (stimulus
  intensity). A scalar "necessity" measured at one intensity is ill-posed. Silencing phenotypes
  should fall into *abolition* (series bottleneck) and *sensitivity shift* (parallel redundancy:
  the dose–response curve shifts but the maximum is kept).
- **H-C (neural epistasis, between- vs within-pathway):** Pairs of individually dispensable neurons
  on parallel routes that converge on common thresholded targets show synergistic (negative)
  epistasis. Pairs in series show masking (positive) epistasis. This is the neural analogue of
  between-/within-pathway genetic interaction models. Candidate structural predictor:
  inclusion–exclusion on source→target max-flow (Menger).
- **H-D (task specificity):** Across tasks that share an output (sugar → MN9 and water → MN9),
  necessity overlaps near the motor end and diverges near the input. Global hubs are rarely
  necessary for any one task.
- **H-E (external validity):** Model necessity predicts experimentally reported necessity better than
  centrality does, and is reproducible across left–right homologs (and later across connectomes).

## 5. Quality protocol ("zero tolerance")

| Item | Rule |
|---|---|
| Citations | Each reference is checked by the citation auditor against a search result retrieved in this session (title, first author, year, venue, DOI if shown). Anything unverifiable is flagged `[UNVERIFIED]` or removed. **No DOI is ever written from memory.** |
| Claims about paper content | Tagged `[V-abs]` (supported by an abstract or snippet retrieved this session), `[V-src]` (supported by primary source code or data we inspected), or `[MEM]` (background knowledge, not verified; must be confirmed before final use). |
| Numbers about data and compute | Every number in the feasibility report traces to a command log in `feasibility/logs/`. |
| Design soundness | An independent red-team review by the most capable model before the design is finalized. All issues are resolved or explicitly accepted in `DECISIONS.md`. |
| Final pass | The PI checks every deliverable against the agent reports for consistency. |

## 6. Phases and gates

| Phase | Output | Gate to pass |
|---|---|---|
| 0. Setup | management files, environment probe | done |
| 1. Parallel research | 3 literature reports, prior-art/novelty report, feasibility report | all 5 reports present and evidence-tagged |
| 2. Synthesis | candidate RQs, design draft, scoring matrix (`docs/design/`) | PI self-check |
| 3. Red team | `docs/research/redteam_review.md` | every critical issue resolved or accepted in DECISIONS.md |
| 4. Verification | `docs/research/citation_audit.md` | 0 unverified citations in final docs (or explicitly flagged) |
| 5. Finalize | `docs/design/PROJECT_DESIGN.md`, 1-page proposal draft, roadmap | consistency pass, commit and push |

## 7. Open strategic questions (update as answered)

- [ ] Has the pairwise / higher-order silencing work the user mentions already used the Shiu model? Who did it, and what did they find? (novelty agent)
- [ ] How large is the active set under sugar-GRN drive, and what does one simulated trial cost? (feasibility agent)
- [ ] Which published experiments give binary or graded necessity labels for named neurons in the PER (proboscis extension) and grooming circuits? (ground-truth agent)
- [ ] Is a faster equivalent simulator needed for pairwise screens? (feasibility, then a decision)
