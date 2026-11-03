# DECISIONS (Architecture Decision Record)

_Each entry gives: context, decision, alternatives considered, consequences, status._

## D-001: Keep large third-party data outside the git repo
- **Context.** The FlyWire connectivity files are about 100 MB each and ship inside the Shiu model repo.
- **Decision.** Clone to `/home/user/external/Drosophila_brain_model` and never commit the data.
  The README documents how to re-create it.
- **Status.** Accepted (2026-11-03).

## D-002: Literature evidence standard under network restrictions
- **Context.** Publisher, preprint and DOI hosts are blocked. Only server-side web search and the
  Consensus abstract index work.
- **Decision.** Every claim about a paper carries an evidence tag (`[V-abs]` / `[V-src]` / `[MEM]`).
  `[MEM]` claims cannot support a key design decision unless upgraded or explicitly flagged.
- **Alternatives.** Ask the user to widen network access. That is offered, but the work does not wait on it.
- **Status.** Accepted (2026-11-03).

## D-003: No analysis code before the design is fixed
- **Context.** The user asked for the research question and design to be settled before code is written.
- **Decision.** Phase 1 engineering is limited to *feasibility probes*: install, inspect data, run
  the baseline simulation and benchmarks. No perturbation screens or predictor pipelines.
- **Status.** Accepted (2026-11-03).

## D-004: Commit identity and attribution
- **Context.** The user requires that every commit be made under the user's own identity, with no
  third-party credit or attribution lines.
- **Decision.** The repo-local git config uses `Meysam Amirsardari
  <62254770+MeysamAmirsardari@users.noreply.github.com>`. Commit messages carry no
  `Co-Authored-By` or session trailers. Earlier commits were rewritten and force-pushed with the
  user's explicit approval (2026-11-03).
- **Status.** Accepted (2026-11-03).

## D-005: Push cadence
- **Context.** The user asked for less frequent pushes (2026-11-03).
- **Decision.** Commit locally as needed. Push to the remote only at milestones: after design synthesis, after the red-team review, and at the final deliverable.
- **Status.** Accepted (2026-11-03).

## D-006: Re-frame the core hypothesis as the input-rescaling law
- **Context.** The prior-art audit shows two things. Intensity-swept single silencing is already in
  the Shiu et al. 2024 design. Synergy among second-order sugar neurons is reported by Jacobs et al.
  2024. "Synthetic essential" neuron pairs are framed by Towlson & Barabási 2020 (C. elegans).
- **Decision.** The core claim becomes the quantitative law O_k(λ) = O((1 − f_k)λ) and its
  consequences: curve collapse, the EC50-shift law, abolition = vertex cut, and parameter-free pair
  interaction curves with a synergy window. The structural estimation of f_k is the "structure" half.
  The centrality-vs-necessity comparison is kept as a baseline section (RQ1).
- **Alternatives considered.**
  - C1, centrality screen only: too incremental.
  - C6, Shapley/MSA: costly, and less directly tied to the student's question.
  - C5, cross-connectome: data-heavy for 5 weeks; kept for the paper.
- **Status.** Proposed, pending red-team review (2026-11-03).

## D-007: Whole project due 2026-11-05; scope unchanged
- **Context.** The user clarified that the WHOLE project (not only the design) must be finished by
  2026-11-05, and said: "Don't change the plan or feasibility! We'll work harder!"
- **Decision.** Keep the full MVP scope: RQ1–RQ3, the RQ4 pilot, and the RQ5 robustness slices. Compress
  the timeline:
  - Nov 3: red team, design freeze, validated simulator.
  - Nov 3–4: calibration, predictors, screens (fast simulator, parallel batches).
  - Nov 4–5: analysis, figures, report and slides.

  The critical path is simulator validation followed by the screens. Scope cuts happen only if the
  user agrees.
- **Status.** Accepted (2026-11-03).

## D-008: Red-team resolutions and the v1.0 pre-registration freeze
- **Context.** RED (Fable 5.1) returned "major revision before freeze": 5 Critical, 13 Major and
  8 Minor issues (`docs/research/redteam_review.md`).
- **Decision.** All issues are accepted and resolved in `PROJECT_DESIGN.md` v1.0 §10 and theory v0.3 §0.
  - C2 (infeasible compute) is resolved by evidence, not by descoping: the validated fastlif
    simulator is about 100× faster than Brian2 and spike-exact against Brian2 objects (G0). RED's
    descoping ladder is retained as §9, in case the gates fail.
  - One primary confirmatory test (P-A), a Holm family S1–S5, everything else exploratory.
  - External labels were frozen from the figure **images** (`fulltext_verification.md` §8). This
    corrected an earlier text-layer error: Phantom = no 50 mM phenotype.
  - The bridge framing (MCA flux control coefficients and receptor reserve) replaces novelty claims.
- **Not adopted as written.**
  - RED's minimum design (Tier A 80–120 neurons, 12 trials). Compute is not binding, so the full
    candidate set with 30 trials is pre-registered. This improves on RED's power estimates.
- **Status.** Accepted (2026-11-03). The commit introducing v1.0 is the pre-registration timestamp.

## D-009: Pre-screen analysis amendments (synthetic validation only; no outcome data seen)
1. **Informativeness gate (§6.2)** is evaluated under the CV-selected model, not only under M_shift.
   Reason: under shift-only, strong gain-loss curves were misclassed as uninformative in 72–100% of
   synthetic cases.
2. **Effect gate (§6.1)** applies a Holm correction across the λ levels within each neuron. Reason:
   15–24% false positives on synthetic neurons with f = 0 and noisy counts.
3. **P-A one-sided decision** uses the 5th percentile of Δρ; the 2.5th percentile is also reported.
   **Variance floor:** 1 count².
4. **GOF (§6.3)** is kept as written. On synthetic data it is conservative (size 0.014–0.036 at a
   nominal 0.05), so collapse could pass more often than it should; this is disclosed as a limitation.
5. **ANALYSIS's other readings of v1.0 are accepted as written:**
   - Ô is clamped at the grid ends and flagged;
   - O_max is taken from the monotone curve;
   - CV removes the held-out seeds from the intact curve as well;
   - Williams/Steiger uses n = number of cell types;
   - S3 is dropped from Holm if there are fewer than 5 dominators.
- **Status.** Accepted (2026-11-03), before any screen was run.
- **D-009 addendum (2026-11-03, before any screen result was viewed).** Accepted ANALYSIS's
  implementation:
  - the informativeness thresholds are relative to the selected model's own maximum: O_max for shift;
    γ·O_max for gain; the fitted Hill at 400 Hz for free;
  - the effect gate applies Holm across the λ levels with intact rate ≥ 5 Hz.

  Synthetic results:
  - gain (γ = 0.5) classified correctly 0.99–1.00 of the time;
  - false positives at f = 0 fall to 3.5–7%.

  Disclosed limitation: for the free model, the 0.9 criterion is met automatically when the grid ends
  at 400 Hz.
