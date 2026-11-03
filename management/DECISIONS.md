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
