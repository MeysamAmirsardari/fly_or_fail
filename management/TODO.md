# TODO

_Status: `[ ]` open · `[~]` in progress · `[x]` done · `[!]` blocked. Owner in brackets._

## Phase 0: Setup [PI]
- [x] Read the course syllabus. Final project = 1-page proposal (7%), presentation 2026-12-10 (10%), 3–5 page report (13%).
- [x] Probe the environment: 4 CPU / 15 GB / no GPU; only GitHub and PyPI reachable from the container.
- [x] Clone the Shiu et al. model repo (includes FlyWire v630 and v783 connectivity) to `/home/user/external/` (outside the repo).
- [x] Create management files (STRATEGY, OFFICE, TODO, LOG, DECISIONS).

## Phase 1: Parallel research
- [x] [LIT-A] Connectome-model and in-silico perturbation literature, 2019–2026
- [x] [LIT-B] Network-theory, lesion and redundancy literature
- [x] [LIT-C] Experimental ground-truth table for candidate circuits
- [x] [NOV] Prior-art and novelty verdicts for H-A…H-E
- [~] [ENG] Feasibility: data inspection, baseline simulation, benchmark, resource availability

## Phase 2: Synthesis [PI]
- [x] Literature assessment (established vs open), PROJECT_DESIGN §1
- [x] Novelty assessment per candidate, §2
- [x] 5 research questions with hypotheses, predicted outcomes, limitations, §3
- [~] Data and model feasibility summary, §4 (waiting for ENG final numbers)
- [x] Experimental design, §5
- [x] Project-selection scoring matrix, §6
- [x] Execution roadmap, §7 (re-plan for the user's 2026-11-05 deadline)

## Phase 3: Red team
- [~] [RED] Adversarial review of the design draft (Fable 5.1/high, running)
- [ ] [PI] Resolve or accept each issue in DECISIONS.md

## Phase 4: Verification
- [ ] [CIT] Audit every citation in the final docs
- [ ] [PI] Fix or flag every failed citation

## Phase 5: Finalize [PI]
- [ ] `docs/design/PROJECT_DESIGN.md` (master document)
- [ ] `docs/design/PROPOSAL_1page.md` (course proposal draft)
- [ ] Consistency pass, commit, push to `claude/ecstatic-ptolemy-9flxh6`

## Phase 6: Simulation infrastructure (added 2026-11-03; user wants compute here)
- [~] [SIM] Numba batched simulator with common random numbers, exact closure reduction, gates G1–G5 vs Brian2 (Opus/high, running)
- [ ] [PI] Review sim_validation.md and accept or reject the simulator

## Phase 7: Pre-registered runs (after the design freeze)
- [ ] Freeze the pre-registration (git commit of the final design and analysis plan)
- [ ] Calibration: transfer function φ, D*, dense intact curve O(λ)
- [ ] Structural predictors L0–L2 and all f estimators, frozen before viewing screen results
- [ ] Single-neuron screen; pair pilot (~60 pairs); robustness subset
- [ ] Primary analyses P1–P5; figures

## User inputs (2026-11-03)
- Compute: here first, then Colab, then MacBook Pro M5
- Deadline: the WHOLE project by 2026-11-05 (user clarification); scope unchanged (D-007)
- Pairs: keep a small pilot
- Full texts: links sent; the user will upload PDFs
