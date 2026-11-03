# fly_or_fail

**From Structural Importance to Functional Necessity:** predicting task-specific vulnerability and
redundancy in the *Drosophila* connectome.

This is a graduate course project for BIOE689N/NACS728Z (*Network Neuroscience and Brain Dynamic
Analysis*, Fall 2026; presentation on 2026-12-10). It is meant to grow into a standalone research paper.

## Current phase

Research-question selection and experimental design. **No analysis code yet** (see
`management/DECISIONS.md`, D-003).

## Repository map

| Path | Contents |
|---|---|
| `management/STRATEGY.md` | Mission, constraints, stance, seed hypotheses, quality protocol, phases |
| `management/TODO.md` | Task list by phase |
| `management/LOG.md` | Append-only research log |
| `management/DECISIONS.md` | Decision record |
| `management/OFFICE.md` | Agent roster and model/effort rationale |
| `docs/research/` | Agent reports: literature, ground truth, novelty, feasibility, red team, citation audit |
| `docs/design/` | Synthesized design documents (theory note, project design, proposal) |
| `feasibility/` | Feasibility-probe scripts, ID lists, logs (not analysis code) |

## External data (not committed)

```bash
git clone --depth 1 https://github.com/philshiu/Drosophila_brain_model /home/user/external/Drosophila_brain_model
```

This repository contains the Shiu et al. (2024) Brian2 LIF model and the FlyWire connectivity data
(v630 and v783). We used commit `91bdd1e7`.
