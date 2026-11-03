# HANDOFF (2026-11-03): How to Resume in a New Session

## State
- **Design:** pre-registered and FROZEN in `docs/design/PROJECT_DESIGN.md` v1.0 (commit e051e08).
  - Theory: `docs/design/theory_note.md` v0.3.
  - Red-team resolutions: DECISIONS D-008. Pre-screen amendments: DECISIONS D-009.
- **External labels:** frozen in `docs/research/fulltext_verification.md` §8.
- **Done and accepted:**
  - literature reports (`docs/research/`);
  - feasibility (`feasibility_report.md`);
  - fast simulator `sim/fastlif.py`: all gates pass, `docs/research/sim_validation.md`;
  - analysis code `analysis/curves.py` and `analysis/stats.py` (52 synthetic tests pass;
    `analysis/IO_CONTRACT.md`).
- **In progress when the session ended:**
  - STRUCT (`analysis/predictors.py`; outputs in `analysis/out/`, not committed: re-run them);
  - ANALYSIS implementing D-009 items 1–2 (informativeness gate under the CV-selected model; Holm
    correction across λ in the effect gate). Check `analysis/curves.py` for these and finish if
    missing.
- **No silencing screen has been run yet.**

## Next steps, in order
1. Environment: `python -m venv venv && pip install brian2 numba pyarrow pandas scipy networkx`.
   Data: `git clone --depth 1 https://github.com/philshiu/Drosophila_brain_model ../external/Drosophila_brain_model`.
   Annotations: `git clone --depth 1 https://github.com/flyconnectome/flywire_annotations ../external/flywire_annotations`.
   Paths in scripts assume `/home/user/external/...`; edit them for your machine.
2. Run STRUCT: structural predictors, plus the intact curve (λ = 0:5:400, 60 seeds) for S_shiu and
   S_pure. Freeze the silencing λ grid via `curves.grid_from_intact` and commit before any screen.
3. Screens with fastlif, per PROJECT_DESIGN §5–6 and IO_CONTRACT. Keep each call ≤ 1,000 jobs.
   - all candidates, singly;
   - the external types (whole-type silencing, S_pure input);
   - 60 pairs;
   - recruitment control;
   - replications.
4. Analysis: P-A, then S1–S5 (Holm), then the exploratory items (§7). Replicate with
   `data/shiu_archive/fig_1f_*` (the authors' runs).
5. Citation audit; report (3–5 pages); slides (Dec 10); final proposal (`docs/design/PROPOSAL_1page.md`
   needs the red-team edits from `redteam_review.md` §8).

## Notes
- Primary readout: MN9 720575940660219265 only. The ipsilateral MN9 is 720575940618238523 (v783).
  **Never average the two.**
- PDFs: re-download via `docs/research/READING_LIST.md`. They are not committed.
- Commits must use the user's identity only, with no attribution trailers (D-004).
