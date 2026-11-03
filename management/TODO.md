# TODO

_Status: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked. Owner in brackets._

## Phase 0: Setup [PI]
- [x] Read the course syllabus. Final project = 1-page proposal (7%), presentation 2026-12-10 (10%), 3–5 page report (13%).
- [x] Probe the environment: 4 CPU / 15 GB / no GPU; only GitHub and PyPI reachable from the container.
- [x] Clone the Shiu et al. model repo (includes FlyWire v630 and v783 connectivity) to `/home/user/external/` (outside the repo).
- [x] Create management files (STRATEGY, OFFICE, TODO, LOG, DECISIONS).

## Phase 1: Parallel research
- [ ] [LIT-A] Connectome-model and in-silico perturbation literature, 2019–2026
- [ ] [LIT-B] Network-theory, lesion and redundancy literature
- [ ] [LIT-C] Experimental ground-truth table for candidate circuits
- [ ] [NOV] Prior-art and novelty verdicts for H-A…H-E
- [ ] [ENG] Feasibility: data inspection, baseline simulation, benchmark, resource availability

## Phase 2: Synthesis [PI]
- [ ] Literature assessment (established vs open)
- [ ] Novelty assessment per candidate
- [ ] 3–5 research questions with hypotheses, predicted outcomes, limitations
- [ ] Data and model feasibility summary
- [ ] Experimental design (circuit, perturbations, metrics, predictors, nulls, controls, statistics)
- [ ] Project-selection scoring matrix
- [ ] Execution roadmap (MVP to 2026-12-10; extension to a paper)

## Phase 3: Red team
- [ ] [RED] Adversarial review of the design draft
- [ ] [PI] Resolve or accept each issue in DECISIONS.md

## Phase 4: Verification
- [ ] [CIT] Audit every citation in the final docs
- [ ] [PI] Fix or flag every failed citation

## Phase 5: Finalize [PI]
- [ ] `docs/design/PROJECT_DESIGN.md` (master document)
- [ ] `docs/design/PROPOSAL_1page.md` (course proposal draft)
- [ ] Consistency pass, commit, push to `claude/ecstatic-ptolemy-9flxh6`
