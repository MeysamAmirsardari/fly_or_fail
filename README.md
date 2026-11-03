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

Clone next to the repo, in `../external/` (or point `NJ_EXTERNAL` at another folder):

```bash
git clone https://github.com/philshiu/Drosophila_brain_model ../external/Drosophila_brain_model && git -C ../external/Drosophila_brain_model checkout 91bdd1e7
git clone --depth 1 https://github.com/flyconnectome/flywire_annotations ../external/flywire_annotations
```

The first repository contains the Shiu et al. (2024) Brian2 LIF model and the FlyWire connectivity
data (v630 and v783). We used commit `91bdd1e7`.

## Environment

Python 3.14 (Brian2 2.11 needs ≥ 3.12):

```bash
python3.14 -m venv venv && venv/bin/pip install brian2 numba pyarrow pandas scipy networkx python-igraph scikit-learn statsmodels pytest
```

Tested 2026-11-03 on an Apple-silicon Mac: numpy 2.5.4, numba 0.68.1, Brian2 2.11.0, scipy 1.18.1,
pandas 3.1.0. A rerun of the v783 S_shiu intact curve (4 λ × 10 seeds) reproduced the committed
spike counts exactly. The scripts under `feasibility/` are historical probes and still hard-code
`/home/user/...` paths.
