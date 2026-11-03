# Full-Text Verification of Decision-Critical Claims (PI, 2026-11-03)

**Sources.** PDFs uploaded by the user, stored locally (not committed) in `literature/pdfs/`. The
text was extracted with `pdftotext -layout` into `literature/text/`. Line numbers refer to those text
files.

**Tag.** `[V-full]` means verified against the full text.

## 1. Shiu et al. 2024, *Nature* 634:210–219 (`Shiu2024_Nature.pdf`)

| Claim | Verdict | Quote / location |
|---|---|---|
| Single-neuron silencing of the top 200 sugar-responsive neurons at 50–120 Hz (10 Hz steps) | ✅ `[V-full]` | "we activated sugar-sensing neurons at frequencies ranging from 50 to 120 Hz in 10 Hz increments" (shiu2024.txt l.229–231) |
| Silencing criterion: MN9 ≤ 80% of control at any of the 8 frequencies | ✅ `[V-full]` | l.233–236 |
| **Redundancy increases with stimulation** | ✅ `[V-full]` **(pre-empts the qualitative H-B)** | "In general, silencing of individual neurons had the greatest effect when sugar GRNs were activated at low frequencies, implying greater redundancy in the circuit as sensory stimulation increases." (l.236–239) |
| 47 neurons sugar-responsive and sufficient; 14 of them also required | ✅ `[V-full]` | l.239–241 |
| W_syn calibration: 100 Hz sugar GRN drive gives about 80% of maximal MN9 | ✅ `[V-full]` | "We chose Wsyn such that activation of sugar GRNs at 100 Hz resulted in roughly 80% of maximal MN9 firing" (l.1038–1040) |
| Robustness checks: W_syn ± 30% (with compensating sensory input), inhibitory:excitatory ratio ± 50%, compared across 164 computational experiments with experimental data | ✅ `[V-full]` | l.1023–1060 |
| "91% accuracy over 164 predictions" | ⚠ Not found verbatim in the lines checked. The robustness text gives agreement (90.2%, 95%) and accuracies (85%, 88%) for the perturbed models. **Do not cite "91%"** | l.1030–1045 |
| Water: 4 of 5 neurons tested had no water-silencing phenotype as predicted; Usnea decreased PER with GtACR1 | ✅ `[V-full]` | l.678–681 |

## 2. Shiu, Sterne et al. 2022, *eLife* 11:e79887 (`Shiu2022_eLife.pdf`, figures PDF)

| Claim | Verdict | Quote / location |
|---|---|---|
| GtACR1 inhibition reduced PER to 50 mM sucrose (food-deprived flies) for 6 of 7 second-order neurons that elicit PER on activation; n = 46–83 flies per genotype | ✅ `[V-full]` | shiu2022.txt l.302–305, l.268–269 |
| **At 100 mM sucrose, inhibition of only Rattle and Usnea decreased PER**; the other second-order neurons had no effect (n = 30–144) | ✅ `[V-full]` **(two-concentration ground truth for dose-dependent necessity)** | l.305–307; figure supplement 2C legend (shiu2022_figs.txt l.310–312) |
| Acute GtACR1 inhibition of third-order or premotor neurons did not influence PER to 50 mM sucrose (n = 40–70), "consistent with multiple pathways to proboscis motor neurons" | ✅ `[V-full]` | l.338–339, l.431–432 |
| Premotor neurons provide about 13% of MN9's synaptic input; G2N-1, Zorro and FMIn connect directly to premotor neurons; the circuit is predicted cholinergic except Usnea and Phantom (GABAergic) | ✅ `[V-full]` | l.333–337 |
| Fig. 1A gives synapse counts from 17 candidate sugar GRNs onto each second-order neuron | ✅ `[V-full]` | l.264–265 |

**Consequence for the design.** This is a genuine **dose-dependent necessity** dataset, with
silencing at two sucrose concentrations, which LIT-C (abstract-level only) did not find. The
rescaling law predicts an ordinal pattern: neurons still necessary at the higher concentration
(Rattle, Usnea) carry the largest |f| among the 7 second-order neurons. Under a uniform random
ranking, the probability that the top 2 of 7 are exactly {Rattle, Usnea} is 1/21 ≈ 0.048.

**Caveat.** Usnea is predicted to be GABAergic, so a sign-based model may give Usnea f < 0
(silencing increases output). The test may therefore expose a model or sign failure. Pre-register
this outcome as informative either way.

## 3. Jacobs et al. 2024, *Cell Reports* 43:114782 (uploaded as `mmc3.pdf`, which contains the full article)

| Claim | Verdict | Quote / location |
|---|---|---|
| Used the Shiu model (default parameters) | ✅ `[V-full]` | mmc3.txt l.261–263, l.980–983 |
| Activated second-order neurons individually or in combination; "act synergistically" to activate third- and fourth-order **stopping** neurons (Fdg, Foxglove, Bluebell) | ✅ `[V-full]` | l.266–278 |
| Bilateral silencing of single second-order neurons left Fdg, Foxglove and Bluebell activity largely unaffected; simultaneous silencing of several had stronger effects | ✅ `[V-full]` | l.283–291 |
| **Design:** every single neuron and every pair; for 3 or more neurons, only excitatory neurons; intensities typically 50, 100 and 200 Hz; "results from the most informative intensity are shown" | ✅ `[V-full]` | l.989–992 |
| Readout | ✅ third- and fourth-order **stopping** neurons, **not MN9** | l.266–268 |
| Interaction score, null model, or structural predictor of interactions | ❌ none: descriptive only | — |
| Code available | ✅ `avdevineni/sugar-circuit` (GitHub, cited in the key resources table) | l.837 |

## 4. Other preprints

- **An 2026, bioRxiv 10.64898/2026.09.19.752860** (single author, Donggyu An).
  - Edge-pruning and compression operators on the Shiu model, with network-state dependence.
  - **No single-neuron silencing screen and no intensity-response analysis** in the text searched
    (an2026.txt).
- **Chen & Xi 2025, bioRxiv 10.64898/2025.12.14.694122** (Wei-Qiang Chen, Wenjie Xi).
  - Escape inputs (LC4, LPLC2 at 150 Hz) suppress MN9 via upstream disfacilitation (Roundup).
  - Silencing one inhibitor fails to restore feeding; silencing two gives partial recovery, termed
    "additive logic" or "additive gain" (chen2025.txt l.617–654).
  - Fixed intensity; no interaction theory.
- **Minnick et al. 2026, arXiv 2610.33881** (Minnick, Gonzalez-Ferrer, Geng, Eshraghian,
  Mostajo-Radji, Haussler, Teodorescu).
  - Shiu-type model on BANC, olfactory system.
  - The fall in Kenyon-cell active fraction from silencing one cholinergic type correlates with that
    type's output synapses (ρ = 0.78, P = 0.0045, 11 types).
  - "Types silenced together do more than the sum of their single falls" (l.258–262).
  - This is a structure→silencing-effect correlation (output synapses) and descriptive
    supra-additivity, with no intensity dependence.

## 5. Berg et al. 2026, *Cell* 189:5504–5526 (male CNS)

- ✅ `[V-full]` The paper uses an end-to-end **maximum-flow analysis** from sensory modality to motor
  domain (Dinic's method; input-normalized capacities; signs ignored; pseudo-source and pseudo-sink;
  flow-preference and specificity scores per interneuron).
- Methods: "Sensorimotor information flow analysis" (malecns_cell2026.txt l.2269–2300).
- **Consequence.** Max-flow on fly connectomes is published (structural, population-level). Our use
  is different: a per-neuron flow *fraction* that predicts silencing dose–response. Cite this paper
  as the source of the max-flow approach.

## 6. Towlson & Barabási 2020, *Network Neuroscience* 4(1):200 (`TowlsonBarabasi2020_NetwNeurosci.pdf`)

- ✅ The title "Synthetic ablations in the *C. elegans* nervous system" and the authors are confirmed
  from the PDF header.
- Framing: network-control-based prediction of neuron pairs and triplets whose joint ablation reduces
  controllability. Not read further.

## 7. Still needed

- Shiu archive **Fig. 1F** silencing CSVs (`fig_1f_*_hz_rate.csv`). Only the Fig. 1E activation CSVs
  (50 and 175 Hz) were provided.

## 8. Shiu & Sterne 2022 Figs. 1E and 2E (PI read of the figure IMAGES; corrects the earlier text-layer reading)

**Correction (2026-11-03).** An earlier version of this table, read from the PDF text layer, marked
Phantom as "reduced" at 50 mM. That was **wrong**: those asterisks belonged to the activation panel.
The table below was read from the rendered figure image (Figure 1, panels A and E; Figure 2, panels A
and E) `[V-full, image]`.

| Second-order neuron | GRN synapses (Fig. 1A) | GtACR1 at 50 mM, per split-GAL4 line (Fig. 1E) | Counted in "6 of 7"? | GtACR1 at 100 mM (Fig. 1—S2C legend) |
|---|---|---|---|---|
| Zorro | 325 | SS67405 *** ↓; SS67406 *** ↓ | yes | no effect |
| Clavicle | 210 | SS48947 *** ↓ | yes | no effect |
| G2N-1 | 165 | SS47082 * ↓; SS56399 ns | yes (one of two lines) | no effect |
| Rattle | 110 | SS50091 *** ↓ | yes | **↓** |
| Usnea | 75 | SS37122 *** ↓ | yes | **↓** |
| FMIn | 75 | SS48944 *** ↓; SS48949 ns | yes (one of two lines) | no effect |
| Phantom | 65 | SS44877 ns; SS44879 ns | **no**: the one of seven without a 50 mM phenotype | no effect |

**Third-order and premotor neurons** (Fig. 2A circuit schematic; Fig. 2E, GtACR1 at 50 mM, n = 40–70):
- Circuit: third-order = Sternum, Bract 1, Bract 2, Fdg; premotor = Roundup, Roundtree, Rounddown.
- Tested by inhibition: **Bract** (SS31320, SS31386), **Fdg** (SS31333, SS46913) and **Roundup**
  (SS47744, SS47745). **All had no effect** at 50 mM.

**Resulting ordinal labels** (frozen here, before any f is computed):

| Tier | Types | Meaning |
|---|---|---|
| 2 | Rattle, Usnea | necessary at 50 **and** 100 mM |
| 1 | Zorro, Clavicle, G2N-1, FMIn | necessary at 50 mM only (G2N-1 and FMIn in one of two lines) |
| 0 | Phantom | no phenotype at 50 or 100 mM |
| Layer comparison | Bract, Fdg, Roundup | third-order and premotor: no effect at 50 mM |

**Notes:**
- Usnea and Phantom are predicted GABAergic.
- Ranking by direct GRN synapse count puts Rattle 4th and Usnea 5th–6th of 7, so the 100 mM result
  is **not** explained by direct sensory input.
- **Sensitivity labelling (pre-registered):** G2N-1 and FMIn are moved to tier 0.5, because only one
  line was significant.
