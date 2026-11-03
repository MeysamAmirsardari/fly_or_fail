# I/O Contract: simulator → analysis

**Owner:** ANALYSIS. **Consumers:** `analysis/curves.py` (`validate_screen`, `analyze_screen`,
`grid_from_intact`) and `analysis/stats.py`.
**Producer:** SIM (`sim/fastlif.py` runner).
**Governs:** PROJECT_DESIGN.md v1.0 (commit e051e08), §5.1, §5.3, §6, §7.

`curves.validate_screen(counts, conditions)` enforces this contract. It raises an error that lists
every violation. Run it on every file before handing the file over.

---

## 1. Files

Each screen is **two parquet files** that share a stem:

```
sim/out/screens/<screen>.counts.parquet       one row per (condition, lambda, seed)
sim/out/screens/<screen>.conditions.parquet   one row per condition
```

Suggested `<screen>` names: `intact_v783_S_shiu`, `intact_v783_S_pure`, `single_v783_S_shiu`,
`type_v783_S_pure`, `pairs_v783_S_shiu`, `subsets_v783_S_shiu`, `controls_v783_S_shiu`.
Replications use the same pattern with their own stem, for example `single_v630_S_shiu`,
`single_v783_S_shiu_left` or `top50_v783_S_shiu_wsyn0.8`.

## 2. Counts table (`*.counts.parquet`)

| column | type | rule |
|---|---|---|
| `condition_id` | string | must exist in the conditions table |
| `input_set` | string | `S_shiu`, `S_pure`, `S_shiu_left`, … (the same string as in the conditions table) |
| `lambda_hz` | float64 | the exact frozen value (§4); no recomputation or re-rounding |
| `seed` | int64 | fastlif trial seed (CRN key) |
| `mn9_primary_count` | int64 ≥ 0 | spike count of the **primary T**, the contralateral MN9, over the whole trial |
| `mn9_secondary_count` | int64 ≥ 0 | spike count of the **secondary**, ipsilateral MN9, over the whole trial |

- **Readout IDs.** These are fixed in one place and asserted by SIM.
  - Primary T: v783 `720575940660219265` (CB0701, side "right").
  - Secondary: v783 `720575940618238523` (CB0701, side "left").
  - v630 secondary: `720575940645521262`, per ENG.
- **The two MN9s are never averaged.**
- **Completeness.** Each (condition_id, input_set) holds a complete λ × seed factorial. No duplicate
  (condition_id, input_set, lambda_hz, seed) rows are allowed.
- **Rates.** Analysis converts counts to rates as rate (Hz) = count / `duration_s`.

## 3. Conditions table (`*.conditions.parquet`)

| column | type | rule |
|---|---|---|
| `condition_id` | string, unique | stable ID, for example `intact`, `k_<flywire id>`, `type_Rattle`, `pair_<a>_<b>`, `sub_03`, `ctl_all_S` |
| `kind` | string | one of `intact`, `single`, `type`, `pair`, `subset`, `control` |
| `silenced_ids` | list<int64> | FlyWire IDs whose outputs are zeroed. Empty for `intact`. For `type`, **all members of the type together** (§7.2). For `pair`, `[a, b]` |
| `input_set` | string | as in counts |
| `lambda_hz` | list<float64> | the λ levels run for this condition (must equal the set present in counts) |
| `duration_s` | float64 | trial length in seconds (fastlif T = 10000 × 0.1 ms → `1.0`); the same in every row of a file |
| `flywire_version` | string | `v783` or `v630` |
| `label` | string | a human-readable name: cell-type name for `type` (exactly `Rattle`, `Usnea`, `Zorro`, `Clavicle`, `G2N-1`, `FMIn`, `Phantom`, `Bract`, `Fdg`, `Roundup`); `a|b` for pairs; control name (`all_S`, `T`, `grn:<id>`, `no_path:<id>`) |

**Optional columns.** If they are absent, the defaults apply.

| column | type | meaning |
|---|---|---|
| `stim_ids` | list<int64> or null | the stimulated subset (recruitment control, §6.6). null means the whole `input_set` |
| `stratum` | string | pairs only: `parallel`, `serial` or `nonconv` |
| `w_syn_scale` | float64 | 1.0 by default; 0.8 or 1.2 for the W_syn replication |
| `inout` | bool | false by default (the sensitivity mode in fastlif that also drops inputs) |

Recommended parquet schema metadata keys: `sim_git_hash`, `crn_salt`, `T_steps`, `created_utc`.

## 4. Required content of each screen

1. **Intact curve** (one file per input set and version):
   - exactly one condition with `kind = intact` and `silenced_ids = []`;
   - λ = 0, 5, …, 400 Hz (81 levels, values `5.0*i`);
   - seeds 0–59.

   Seeds 0–29 are the training seeds (Ô); seeds 30–59 are the independent seeds (Ô_ind, used for
   the absolute GOF).
2. **Silencing grid.** It is frozen once per input set **before** any silencing run:
   - computed with `curves.grid_from_intact(counts, conditions, input_set)`;
   - λ50 of Ô is estimated on seeds 0–29;
   - the grid has 10 levels, log-spaced from 0.5·λ50 to min(8·λ50, 400), rounded to 0.01 Hz.

   The PI commits the result to `analysis/out/lambda_grid_<ver>_<input_set>.json` with these keys:
   `input_set`, `readout`, `lam50`, `O_max`, `lambda_hz`, `non_physiological`. Every silencing screen
   uses exactly these `lambda_hz` values.
3. **Every silencing screen file** contains its own paired baseline:
   - one `kind = intact` condition per input set, on the frozen grid, seeds 0–29;
   - every silencing condition on the same grid and the same seeds 0–29.

   With CRN this baseline is bit-identical to the intact runs at those λ. It is still required in
   the file, because the effect gate (§6.1) uses per-seed paired differences.
4. **CRN.** One `crn_salt` is used across every file of a version and input set. Seed *s* in any file
   must be the same fastlif trial seed *s*.
5. **Pairs.** Both single conditions `k_<a>` and `k_<b>` must exist on the same grid and seeds. They
   may live in the single-screen file, which is joined on `condition_id`.
6. **Silent-everywhere neurons** (§5.4) are **not** simulated. STRUCT or SIM lists them separately
   with f = 0.

## 5. Intact curve arrays as seen by the analysis

`curves.IntactData(lam[81], rates[60, 81], seeds[60], duration_s)` is built from the intact-curve file
for one `input_set` and one readout. It exposes:
- `.train`: Ô, using seeds 0–29;
- `.indep`: Ô_ind, using seeds 30–59;
- `.train.O_max` and `.train.lam50`.

A silencing condition is passed to the analysis as two arrays, each of shape (30 seeds, 10 λ):
`Y_sil` and `Y_intact_paired`. The analysis builds them with `curves.condition_matrix`.

## 6. Minimal example (pandas)

```python
counts = pd.DataFrame({'condition_id': ['intact', 'k_720575940600000001'] * 2,
                       'input_set': 'S_shiu', 'lambda_hz': [31.42, 31.42, 41.68, 41.68],
                       'seed': [0, 0, 0, 0], 'mn9_primary_count': [9, 7, 15, 12],
                       'mn9_secondary_count': [8, 7, 14, 11]})
conds = pd.DataFrame([dict(condition_id='intact', kind='intact', silenced_ids=[], input_set='S_shiu',
                           lambda_hz=[31.42, 41.68], duration_s=1.0, flywire_version='v783', label='intact'),
                      dict(condition_id='k_720575940600000001', kind='single',
                           silenced_ids=[720575940600000001], input_set='S_shiu',
                           lambda_hz=[31.42, 41.68], duration_s=1.0, flywire_version='v783',
                           label='CB1234')])
counts.to_parquet('x.counts.parquet'); conds.to_parquet('x.conditions.parquet')
curves.validate_screen(pd.read_parquet('x.counts.parquet'), pd.read_parquet('x.conditions.parquet'))
```

The round trip, from synthetic parquet through `validate_screen` and `analyze_screen` to f̂ recovery,
is tested in `analysis/tests/test_curves.py::test_io_contract_roundtrip`.
