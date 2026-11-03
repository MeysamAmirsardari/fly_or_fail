# OFFICE: Agent Roster and Model/Effort Rationale

_The user asked for "an office of subagents" with models and effort chosen to balance quality and
usage, and zero tolerance for mistakes._

## Model pricing basis (API list prices as of 2026-10-06; input/output per 1M tokens)

| Model | Price | Use here |
|---|---|---|
| Fable 5.1 (most capable) | $10 / $50 | Only the highest-stakes judgement: adversarial review of the final design |
| Opus 5.5 | $4 / $20 | PI-coordinator (main session) and the novelty/prior-art hunt, where a miss would be costly |
| Sonnet 5.5 | $2 / $10 | Broad literature sweeps, data/model engineering, citation auditing |
| Haiku 5.5 | $0.10 / $0.50 | Not used: every task here needs judgement, and zero tolerance rules out the cheapest tier |

## Roster

| ID | Role | Model | Effort | Phase | Output |
|---|---|---|---|---|---|
| PI | Coordinator: strategy, synthesis, design, final consistency pass | Opus 5.5 (main session) | n/a | all | `docs/design/*`, `management/*` |
| LIT-A | Literature: connectome-constrained models and *Drosophila* in-silico perturbation, 2019–2026 | Sonnet 5.5 | high | 1 | `docs/research/lit_A_connectome_models.md` |
| LIT-B | Literature: network theory of lesions, structural predictors, causal attribution (MSA/Shapley), redundancy/degeneracy, genetic-interaction analogies | Sonnet 5.5 | high | 1 | `docs/research/lit_B_network_theory.md` |
| LIT-C | Experimental ground truth: neurons with published necessity/sufficiency data in candidate circuits (PER, grooming, …) | Sonnet 5.5 | high | 1 | `docs/research/lit_C_ground_truth.md` |
| NOV | Prior-art and novelty hunter for each seed hypothesis H-A…H-E | Opus 5.5 | high | 1 | `docs/research/novelty_prior_art.md` |
| ENG | Data and model feasibility: install, inspect FlyWire v783, run the Shiu baseline, benchmark, check other datasets | Sonnet 5.5 | high | 1 | `docs/research/feasibility_report.md`, `feasibility/` |
| RED | Red team: novelty, circularity, confounds, statistics, feasibility | Fable 5.1 | high | 3 | `docs/research/redteam_review.md` |
| CIT | Citation auditor: verify every reference in the final docs | Sonnet 5.5 | medium | 4 | `docs/research/citation_audit.md` |
| STRUCT | Analysis engineer: structural predictors (L0–L2), walk-sum/Sherman–Morrison transmission fractions, max-flow, dominators, intact λ-curve | Opus 5.5 | high | 7 | `analysis/`, `analysis/PREDICTORS.md` |
| SIM | Simulation engineer: batched numba replica of the Shiu LIF model with common random numbers, exact network reduction, validation against Brian2 | Opus 5.5 | high | 6 | `sim/`, `docs/research/sim_validation.md` |

### Why these choices

- **Literature sweeps on Sonnet/high.** The work is many searches plus careful extraction. Sonnet
  5.5 handles this well at half Opus's price. High effort keeps it from stopping early.
- **Novelty hunt on Opus/high.** Calling something "novel" when prior art exists is the costliest
  mistake for the paper goal, and judging closeness of prior art is subtle.
- **Engineering on Sonnet/high.** The work is multi-step tool use with checks. Correctness comes from
  logged evidence, not raw reasoning depth.
- **Red team on Fable 5.1/high.** One focused, high-value adversarial pass where the strongest
  reasoning pays for itself.
- **Simulator on Opus/high.** Every result depends on this code. A subtle semantic error (update order, refractoriness, reset) would silently invalidate the whole study, which justifies the stronger model. Validation gates against Brian2 are mandatory.
- **Citation audit on Sonnet/medium.** Matching metadata is a narrow task. Medium effort is enough
  when the rules are explicit, and Haiku is excluded under zero tolerance.

## Rules of engagement for all agents

1. Write only to your assigned output file(s). Never commit or push; the PI does that.
2. Tag the evidence for every claim (`[V-abs]`, `[V-src]`, `[MEM]`). Never invent a DOI, author, year or result.
3. Keep a query/command log in your output so every search or run can be repeated.
4. Report blocked resources plainly. Do not mock or invent results to fill gaps.
