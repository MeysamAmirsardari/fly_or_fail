# LIT-A: Connectome-constrained models and in-silico perturbation in Drosophila (2019 to Nov 2026)

_Agent LIT-A. Written 2026-11-03. Scope: see §0. This is a literature and source-code audit, not a design._

## Contents

0. Scope, evidence tags and search coverage limits
1. Annotated bibliography by theme
2. Shiu et al. 2024 capability sheet (model, analyses, validation, gotchas)
3. Established vs open: synthesis against H-A to H-E
4. Unconfirmed leads
5. Query log

---

## 0. Scope, evidence tags and search coverage limits

### 0.1 Evidence tags (as required by the PI)

| Tag | Meaning in this file |
|---|---|
| **[V-abs]** | Supported by a Consensus abstract (real abstract text) or by a WebSearch result retrieved in this session. The URL I saw is given. Where the support is only a WebSearch-generated paraphrase of a record page (not abstract text), I add **(ws)**. Treat (ws) items as one notch weaker than abstract text. |
| **[V-src]** | Supported by primary code or data I inspected: the Shiu repo at `/home/user/external/Drosophila_brain_model` (read only, nothing run), or third-party GitHub repos cloned into the scratchpad (untrusted, nothing executed). For third-party repos, [V-src] means "the README or code says this". It does not mean I reproduced the result. |
| **[MEM]** | Background knowledge not confirmed this session. I have tried to keep these to a minimum. |

DOIs are quoted only where they appeared in search-result text or URLs in this session. They come from search-tool output, not from the journal page, so the citation auditor should still re-check them.

### 0.2 What was searched

Consensus (abstract index) and WebSearch (server-side) only, plus local reading of the Shiu repo and shallow clones of four public GitHub repos. Full texts of papers could not be read. Every statement about the content of the Shiu et al. 2024 Nature paper that is not [V-src] therefore rests on abstracts or search paraphrases.

### 0.3 Coverage limits that matter (read before relying on §3)

1. **Consensus free quota was exhausted** partway through ("100% of free usage this month; resets December 1"). Three of my planned connectome-resource queries (Matsliah, Schlegel, Eckstein via Consensus) failed. I recovered those through WebSearch (ws-level evidence only).
2. **The shared WebSearch budget was exhausted** near the end. Three queries were refused (logged in §5): (a) combinatorial or double silencing of neurons in real flies, (b) BANC coverage of the SEZ, gustatory and proboscis motor neurons, (c) sensitivity of connectome-LIF output to proofreading errors and synaptic-weight noise. These three topics are **under-searched**. Statements of absence ("no study found") on them are weak.
3. WebSearch results are model-synthesised summaries and occasionally contradict themselves (for example a conflicting first author for Schlegel et al., conflicting neuron counts for the male CNS). I flag conflicts where seen.
4. I did not search for experimentally measured necessity labels for named neurons (the ground-truth agent's job) beyond what the Shiu abstracts say.
5. The sub-areas "Studies using the Shiu model for other behaviours" and "GPU re-implementations" are well covered, mostly by grey literature (GitHub), which is explicitly **not peer reviewed**.

---

## 1. Annotated bibliography

Hypotheses: H-A model ladder; H-B threshold-margin redundancy theory; H-C neural epistasis (pairs); H-D task specificity; H-E external validity (experiments, left–right homologs, other connectomes).

### 1.1 Connectome resources

**Coverage table** (SEZ and feeding relevance; evidence in the entries below)

| Resource | Tissue / sex | Includes SEZ and gustatory input? | Includes proboscis motor neurons (e.g. MN9)? | Notes |
|---|---|---|---|---|
| FlyWire FAFB (Dorkenwald 2024) | Adult female whole brain (central brain plus optic lobes) | Yes: whole brain; SEZ annotation is a stated strength (ws) | Yes in the model files: left MN9 ID is present in both v630 and v783 completeness tables [V-src] | The Shiu model's substrate. Nerves are cut at the brain boundary [MEM]. |
| Hemibrain (Scheffer 2020) | Adult female central-brain subvolume | **Poorly.** SEZ and optic-lobe annotations "largely absent from the hemibrain" (ws). I found no source explicitly saying "excludes the SEZ", so the evidence is indirect. | Not expected | Not a candidate for the feeding circuit. |
| MANC (Takemura 2024 and companions) | Adult male ventral nerve cord only | No (no brain) | Not applicable (VNC) | Useful for leg and neck circuits and for cross-matching to FlyWire. About 50% reconstruction completion noted by reviewers (ws). |
| FANC (Phelps 2021) | Adult female VNC | No | n/a | Not retrieved in this session. See §4. |
| BANC (Bates et al.) | Adult female brain plus nerve cord | Brain included, so SEZ present in principle. Specific SEZ and gustatory coverage **not checked** (search refused). | Not checked | Nature 2026 (ws). |
| Male CNS (Janelia/Google, v1.0) | Adult male brain, optic lobes and VNC | Brain included. Third-party code runs sugar-GRN input on it and reports MN9-like readouts [V-src, README claims]. Official annotation coverage of the SEZ **not verified**. | Third-party READMEs treat MN9 and pump motor neurons as present [V-src, README claims] | Released 2026-09-03 per a news item (ws). Counts differ across sources. |

**Dorkenwald et al. 2024, "Neuronal wiring diagram of an adult brain", Nature.** First author S. Dorkenwald, 2024. https://consensus.app/papers/details/5c6cf12d304952868f132cf61116c458/?utm_source=claude_desktop (peer reviewed)
- [V-abs] Whole-brain wiring diagram of an adult female fly: 139,255 neurons, about 5 x 10^7 chemical synapses, with annotations for cell classes and types, nerves, hemilineages and predicted neurotransmitter identities.
- [V-abs] Includes a projectome and information-flow analysis from inputs (sensory, ascending) to outputs (motor, endocrine, descending).
- Relevance: the substrate for the Shiu model and for every structural predictor we would compute (H-A, H-E).

**Dorkenwald et al. 2020, "FlyWire: Online community for whole-brain connectomics", Nature Methods.** https://consensus.app/papers/details/4d6ed89b4ed958768a6018b8809aa3ab/?utm_source=claude_desktop (peer reviewed)
- [V-abs] Proofreading platform; demonstrated on the mechanosensory connectome. Method background only.

**Schlegel et al. 2024, "Whole-brain annotation and multi-connectome cell typing of Drosophila", Nature 634:139-152.** First author as displayed in most records: P. Schlegel (one aggregator listed a different first author). DOI as stated in ws text: 10.1038/s41586-024-07686-5. https://ideas.repec.org/a/nat/nature/v634y2024i8032d10.1038_s41586-024-07686-5.html (peer reviewed)
- [V-abs, ws] 8,453 annotated cell types: 3,643 previously proposed in the hemibrain, 4,581 new, mostly outside the hemibrain volume. About one third of hemibrain-proposed types could not be reliably re-identified.
- [V-abs, ws] "About one in six cell types shows a difference in numbers between left and right hemisphere and one in three across brains"; edge-weight variability exceeds technical noise, giving a lower bound on biological variability (from a ws summary of the paper, found via the variability query, https://www.nature.com/articles/s41586-024-07686-5). Also a caution that whole-connectome statistics can have exceptions for individual neurons.
- Relevance: H-E. Left–right homologs are a legitimate internal replication, but one in six types differ in count, so "homolog" needs a type-matched design. Cell-type labels (consensus types) let us pair neurons across hemispheres and across FlyWire versus hemibrain.

**Lin et al. 2024, "Network statistics of the whole-brain connectome of Drosophila", Nature 634:153-165.** First author A. Lin. DOI in ws text: 10.1038/s41586-024-07968-y. Consensus shows the 2023 bioRxiv version: https://consensus.app/papers/details/53b2bf60fa6a55b89c8f0c57893b4c84/?utm_source=claude_desktop. ws record: https://ideas.repec.org/a/nat/nature/v634y2024i8032d10.1038_s41586-024-07968-y.html
- [V-abs] Two- and three-node motifs, neurotransmitter composition of motifs, rich-club organisation with a large population (about 30% of the connectome) of highly connected neurons, subsets that may act as integrators or broadcasters, and 78 neuropil subnetworks.
- Relevance: H-A. This is the standard source for the global-centrality predictors (rich-club membership, degree) that H-A sets as the low rung. Nothing in the abstract tests functional necessity.

**Eckstein et al. 2024, "Neurotransmitter classification from electron microscopy images at synaptic sites in Drosophila melanogaster", Cell 187(10):2574-2594.** First author N. Eckstein. DOI in ws text: 10.1016/j.cell.2024.03.016. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11106717/ (peer reviewed; 2020 bioRxiv preprint also seen)
- [V-abs, ws] Six transmitters distinguished with about 87% accuracy per synapse and 94% per whole neuron. The 91% figure for known cell types appeared in one aggregator only and is unconfirmed.
- Relevance: the Shiu model's excitatory/inhibitory sign comes from predicted transmitter identity (Nature abstract). Sign-error rate is therefore a real, non-zero model uncertainty. The relation between the six-way accuracy and the binary E/I mapping Shiu used is **not** verified here.

**Matsliah et al. 2024, "Neuronal parts list and wiring diagram for a visual system", Nature 634:166-180.** DOI in ws text: 10.1038/s41586-024-07981-1. https://ideas.repec.org/a/nat/nature/v634y2024i8032d10.1038_s41586-024-07981-1.html
- [V-abs, ws] About 38,500 optic-lobe intrinsic neurons collapsed onto 227 types; a new serpentine medulla family; connectivity with boundary types between the optic lobe and the central brain.
- Relevance: low for the feeding circuit (visual system). Relevant only to the cell-type-collapse idea (types as replicates) and to the escape-versus-feeding competition preprint in §1.3.

**Scheffer et al. 2020, "A connectome and analysis of the adult Drosophila central brain", eLife.** https://consensus.app/papers/details/67d505a942bb586291e6684c15de3e81/?utm_source=claude_desktop (peer reviewed)
- [V-abs] The hemibrain: cell types, compartments, connection-strength distributions, motifs.
- Relevance: second connectome for cross-dataset replication (H-E), but not for the SEZ (see table).

**Bates et al., BANC (brain and nerve cord).** Nature 2026, DOI in ws text 10.1038/s41586-026-10735-w; preprint title "Distributed control circuits across a brain-and-cord connectome". Seen at https://blog.flywire.ai/?p=1823 (FlyWire blog) and ws summary (peer reviewed per ws; not read).
- [V-abs, ws] Adult female CNS, one source gives 158,262 neurons and more than three million synaptic connections (the synapse figure looks low relative to FlyWire, which counts 5 x 10^7 synapses. The counting basis is unverified). Main claim: behavioural control is distributed across brain and cord circuits rather than hub-based.
- Relevance: H-E (independent connectome with brain and cord), possibly for motor output beyond MN9. SEZ and proboscis coverage: **not checked** (search refused).

**Male CNS connectome (Janelia FlyEM and Google).** Project page https://www.janelia.org/project-team/flyem/male-cns-connectome. Cell 2026 paper "Sexual dimorphism in the complete Drosophila male central nervous system connectome": https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6; preprint DOI seen in URL 10.1101/2025.10.09.680999 (https://www.biorxiv.org/content/10.1101/2025.10.09.680999.full.pdf).
- [V-abs, ws] Complete male CNS: central brain, optic lobes and VNC. 331 sex-specific and 114 dimorphic cell types. Counts disagree across sources (about 165,000 to 166,700 neurons; 25.6 M connections vs 6.24 M connections with at least 5 synapses). Data are CC-BY 4.0 (per third-party repos).
- Relevance: H-E (independent connectome of a different sex and animal). The model-on-new-connectome step is already being done by hobbyists (§1.3 grey).

**Takemura et al. (MANC) and companions, eLife.** Seen via https://elifesciences.org/reviewed-preprints/97769v1/reviews and https://elifesciences.org/articles/96084 (DN to motor circuits in MANC).
- [V-abs, ws] Dense male VNC connectome; reviewers flag about 50% reconstruction completion; a follow-up finds direct descending-to-motor-neuron connections are infrequent.
- Relevance: the Pugliese preprint and the axo-axonic study (§1.3) use MANC.

**"From Sensory Detection to Motor Action: The Comprehensive Drosophila Taste-Feeding Connectome", bioRxiv 2025.** First author not visible in what I retrieved. DOI in URL 10.1101/2025.08.25.671814. https://www.biorxiv.org/content/10.1101/2025.08.25.671814.full.pdf (preprint; the Transmitter hints a Cell version exists, unverified)
- [V-abs, ws] Gustatory system mapped at synaptic resolution by cross-matching FAFB-FlyWire and MANC. Taste classes converge on second-order hubs that project to proboscis motor neurons, descending premotor neurons, locomotor-stop circuits and neuroendocrine cells.
- Relevance: H-D and the GRN to MN9 starting circuit. A structural map of exactly the circuit we would perturb, independent of the Shiu model.

**"Connectomic mapping of pharyngeal and gut sensory circuits in adult Drosophila", bioRxiv 2025.** DOI in URL 10.64898/2025.12.14.694216. https://www.biorxiv.org/content/10.64898/2025.12.14.694216.full.pdf (preprint)
- [V-abs, ws] Uses FAFB to identify internal sensory axons entering the SEZ, "a major feeding control center", some of which synapse directly on motor neurons and endocrine cells.
- Relevance: the SEZ is the feeding hub; FlyWire covers it. Also states proboscis motor neurons arborise in the dorsal SEZ (ws).

**Winding et al. (listed 2022 in Consensus; Science), "The connectome of an insect brain".** https://consensus.app/papers/details/11d164f18fc1567384fc80b59a366467/?utm_source=claude_desktop
- [V-abs] Larval connectome, 3,016 neurons and 548,000 synapses; recurrent architecture and feedback from descending neurons. Background only (small, complete, permits full analysis).

### 1.2 The Shiu model itself

**Shiu et al. 2024, "A Drosophila computational brain model reveals sensorimotor processing", Nature 634(8032):210-219.** First author P. K. Shiu. DOI in ws text 10.1038/s41586-024-07763-9. Consensus record: https://consensus.app/papers/details/91a3521fd6815a4b9f24273f6fa6a19e/?utm_source=claude_desktop. PMC (seen in results list): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11446845/ (peer reviewed)
- [V-abs] LIF model of the entire brain from connectivity and neurotransmitter identity. Activating sugar- or water-sensing gustatory neurons "accurately predicts neurons that respond to tastes and are required for feeding initiation". Activating neurons in the feeding region predicts those that elicit motor-neuron firing, a hypothesis validated by optogenetic activation and behavioural studies. Taste-modality interaction predicted. Mechanosensory activation predicts the antennal grooming circuit.
- [V-abs] The abstract mentions neither pairwise silencing nor a sensitivity analysis. Full text not read. See §2 for what the code and notebooks show.
- Relevance: all of H-A to H-E.

**Shiu et al. 2023, bioRxiv, "A leaky integrate-and-fire computational model based on the connectome of the entire adult Drosophila brain reveals insights into sensorimotor processing".** DOI in URL 10.1101/2023.05.02.539144. https://consensus.app/papers/details/c05176ac454c5a0f8eec7fcfa28f390b/?utm_source=claude_desktop (preprint; code README links to this version)
- [V-abs] The preprint abstract adds claims that the Nature abstract omits: the sugar and water pathways "form a partially shared appetitive feeding initiation pathway, which our calcium imaging and behavioral experiments confirm"; and the grooming circuit "do[es] not overlap with gustatory circuits". These are the closest existing statements to H-D, at the activation level.
- Caution: the preprint and Nature versions differ. Cite the Nature version for claims and check whether the shared-pathway claim survived.

**Code: `philshiu/Drosophila_brain_model`** (local clone, last commit 91bdd1e "Update Readme.md"). See §2 for the full source-level audit.

### 1.3 Follow-ups that use, extend, port or test the Shiu model

**Sapkal et al. 2024, "Neural circuit mechanisms underlying context-specific halting in Drosophila", Nature 634:191-200.** DOI in ws text 10.1038/s41586-024-07854-7. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11446846/ (peer reviewed; bioRxiv version 10.1101/2023.09.25.559438 seen in URL)
- [V-abs, ws] Two halting mechanisms: "walk-OFF" (GABAergic brain neurons inhibiting specific descending walking commands, used in feeding contexts) and "brake" (excitatory cholinergic ascending neurons, used in grooming). Screening of SEZ-innervating neurons gave 11 driver lines that halt walking. Authors include P. Shiu.
- [V-abs, secondary] The State of Brain Emulation Report 2025 (https://arxiv.org/pdf/2510.15745, per ws) says Sapkal used the Shiu model. The Sapkal abstract text I saw says "connectome-informed network models". Treat "uses the Shiu LIF model" as secondary-confirmed.
- Relevance: a peer-reviewed example where a Shiu-type model is combined with functional experiments (H-E). Direct evidence that SEZ/feeding circuits couple to locomotor halting.

**An 2026, "How sparse can a fly-brain model be? Connection strength, wiring placement, network state and task jointly determine function-preserving compression of the Drosophila connectome", bioRxiv.** First author D.-G. An (as displayed). https://consensus.app/papers/details/1e64a2d47bdf59e0994a132ddd54b9b9/?utm_source=claude_desktop. bioRxiv URL seen in a result list: https://www.biorxiv.org/content/10.64898/2026.09.19.752860v1 (preprint)
- [V-abs] Uses the Shiu LIF model. Compares six edge-removal operators at identical edge budgets across three validated circuits (sugar-evoked proboscis extension, bitter suppression, grooming pathway specificity), silent versus spontaneously active states, multiple seeds.
- [V-abs] Weak-synapse pruning keeps 79% of feeding output with 6% of edges, with a cliff near k* of about 9 synapses. Random removal, degree-preserving rewiring and weight shuffling at the same budget abolish output. "Function resides in the conjunction of wiring placement and strength, not in degree statistics or synaptic mass."
- [V-abs] Task dependence: grooming specificity collapses below k = 2 through disinhibition. In the active state failure changes character (over-excitation instead of loss) and bitter suppression reverses at k = 31.
- Relevance: **H-A, H-B, H-D, and the circularity concern.** (i) Degree statistics are insufficient to preserve function, consistent with H-A's claim that global centrality is a poor predictor. (ii) Network-state dependence is direct support for H-B's operating-point dependence, though about edges, not neurons. (iii) Edge-level, not neuron-level, perturbation; no pairs of neurons. (iv) Any "synapse-count threshold" sensitivity result for our design should cite this. **Closest prior art for a robustness/sensitivity claim on the Shiu model.**

**"Whole-brain connectomics of Drosophila reveals a robust, distributed architecture for the suppression of feeding during escape", bioRxiv, Dec 2025.** Authors not visible. DOI in URL 10.64898/2025.12.14.694122. https://www.biorxiv.org/content/10.64898/2025.12.14.694122v1.full.pdf (preprint)
- [V-abs, ws] Re-implements the Shiu LIF framework on FlyWire v783 (127,400 neurons stated). Looming predator simulated by activating LC4 and LPLC2. Escape suppresses feeding "not through lateral inhibition at the motor output (MN9), but via upstream disfacilitation" (premotor hub "Roundup"), and the inhibitory architecture is highly modular and distributed. One summary says it cautions against inferring function from structure alone.
- Relevance: **H-A and H-D.** Same readout (MN9) and a mechanism (disfacilitation) that a centrality-based predictor would not see. Only intro/abstract-level evidence; read the paper before citing.

**Li et al. 2026, "Connectome-constrained modeling identifies neurons and synapses that sustain spontaneous activity in Drosophila", bioRxiv.** First author Qian-Zhu Li. https://consensus.app/papers/details/d402f7a05ec7586cb55513877e178ab3/?utm_source=claude_desktop (preprint)
- [V-abs] A FlyWire-constrained whole-brain model **fitted to calcium recordings** of spontaneous activity; systematic in-silico perturbations. Spontaneous activity is organised by a compact neuropil core; a sparse, brain-spanning ensemble of inhibitory hub neurons and their reciprocal synapses with excitatory partners are "necessary and sufficient" for resting-state dynamics.
- Relevance: **H-A, H-B, H-E.** (i) Unlike Shiu's silent baseline, this model has spontaneous activity, which bears on the stance "activity is not necessity". (ii) Hub inhibitory neurons as necessary is a global-structure-type finding (supports centrality for resting-state necessity, different task from MN9 sugar drive). (iii) Fitted to data, so a partial break of circularity.

**Ceballos, Pena et al. 2026, iScience 29(5), "The Drosophila connectome reveals Axo-Axonic Synapses on Descending Neurons that modulate the Giant Fiber System".** Journal DOI in ws text 10.1016/j.isci.2026.115624; preprint 10.1101/2025.09.04.674108 (https://www.biorxiv.org/content/10.1101/2025.09.04.674108.full.pdf) (peer reviewed)
- [V-abs, ws] Brian2 LIF simulations of the whole MANC v1.2.1 VNC connectome (23,437 valid neurons; 1,152,548 connections per a conference abstract, unverified). Predicted axo-axonic modulators of the Giant Fiber pathway were tested with optogenetic activation in vivo.
- Relevance: **H-E**, another model-then-experiment loop on a different connectome. It is not stated here to reuse the Shiu code. Treat as "Shiu-style", not "Shiu".

**Pugliese et al. 2026 (listed 2026 in Consensus), "Connectome simulations identify a central pattern generator circuit for fly walking", bioRxiv.** First author S. M. Pugliese. https://www.biorxiv.org/content/10.1101/2025.09.12.675944.full.pdf (DOI in URL; the DOI suggests a Sept 2025 posting while Consensus lists 2026; date conflict) https://consensus.app/papers/details/4b6e0ac8599f5c8d9834508b3edc505c/?utm_source=claude_desktop (preprint)
- [V-abs] Activation screen of descending neurons in VNC connectome simulations. Simulated network pruning isolates a three-neuron rhythm generator that was "necessary and sufficient for motor rhythms across all six legs and in four connectome datasets". A second descending pathway (DNb08) predicted and confirmed with optogenetics.
- [V-abs, ws] The simulation is a firing-rate model on MANC front-leg neurons, so **not** the Shiu LIF model.
- Relevance: **H-C and H-E.** A published template for (a) greedy pruning to a minimal necessary-and-sufficient circuit (a within-model minimal-cut analysis), and (b) replication across four connectome datasets. It tests necessity/sufficiency by pruning, not pairwise interaction types.

**Wang et al. 2025, "Neuromorphic Simulation of Drosophila Melanogaster Brain Connectome on Loihi 2", arXiv.** First author Felix Wang. https://consensus.app/papers/details/d968aeea2b4655619829d70bf7dc46a3/?utm_source=claude_desktop (preprint)
- [V-abs] FlyWire connectome (140K neurons, 50M synapses) on 12 Loihi 2 chips; "orders of magnitude faster than numerical simulations on conventional hardware", statistically validated against reference simulations; advantage grows with sparser activity.
- Relevance: feasibility for large perturbation screens if hardware were available. The abstract does not say it reproduces the Shiu model specifically.

**Wang C. et al. 2026, "Model-agnostic linear-memory online learning in spiking neural networks" (BrainTrace), Nature Communications.** https://consensus.app/papers/details/5b9a9ab60ae95715ae1e8925b8f39e8b/?utm_source=claude_desktop (peer reviewed)
- [V-abs] Enables "online fitting of a whole-brain-scale Drosophila SNN that recapitulates region-level functional activity". Peripheral to our questions.

**Software ports and third-party extensions (grey literature; not peer reviewed; I read READMEs and a few scripts only, ran nothing).**

| Repo (as seen) | What the README says [V-src] | Relevance |
|---|---|---|
| `eonsystemspbc/fly-brain` (last commit 2026-08-29) https://github.com/eonsystemspbc/fly-brain | Shiu LIF model benchmark across Brian2 (CPU ground truth), Brian2CUDA, PyTorch, NEST GPU, GeNN and Brian2GeNN; compares spike outputs to Brian2 via Jaccard overlap and rate correlations. README says "Based on Shiu et al." and repeats the "91% prediction accuracy" claim (see §4). Repeats Shiu's "to and from" silencing sentence. | GPU/PyTorch re-implementation exists. For our budget: a validated faster backend may exist (the feasibility agent should assess). |
| `Kisame76/drosophila-brain-mlx` (2026-09-26) https://github.com/Kisame76/drosophila-brain-mlx | Apple-silicon MLX port of the Shiu model, "same parameters, same tick ordering", 0.29 s per biological second vs 2.07 s in Brian2 on an M4 Pro (self-reported). Includes a degree-preserving shuffled-connectome control: MN9 fires 67.3 Hz on real wiring, silent on 5 shuffles (21 right sugar GRNs at 100 Hz). | Independent confirmation that wiring beyond degree and sign is needed for the sugar to MN9 signal (consistent with An 2026). Also independently confirms the README-vs-code silencing discrepancy (§2.5). |
| `UditAkhourii/StrokeSim` (2026-10-27) https://github.com/UditAkhourii/StrokeSim | Single-author "preprint in preparation". Shiu model on FlyWire v783/v630 and MaleCNS. Region-wise silencing (MN9 survives 49 of 51 regions, GNG is a single point of failure), a **single-neuron knockout screen of 402 PRW neurons** (CB0246 top hit), **pairwise knockouts of 6 "chain" cells (all singles and pairs, 10 trials)**, weight-scale replication (0.25 to 0.35 mV) and a "static paths" predictor of the knockout screen: Spearman 0.70 (static weighted paths) and 0.81 (activity-weighted paths) among the 21 active PRW neurons; sign-blind paths mis-rank an inhibitory neuron first. | **Closest grey-literature pre-emption of H-A (structure vs structure plus activity), H-C (pairs) and the replication part of H-E.** Not peer reviewed, one circuit, no centrality baselines described in what I read, and I have not reproduced anything. Must be cited as such if used. |
| `gianlucamazza/flymsg` (2026-11-02) https://github.com/gianlucamazza/flymsg | Shiu-style whole-CNS LIF model on MaleCNS v1.0 with pre-registered silencing scans. Reports "silence fails": silencing both DNp01 leaves TTMn_R firing; a "residual partner" scan names DNp02 or DNp06, and silencing DNp01 plus either takes TTMn_R from 7 spikes to 0 (replicated on fresh seeds). States limits: "qualitative rates", validation cases mostly 1 to 2 hop chains, transmitters are machine predictions, 2.6% of synapses carry no sign. | A concrete grey-literature example of a **parallel-route (redundant) pair** in a Shiu-type model (H-C). Same caveats. |
| PyPI `flycns` and `flybrain`, GitHub `IONOFIELD/FLYCNS`, `lixiang1076/fly-brain` | Seen only as search-result titles/summaries (ws): LIF ports to MaleCNS (flybrain: 166,700 neurons, 25.6 M connections, CuPy). Not inspected. | Evidence that the model has been ported to MaleCNS several times. Quality unknown. |

### 1.4 Other connectome-constrained or connectome-structured models (not the Shiu model)

**Zhang et al., "Network structure governs Drosophila brain functionality", Fundamental Research (2024; "© 2025" in the record).** First author Xiao-Yu Zhang. https://consensus.app/papers/details/7eac1cab743e57028b6f237c38d3afe7/?utm_source=claude_desktop. arXiv 2404.17128 (listing shows the title changed across versions v1 "Simple Network Mechanism Leads to Quasi-Real Brain Activation Patterns with Drosophila Connectome", v3 "Network Structure Trumps Neuron Dynamics...", v4 current) https://arxiv.org/html/2404.17128v4 (peer reviewed)
- [V-abs] Simplified activation mechanisms on the adult connectome give activation patterns resembling the real brain; patterns are consistent across neuron-dynamics models sharing a network structure; network distance (not spatial distance) determines activation; a reconnect rate of at least 1 per mille "was sufficient to disrupt the previously observed activation patterns"; interhemispheric synergy for unilateral visual stimuli.
- [V-abs, ws] Degree-preserving rewiring gave no correct activation pattern. I could not confirm which dynamics models were used (nothing indicates it re-implements Shiu).
- Relevance: **H-A and the circularity concern.** "Structure predicts model activation" is nearly guaranteed when model and predictor share W. The paper's own null (degree-preserving rewiring) is the standard control we should copy. Its "activation pattern" is a population response, not single-neuron necessity.

**Zhang et al. 2025, "Structural Heterogeneity of the Drosophila Brain Network".** https://consensus.app/papers/details/bfc962687ea355f992f28d6eb4c15c2c/?utm_source=claude_desktop (venue unknown in record; arXiv 2509.26019 seen in a result URL)
- [V-abs] Bilateral symmetry in topology; Kuramoto simulations suggest functional hemispheric asymmetry arises from differences in intrinsic frequencies, not structural asymmetry. Relevance: H-E (left–right).

**McAllister et al. 2026, "Non-random brain connectome wiring enables robust and efficient neural network function under high sparsity", bioRxiv.** https://consensus.app/papers/details/4e8b9594fc7b5397aa1212affa0eb1d4/?utm_source=claude_desktop (preprint; Ulster record at https://pure.ulster.ac.uk/en/publications/non-random-brain-connectome-wiring-enables-robust-and-efficient-n/)
- [V-abs] Echo State Networks wired from the Drosophila connectome vs sparsity-matched random networks on eight cognitive tasks. "The importance of a neuron for task performance correlated with its node degree, local clustering, and selfrecurrency, and these correlations were stronger in CoNNs than in random networks." CoNNs more robust to neuronal loss and hyperparameter variation; excess self-recurrency is sufficient to explain the robustness.
- Relevance: **H-A, directly adversarial.** In a trained reservoir computer, neuron importance correlates with degree. Our H-A says global centrality predicts single-neuron necessity poorly in the LIF sensorimotor setting. These are different systems (trained linear readouts; which fly connectome is not stated in the abstract. A Cambridge talk abstract by a McAllister described a *larval* connectome, ws, https://talks.cam.ac.uk/talk/index/232441), but a reviewer will cite it. We need a stated reason why the LIF sensorimotor case differs (single readout, thresholded drive, silent baseline).

**Related echo-state / reservoir papers on connectome wiring** (all abstract-level, [V-abs]; relevance mostly background for H-A):
- Costi et al. 2025, Biomimetics, "The Drosophila Connectome as a Computational Reservoir for Time-Series Prediction": both topology and weights contribute to overfitting resilience. https://consensus.app/papers/details/fdf7e818d7b85b9486e20ecd9e1f845c/?utm_source=claude_desktop
- Morra et al. 2022 (IJCNN 2023), "Using Connectome Features to Constrain Echo State Networks". https://consensus.app/papers/details/e3f9ec94e192547eb24062e50a5457e4/?utm_source=claude_desktop
- Yan et al. 2025 (bioRxiv), "Cross-species connectome comparisons...": "weakly connected but highly central nodes are essential ... their targeted perturbation significantly degrades performance." https://consensus.app/papers/details/4b592a8083a758be802ea37178905f18/?utm_source=claude_desktop
- Takahashi et al. 2025 (IJCNN): robustness to spectral radius "attributable to network-level characteristics ... rather than the presence of high-degree hub nodes". https://consensus.app/papers/details/00ae6571574d5b7ab7dcca8fc4d9df3c/?utm_source=claude_desktop
- Damicelli et al. 2021/22 (PLOS Comput Biol), "Brain connectivity meets reservoir computing". https://consensus.app/papers/details/0e880e49322654ffabc59af40953d345/?utm_source=claude_desktop
- Relevance to H-A: the reservoir literature itself is split on whether hubs matter (Yan: weak-tie central nodes matter; Takahashi: not hubs). Good evidence that "degree predicts importance" is task- and model-dependent.

**Therianos 2026, "A frozen rate operator from the complete larval connectome: degree and weight govern the gross response, exact wiring governs input routing and mushroom-body modes".** https://consensus.app/papers/details/c9caa8cc1cda539585703f5a2e4c69bb/?utm_source=claude_desktop (venue unknown)
- [V-abs] Larval connectome (2,825-neuron strongly connected core) as a frozen leaky-tanh rate operator with no fitted single-neuron parameters, against degree-and-weight-matched rewired ensembles. Gross signature (gain, effective dimensionality) is set by coarse statistics. Under sparse afferent drive the operator confines activity to a fifth of the core vs two thirds for the ensemble; both spatial properties "depend on the exact placement of synapses".
- Relevance: **H-A and the circularity concern, directly.** This is the "which compression of W is sufficient" question posed explicitly, answered for a larval rate model: coarse statistics suffice for gross response, exact wiring needed for routing. It is not an adult LIF necessity study. Cite as nearest conceptual prior art for the sufficiency-of-compressions framing.

**Pospisil et al. 2024, "The fly connectome reveals a path to the effectome", Nature 634:201-209.** DOI in ws text 10.1038/s41586-024-07982-0; preprint "From connectome to effectome: learning the causal interaction map of the fly brain" (bioRxiv Feb 2024). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11446844/ (peer reviewed)
- [V-abs, ws] Stochastic optogenetic perturbation data plus the connectome as a strong prior to estimate a causal interaction map ("effectome"). Reported finding: fly whole-brain dynamics appear to be "generated by a large collection of small circuits that operate largely independently of each other".
- Relevance: **H-E, H-C.** The one empirical, perturbation-based causal map for the fly that I found. "Largely independent small circuits" is a prior against strong pairwise interactions between random neurons, but our H-C targets pairs on parallel routes converging on a shared target, which is exactly what independence-of-circuits would exclude. Should be a baseline for what fraction of random pairs interact.

**Lappalainen et al. 2024, "Connectome-constrained networks predict neural activity across the fly visual system", Nature 634:1132-1140.** DOI in ws text 10.1038/s41586-024-07939-3. https://consensus.app/papers/details/e5590ea6830753528b4eda6e1e89b8a5/?utm_source=claude_desktop (peer reviewed)
- [V-abs] Connectivity of 64 optic-lobe cell types with unknown single-neuron and synapse parameters, optimised by deep learning on a motion-detection task. Predictions agreed with experiments across 26 studies. "More likely to be successful when neurons are sparsely connected."
- Relevance: H-A and H-E. The standard demonstration that connectivity plus a task constraint can predict activity. A different recipe from Shiu (fitted vs a single global weight).

**Cowley et al. 2024, "Mapping model units to visual neurons reveals population code for social behaviour", Nature.** https://consensus.app/papers/details/9fc3c0d8d58d5dbc9732091bd9dcf135/?utm_source=claude_desktop (peer reviewed)
- [V-abs] "Knockout training": perturbing the network during training to match behavioural effects of real cell-type perturbations, giving a one-to-one unit-to-cell-type mapping. Conclusion: combinations of visual projection neurons drive male interactions with the female (a population code), against one-channel-one-behaviour.
- Relevance: **H-C, H-E.** A behavioural precedent that combinations rather than single channels matter, and a methodological template for using real perturbation data as a constraint. Not a connectome-LIF study.

**Beiran and Litwin-Kumar, "Prediction of neural activity in connectome-constrained recurrent networks", bioRxiv 2024.** DOI in URL 10.1101/2024.02.22.581667. https://consensus.app/papers/details/f39526282bc25da2852b8c03e30aa8aa/?utm_source=claude_desktop (preprint. A Nature Neuroscience version was **not** confirmed by my search)
- [V-abs] Teacher-student theory: "a connectome is often insufficient to constrain the dynamics of networks that perform a specific task, illustrating the difficulty of inferring function from connectivity alone", but recordings from a small subset of neurons can remove the degeneracy.
- Relevance: **H-A, H-E, stance 2.** Theoretical support for "structure alone underdetermines function" when biophysical parameters are uncertain. Shiu fixes those parameters to one set of values, which hides this degeneracy.

**Karaneen et al. 2026, "Reproducibility and model-selection stability in connectome-constrained circuit modeling", bioRxiv.** First author as displayed: C. Karaneen. https://consensus.app/papers/details/00fba7b81a1a5f69b97d32b2c8e1e16c/?utm_source=claude_desktop (preprint)
- [V-abs] Retraining connectome-constrained models of the motion pathway under identical conditions: task performance is similar but identification of biologically plausible circuit solutions is unstable.
- Relevance: H-E. Cautionary for any fitted-model route. Not relevant to the fixed-parameter Shiu model except as a reminder that "same behaviour" does not pin down mechanism.

**Braun et al. 2024, "Descending networks transform command signals into population motor control", Nature 630:686-694.** DOI in ws text 10.1038/s41586-024-07523-9. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11186778/ (peer reviewed)
- [V-abs, ws] Command-like descending neurons recruit larger DN populations through direct excitatory DN to DN connections, within behaviour-specific clusters that inhibit one another; connectome analysis plus manipulations.
- Relevance: **H-C, H-D.** Experimental evidence that single "command" neurons are not sufficient or necessary alone in the descending population, supporting the rationale for pair/network perturbations. The paper is an analysis-plus-experiment study, not a simulation.

**Clark et al. 2025, "Connectivity Structure and Dynamics of Nonlinear Recurrent Neural Networks", Physical Review X.** https://consensus.app/papers/details/91ba2ca519b8541a9d99cf5459507e14/?utm_source=claude_desktop
- [V-abs] Theory of how singular-value spectrum and left–right mode overlaps shape collective dynamics; shows structured overlaps in the Drosophila connectome. Relevance: H-A (analytic grounding), not a perturbation study.

**Litwin-Kumar et al. 2019, "Constraining computational models using electron microscopy wiring diagrams", Curr Opin Neurobiol.** https://consensus.app/papers/details/fab0c2ab3b015a3b809caa59ba742c1e/?utm_source=claude_desktop (first author A. Litwin-Kumar as displayed). [V-abs] Review: no standard toolset yet for incorporating connectivity constraints into models. Background only.

**Earlier whole-brain spiking models:** Huang et al. 2018, Frontiers in Neuroinformatics, "A Single-Cell Level and Connectome-Derived Computational Model of the Drosophila Brain" (FlyCircuit-based Flysim, 20,089 neurons; connectome vs shuffled network behaves differently under short-term depression). https://consensus.app/papers/details/27da0b997dea5d05abbb3d70bd3354e7/?utm_source=claude_desktop [V-abs]. Nanami et al. 2024 (olfactory SNN on an FPGA) [V-abs] https://consensus.app/papers/details/be4b599262295dc689e1eb7575daa85c/?utm_source=claude_desktop. Prior art for the "shuffled network" control.

### 1.5 Embodied and whole-body models

**Vaxenburg et al. 2025, "Whole-body physics simulation of fruit fly locomotion", Nature 643:1312-1320 (flybody).** DOI in ws text 10.1038/s41586-025-09029-4. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12310536/ ; Consensus https://consensus.app/papers/details/529af6638ade5fae930e00437768699c/?utm_source=claude_desktop (peer reviewed)
- [V-abs] MuJoCo whole-body model; RL-trained neural controllers for walking and flight; visual sensors and hierarchical control. Controllers are **not** connectome-constrained.

**Wang-Chen et al. 2024, "NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila", Nature Methods** https://consensus.app/papers/details/71b2a511b8575b27b0e3ce7d158e96be/?utm_source=claude_desktop (peer reviewed; bioRxiv preprint https://consensus.app/papers/details/a4057079d74d5bbaa8b60ec12d9f7acf/?utm_source=claude_desktop)
- [V-abs] Vision, olfaction, ascending feedback, complex terrain; includes a connectome-constrained visual network for fly-following.

**Jin et al. 2026, "Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly" (Fly-connectomic Graph Model, FlyGM), arXiv.** https://arxiv.org/pdf/2602.17997 ; https://consensus.app/papers/details/d79ca149ac4f5e4b894ad839085d6899/?utm_source=claude_desktop (preprint)
- [V-abs] Instantiates the adult whole-brain connectome as a graph-structured neural controller for a simulated biomechanical fly, trained with deep RL; better sample efficiency than graph and non-graph baselines.
- Relevance: connectome as an architectural prior; not a perturbation study. Possible source for "connectome structure helps" claims; no necessity analyses seen.

**Eon Systems, "embodied fly" (March 2026 onwards).** Company posts https://eon.systems/updates ; https://eon.systems/updates/embodied-brain-emulation ; coverage https://the-decoder.com/startup-claims-first-full-brain-emulation-of-a-fruit-fly-in-a-simulated-body/ . **No peer-reviewed paper found.**
- [V-abs, ws] Announced 2026-03-08: FlyWire connectome with a simple LIF neuron model from Shiu et al. controlling a MuJoCo NeuroMechFly body. The blog reports "91% behavior accuracy"; the homepage describes the 91% differently (as the 2024 Nature paper's match to biological neural responses). The two metrics are inconsistent in the ws summary.
- [V-abs, ws] Eon states the body is not driven by the full downstream motor hierarchy and that the mapping from brain outputs to body was constructed by the team (a "real limitation of the FlyWire connectome"). Body-coupling code was reportedly not released at the time of one article.
- Relevance: embodiment shows the Shiu model is being used as a controller, but nothing here speaks to perturbation or necessity. Do not cite the 91% figure.

### 1.6 Connectome variability, hubs and lesion-type structure analyses

- Schlegel et al. 2024 (above): left–right and across-brain variability measured. No study found that propagates measured weight variability through a dynamical model to function (that search was only partly covered; see §0.3).
- **Pedigo et al. (eLife), "Generative network modeling reveals quantitative definitions of bilateral symmetry exhibited by a whole insect brain connectome".** Title seen at https://elifesciences.org/articles/83739 . Per ws summary: larval brain left/right connection probabilities differ overall; strongest edges (by input proportion) do not differ significantly. [V-abs, ws] Relevance: H-E: supports restricting homolog comparisons to strong edges. First author inferred from the known paper [MEM] and not shown in what I retrieved.
- **Corradini et al. 2026, "A Complex Network-Based Approach for Detecting and Characterizing Power Neurons in Drosophila", Neuroinformatics 24:11.** DOI in ws text 10.1007/s12021-026-09773-6. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12904900/ (peer reviewed). [V-abs, ws] "Power neurons" = high in degree, closeness, betweenness and eigenvector centrality simultaneously; 60,848 rich-club neurons and 5,473 power neurons; claim that a very small number of power neurons "can strongly influence all other neurons". It is structural; no functional lesion validation. Relevance: H-A. This is the kind of "important by centrality" claim we would test; a clean target for a negative result.
- Search for "in-silico lesion centrality predicts functional importance in the fly" returned no direct study (ws), consistent with an open gap, but this was one query.

### 1.7 C. elegans analogues (brief)

**Randi, Sharma, Dvali, Leifer 2023, "Neural signal propagation atlas of Caenorhabditis elegans", Nature 623:406-414.** DOI in ws text 10.1038/s41586-023-06683-4. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10632145/ (peer reviewed; arXiv 2208.04790)
- [V-abs, ws] Single-neuron stimulation with whole-brain calcium imaging across about 23,400 neuron pairs. Functional measurements predict spontaneous activity better than anatomy does; the gap is partly attributed to extrasynaptic (peptidergic) signalling not in the wiring diagram.
- Relevance: **H-E, stance 1.** The direct "structure is not function" benchmark and the template for an experimental ground truth. It also warns that a synaptic-only model (as Shiu) omits a whole channel.

**Bacik et al. 2016, "Flow-Based Network Analysis of the Caenorhabditis elegans Connectome", PLoS Comput Biol 12(8):e1005055.** DOI in ws text 10.1371/journal.pcbi.1005055. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4975510/ (peer reviewed; arXiv 1511.00673)
- [V-abs, ws] In-silico evaluation of **all single and double neuron ablations** for their disruption of multi-scale flow structure; ablations linked to functionally relevant neurons. Flow structure, not spiking dynamics.
- Relevance: **H-C.** The only exhaustive single-plus-double ablation study I found; it is structural (graph flow), not a dynamical model. It is precedent for the pair-screen idea on a structural readout.

**"Asymmetry in synaptic connectivity balances redundancy and reachability in the C. elegans connectome", bioRxiv (2024).** DOI in URL 10.1101/2024.03.06.583122 (seen as a title in a result list only; content only from ws). Redundancy defined as selective reinforcement of paths between neuron classes via parallel alternatives. Relevance: H-B/H-C vocabulary; unverified beyond the title.

**Duan et al. 2021, "Resilience of Nematode Connectomes Based on Network Dimension-reduced Method"** (record shows an "Unknown Journal"). https://consensus.app/papers/details/2517bc8d89555e4ca6eea03bc01673bc/?utm_source=claude_desktop [V-abs] A mean-field-derived neuron importance index (x_eff) for C. elegans and P. pacificus. Relevance: H-A (a dimension-reduced importance index is a competitor to an (I - DW)^-1 predictor). Low-visibility source; verify before citing.

**Mann et al. 2017, "Whole-brain calcium imaging reveals an intrinsic functional network in Drosophila", Current Biology.** https://consensus.app/papers/details/8dba5322dc43570cbefc21372008f5c5/?utm_source=claude_desktop [V-abs] Region-level functional connectivity in the fly; early benchmark for structure–function comparison (H-E). I did not search for the follow-up whole-brain-imaging studies that compare against the connectome.

---

## 2. Shiu et al. 2024 capability sheet

All of §2.1 to §2.6 is **[V-src]** unless tagged, from `model.py`, `utils.py`, `example.ipynb`, `figures.ipynb` and the two data pairs in `/home/user/external/Drosophila_brain_model`. I read all of this; I ran no simulation. The only code I executed was a pandas read of the data tables (to count rows and check signs).

### 2.1 Model specification

| Item | Value / rule |
|---|---|
| Neuron | LIF: `dv/dt = (v_0 - v + g)/t_mbr`, `dg/dt = -g/tau`. `v_0 = v_rst = -52 mV`, `v_th = -45 mV` (a 7 mV gap), `t_mbr = 20 ms`, `tau = 5 ms`, refractory 2.2 ms, synaptic delay 1.8 ms. Reset sets `v = v_rst` and `g = 0`. |
| Synapse | Presynaptic spike does `g += w` after the delay. `w = (signed synapse count) * w_syn`, with `w_syn = 0.275 mV`, labelled in the code comment as the "Free parameter". One value for all synapses; no per-synapse heterogeneity beyond count and sign. |
| Input (activation) | `PoissonInput` onto the membrane voltage of chosen neurons, rate `r_poi` (default 150 Hz) and a second class at `r_poi2` (default 0 Hz). Weight `w_syn * f_poi` with `f_poi = 250`, i.e. 68.75 mV per input event, far above the 7 mV gap, so each Poisson event elicits a spike. Poisson-targeted neurons have refractory period 0. |
| Baseline activity | **None.** No background drive, no noise term. Neurons start at `v_0` and `g = 0`. A neuron that is not reached by the stimulus does not fire. This matches STRATEGY §3.3: zero baseline means zero silencing effect by construction. |
| Stochasticity | Only the Poisson input. A trial is 1 s; 30 trials per condition by default. |
| Sign | See §2.2: assigned per presynaptic neuron. |
| Not in the model (from code; matches the authors' stated limits in ws) | Morphology, receptor dynamics, gap junctions, neuromodulation, plasticity, intrinsic heterogeneity, glia, spontaneous activity. |

### 2.2 Data files (read with pandas; counts are mine)

| | v630 (paper version) | v783 (public) |
|---|---|---|
| Neurons (rows in completeness CSV) | 127,400 | 138,639 |
| Directed edges (unique pre to post pairs) | 14,687,178 | 15,091,983 |
| Sum of |signed counts| (total synapses) | 52,793,639 | 54,492,922 |
| Minimum `Connectivity` | 1 | 1 |
| Share of edges that are inhibitory (negative weight) | 0.401 | 0.400 |
| Share of presynaptic neurons inhibitory | not computed | 0.300 |

- **No synapse-count threshold is applied in the model files**: the minimum edge weight is 1 synapse. In v783, 82.1% of edges have fewer than 5 synapses; only 2,700,513 edges have 5 or more. Any threshold analysis (cf. An 2026) therefore starts from the full table.
- **Sign is a property of the presynaptic neuron**: in v783 every one of the 138,005 presynaptic neurons has a single `Excitatory` value (+1 or -1). The model cannot represent mixed-transmitter neurons or cotransmission.
- Self-loops: none (0 in both files).

### 2.3 What perturbations the code implements

1. **Activation**: Poisson drive of a neuron set at a fixed rate; two sets with different rates.
2. **Silencing**: `silence()` sets the weight of every synapse **from** the neuron to 0. The code is `syn.w[' {} == i'.format(i)] = 0*mV`, which selects synapses whose presynaptic index equals `i`.
   - **README vs code discrepancy.** The README (and the Eon port's copy) says silencing "sets all synaptic connections to and from those neurons to zero". The code zeroes only outgoing synapses. A silenced neuron still receives input, integrates and can spike; it just has no effect on others. The MLX port's README independently states the same discrepancy ("its code produced the published results, and this follows the code").
   - Consequence: "silencing a neuron" and "removing a node" are different in-silico operations. For effects on downstream targets they coincide. They differ for any readout measured on the silenced neuron itself, and for neurons that are also stimulated.
3. Nothing else: no lesion by edge, no weight scaling API, no partial silencing, no noise injection, no hyperpolarising current. A graded (dose) silencing or an edge-wise knockout would require new code.
4. Each `run_trial` rebuilds the full network (`create_model`) for every trial, 30 trials per experiment. The cost model is the feasibility agent's job. Noted only because pairwise screens multiply it.

### 2.4 Analyses in `figures.ipynb` (what the repo shows the authors ran)

| Fig | What is run | Readout | Perturbation type |
|---|---|---|---|
| 1D | 21 right-hemisphere labellar **sugar GRNs** activated at 10 to 200 Hz in steps of 10 Hz | rates of all neurons; top 200 responders at 200 Hz saved | activation |
| 1E | **Each of the top-200 responders** activated alone, 25 to 200 Hz (8 rates) | MN9 rate | single-neuron activation (sufficiency) |
| 1F | Sugar GRNs at 50 to 120 Hz (8 rates in 10 Hz steps), **each of the top-200 silenced one at a time** | MN9 rate | **single-neuron silencing (necessity), restricted to the top 200 responders** |
| 2 | Activation of many cell-type groups from `sez_neurons.pickle`, at 50, 100, 150, 200 Hz | MN9 (left and right IDs) | group activation by type |
| 3A, 3B | Sugar x bitter and sugar x Ir94e activation on 11 x 11 grids of rates (0 to 200 Hz); bitter GRN set has 21 IDs, Ir94e set 18 | MN9 | co-activation interaction, not silencing |
| 4A to 4C | Water GRNs (18 IDs): activation 20 to 260 Hz, top-200 individual activation, **top-200 individual silencing at 160 to 220 Hz** | MN9 | activation, silencing (water) |
| 4E | Sugar x water grid (11 x 14 rates) | MN9 | co-activation |
| 5 | JON (Johnston's organ, mechanosensory) groups; top-300 responders individually activated and **individually silenced** (140 to 180 Hz) | descending neurons DN1_1 and DN2_l (and aBN1 in 5G) | single silencing and activation; S5C: **3 inhibitory neurons silenced together** (`three_inhibitory`) while JON-F is driven | 
| S1D | Left-hemisphere sugar GRNs (10 IDs) | rates | left-right check on the input side only |

Observations:
- **No pairwise or combinatorial silencing screen is present in the repo.** The only multi-neuron silencing is the three-neuron set in S5C. Pair or combination effects are explored only on the **input side** (sugar x bitter, sugar x Ir94e, sugar x water co-activation grids).
- **Silencing screens are restricted to the 200 (sugar, water) or 300 (JON) most responsive neurons** at maximal drive, so silent-by-construction and weakly active neurons are never tested. This is a ranking-by-activity filter built into the original analysis, which STRATEGY §3.3 flags.
- Sugar, water and JON silencing are each run over a **narrow band of input rates** (sugar 50 to 120 Hz; water 160 to 220 Hz; JON 140 to 180 Hz). The operating point is chosen per task. A ws summary says the paper's silencing criterion was MN9 firing "80% or lower compared to control ... at any of the 8 sugar activation frequencies" (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11446845/ via ws; not read in full). That is a max-over-rates rule: a neuron counts as "required" if it matters at any one rate, an implicit acknowledgement of the intensity dependence in H-B. The same text implies no formal margin theory.
- Sugar silencing (1F) and water silencing (4C) were both run on top-200 sets. **Whether the paper compares the two necessity lists (H-D) I could not verify.** The raw data to do so exist in the Shiu data archive (https://doi.org/10.17617/3.CZODIW, named in the README; I did not check its contents).
- Left-right: only the input GRNs have a left-hemisphere run (S1D). The MN9 readouts use left and right IDs (Fig 2). **Practical gotcha:** the right MN9 ID used in Fig 2 (`720575940645521262`) is present in the v630 completeness file but **absent from the v783 file**; the left MN9 (`720575940660219265`) is present in both. IDs change between materialisations, so the ID-to-neuron mapping must be re-derived for v783 rather than copied.

### 2.5 What was validated, and how

- **Experimentally validated (abstract level, [V-abs])**:
  - Prediction that activating specific feeding-region neurons elicits motor-neuron firing: validated by optogenetic activation and behavioural studies (Nature abstract).
  - Prediction that sugar and water pathways form a partially shared feeding-initiation pathway: calcium imaging and behaviour (bioRxiv abstract only; presence in the Nature text not verified).
  - Taste-modality interaction predictions (bitter suppression of sugar drive; Ir94e role) and mechanosensory subtype to antennal grooming circuit predictions: stated as "accurate" against prior literature (Nature abstract). The Ir94e item is described by a secondary source as a "novel prediction about an inhibitory role" (ws; State of Brain Emulation Report).
- **Not (as far as the abstracts show) experimentally validated by silencing in real flies:** the computational silencing screen's list of "required" neurons was matched to prior experiments ("required for feeding initiation", abstract ref 4), not freshly tested by silencing. I cannot confirm from abstracts how many silencing predictions were checked, so any claim about "silencing validated" is unsupported here.
- **Calibration**: `w_syn` is the one parameter the code labels "free". A secondary source says it was set so that 100 Hz sugar GRN drive gives about 80% of maximal MN9 firing (ws; unverified, not in the code). If true, MN9's operating point is partly built in, which affects any claim about absolute necessity at 100 Hz.
- **Accuracy numbers**: "91% accuracy across 164 experimental predictions" circulates in the Eon README, the Eon blog and a secondary report (State of Brain Emulation Report 2025, per ws). I could **not** verify it against the Nature paper. Treat as unconfirmed (see §4). Do not use it in our documents.
- **Controls in the original work**: a ws summary says Shiu's own control shuffled connectivity weights while keeping the global weight distribution (unverified). Independent grey controls: degree-preserving shuffle (MLX README), weight noise and weight-scale 0.25 to 0.35 mV (StrokeSim README), edge-removal operators (An 2026, peer-review status: preprint).

### 2.6 What the model can and cannot do (for our design)

Can:
- Compute single-neuron necessity and sufficiency for MN9 under sugar or water GRN drive. Group silencing is trivial (pass a list). The infrastructure for pair screens exists (a list of two IDs), only the cost is a problem.
- Produce graded dose-response over input rate (done by Shiu for several tasks), which is what H-B needs (necessity as a function of operating point).
- Run on v630 (paper) and v783 (public) with the same code. Third-party ports target MaleCNS.

Cannot (without code changes) or is built in:
- Background activity: absent. "Baseline predictor" for necessity is zero for every neuron not driven by the stimulus; activity under the stimulus must be the baseline.
- Mixed-sign or neuromodulatory neurons; extrasynaptic signalling (Randi in C. elegans shows this is a large channel; for flies the model's authors list it as a limitation, ws).
- Silencing that also blocks input (the README claims it, the code does not).
- Heterogeneous synaptic strengths: all synapses count equally in weight. A 1-synapse and a 100-synapse edge differ only by linear count.
- Absolute rates: qualitative only (flymsg README states this for its own port; the Shiu paper's abstract speaks of "predicts neurons that respond", not rates).

### 2.7 Peer-reviewed and preprint follow-ups on the Shiu model, summarised

| Work | Status | Perturbation type on the model |
|---|---|---|
| Sapkal 2024 | Nature | uses a connectome-informed (Shiu-type) model for halting circuits; combined with experiments |
| An 2026 | bioRxiv | edge removal (six operators), not neurons |
| Escape vs feeding, Dec 2025 | bioRxiv | circuit-level mechanism with MN9 as readout, v783 |
| Eon, MLX, StrokeSim, flymsg, others | grey | ports; StrokeSim has neuron screens and pairs on a 6-cell chain |

---

## 3. Established vs open

### 3.1 Established (with the strength of evidence)

1. **A synapse-count plus sign LIF model with one global weight reproduces a number of known sensorimotor relations at the level of which neurons are recruited** (Shiu 2024 abstract, [V-abs]). Quantified accuracy is unverified.
2. **Wiring beyond degree, weight statistics and sign matters for function in that model.** An 2026 (preprint, [V-abs]) and the MLX shuffle control (grey, [V-src]) both show degree-preserving rewiring abolishes the sugar to MN9 output. Zhang 2024 [V-abs] shows the same for a simpler propagation model. This is the one claim in the area with three independent, if low-level, supports.
3. **Sparsification has a task- and state-dependent cliff** (An 2026): the right synapse threshold differs between feeding (k* about 9) and grooming (k below 2), and in an active state failure flips from loss to over-excitation. The Shiu model files contain all edges at 1 synapse or more, so thresholds are free parameters [V-src].
4. **Parallel redundancy appears in Shiu-type models** in at least one grey example (flymsg: DNp01 silence "fails", residual partners DNp02/DNp06; pair silencing abolishes the TTMn_R response).
5. **Cross-connectome replication is feasible and has been done informally** (StrokeSim: v630, v783, MaleCNS) and formally for a different (VNC, firing-rate) model (Pugliese: four datasets).
6. **For trained reservoirs (ESNs), neuron importance correlates with degree, clustering and self-recurrence** (McAllister 2026, preprint), while other ESN studies disagree on whether hubs matter (Yan 2025 vs Takahashi 2025). So "degree predicts importance" is model- and task-dependent in the literature, and H-A must say which regime it addresses.
7. **Connectivity alone underdetermines function when biophysical parameters are free** (Beiran and Litwin-Kumar, theory, preprint; Karaneen 2026 preprint; Randi 2023 in C. elegans for real data).

### 3.2 Open (our opportunities, with pre-emption risk)

| Hypothesis | Status | Closest prior art | Risk |
|---|---|---|---|
| **H-A (ladder)** | Open at peer-reviewed level. The specific ladder (global centrality, then source-to-target flow, then operating-point linear response (I - DW)^-1) has not been tested on single-neuron necessity in the Shiu model, to my search. | **StrokeSim (grey)**: static paths 0.70 vs activity-weighted 0.81 Spearman on 21 active neurons (one circuit, no named centrality baselines). Therianos 2026 (larval rate model) asks the sufficiency-of-compressions question. McAllister 2026 (ESN) opposes the "centrality is poor" premise. | **Medium to high** for the "structure plus activity beats structure" sub-claim. Low for centrality baselines. |
| **H-B (threshold margin theory)** | Open. Shiu's "any rate" rule and An 2026's state-dependence are indirect support. No margin-based theory found. | An 2026 (edges), Shiu 1F rule. | **Low** on theory; check Li 2026 hub-inhibition work for related ideas. |
| **H-C (neural epistasis, pairs)** | Open for neurons in a whole-brain LIF model at scale. | StrokeSim 21 pair conditions on 6 cells; flymsg DNp01 plus DNp02/06; Bacik 2016 (C. elegans, structural double ablation); Cowley 2024 (behavioural combinations); Pospisil 2024 (effectome says circuits largely independent). | **Low to medium** (grey work is tiny and not framed as epistasis). Real-fly combinatorial silencing literature was **not searched** (budget). |
| **H-D (task specificity)** | Partly done at the activation level: Shiu bioRxiv abstract states sugar and water form a partially shared pathway, confirmed by imaging and behaviour. Necessity-level overlap is unknown; the Shiu repo ran both silencing screens. | Shiu 2023/2024; An 2026 (task-dependent cliffs); escape vs feeding preprint. | **Medium**: if the Nature paper compares the two silencing lists, H-D is partly pre-empted. Verify in full text. |
| **H-E (external validity)** | Open and the strongest hook for a paper. | Pugliese (replication across 4 connectomes), Ceballos and Sapkal (model-then-experiment), Randi (C. elegans benchmark). | The risk is that no published named-neuron necessity labels match the top-200 screens. That is the ground-truth agent's job. |

### 3.3 Specific implications for the design

1. **Circularity check**: Copy the null models used in the literature (degree-preserving rewiring with sign preservation; weight shuffle; the "frozen operator" ensemble of Therianos) so that "structure predicts necessity" is compared to a rewired-structure baseline, not to chance.
2. **Baseline activity**: Because the model has no baseline, the Shiu 1F/4C/5D screens already restrict to neurons that fire under drive. Our activity baseline must be defined on the same population and must be reported alongside structure.
3. **Silencing semantics**: Decide explicitly between "no output" (Shiu code) and "no input and output" (Shiu README). The two differ for readouts on the silenced neuron.
4. **Sign errors**: sign is neuron-level and derived from predicted transmitters (Eckstein: 87%/94% six-way accuracy). A sign-flip robustness check is a cheap addition that no source I found has done on the Shiu model (partly searched; see §0.3).
5. **Connectome variability**: Schlegel reports that one in six cell types differs in count between hemispheres and one in three across brains, with weight variability above technical noise [V-abs, ws]. Left-right homolog replication should be type-matched and weight-restricted to stronger edges (Pedigo, ws).
6. **ID drift**: re-map neuron IDs for v783 (the right MN9 ID in the notebook is missing).

---

## 4. Unconfirmed leads

| Lead | What I could and could not confirm | Status |
|---|---|---|
| "91% prediction accuracy across 164 experimental predictions" for the Shiu model | Appears in the Eon README, the Eon blog, and (per ws) the State of Brain Emulation Report 2025 (arXiv 2510.15745; authors per ws: Zanichelli, Schons, Freeman, Shiu, Arkhipov). I never saw it in the Nature abstract or paper text, and the Eon sources themselves describe the figure inconsistently. A news item cites "95%" for a later Eon demonstration. | **Unconfirmed. Do not cite.** |
| Shiu calibration: "100 Hz sugar GRN drive gives about 80% of maximal MN9 firing" | Secondary only (ws). Not in the code. | Unconfirmed |
| Shiu's own shuffled-connectome control ("shuffled weights, same global distribution") | Secondary (ws). | Unconfirmed |
| "Silencing criterion MN9 at or below 80% of control at any of 8 sugar rates"; "39 water-responsive neurons also sufficient for MN9" | ws paraphrase of the paper. Consistent with the notebook (8 rates in Fig 1F) but the 80% threshold and the 39 count are not in the code I read. | Unconfirmed (plausible) |
| Hemibrain "excludes the SEZ" | Only indirect: "SEZ and optic-lobe annotations largely absent from the hemibrain" (ws) plus subvolume scope. No explicit statement. | Indirect only |
| BANC coverage of SEZ, gustatory GRNs, MN9 | Search refused (budget). Nature 2026 and preprint title seen; coverage details not seen. | **Not checked** |
| Male CNS: official annotation of SEZ/MN9 | Only via third-party READMEs. | Not checked |
| FANC (Phelps et al. 2021) | Appeared only as a cited predecessor; no record retrieved. | **Not confirmed** |
| Beiran and Litwin-Kumar journal version (Nature Neuroscience 2025 suggested by my query) | Only the 2024 bioRxiv version found. | Unconfirmed as published |
| McAllister: the Cambridge talk abstract describes the larval connectome; the bioRxiv abstract does not say larva or adult | Possible mismatch of datasets. | Check full text |
| Sapkal 2024 "uses the Shiu LIF model" | Secondary (State of Brain Emulation Report via ws); abstract says "connectome-informed network models"; Shiu is a coauthor. | Probable, not read |
| Sapkal et al., a 2026 bioRxiv on a different walking CPG (mentioned in a Transmitter article snippet) | Not retrieved. | Unconfirmed |
| "Mechanistic bridges from receptors to whole-brain dynamics: mean-field reductions, validity domains, and computational trade-offs", arXiv 2608.00306 | Appeared in two result lists; per ws it contains a remark that the Shiu model's dimensionality makes parameter exploration hard. I never saw its abstract. | Unconfirmed |
| Eon peer-reviewed paper | None found. The "Nature 2026" mentions in the Eon repo CLI (`--run-label nature_2026_07`) are a label for a benchmark suite, not evidence of a paper. | No paper known |
| Connectome-variability impacts on simulated function | No study found; search partly covered. | Open (weak absence) |
| Real-fly combinatorial silencing or neuron-pair interaction studies (for H-C external validity) | Search refused. | **Not searched** |
| Proofreading-error / weight-noise sensitivity of LIF connectome models | Only the StrokeSim README (weight noise, 10 seeds, lognormal) and An 2026 (edge operators). Search refused. | Weak absence |
| Zhang et al.: whether any model in the paper is the Shiu LIF | Not stated in what I saw. | Unconfirmed |
| `flycns`, `flybrain` (PyPI), `IONOFIELD/FLYCNS`, `lixiang1076/fly-brain` | Seen as search titles only; not inspected. | Unreviewed |

---

## 5. Query log

### 5.1 Consensus (`mcp__Consensus__search`)

| # | Query | Outcome |
|---|---|---|
| C1 | Drosophila whole-brain computational model connectome leaky integrate-and-fire sensorimotor processing | rate limited, no result |
| C2 | Network structure governs Drosophila brain functionality | ok |
| C3 | A Drosophila computational brain model reveals sensorimotor processing | ok |
| C4 | connectome-based echo state network neuron importance degree robustness to neuron loss Drosophila | rate limited |
| C5 | connectome-based echo state network neuron importance degree robustness to neuron loss | ok |
| C6 | Beiran Litwin-Kumar prediction identifiability connectome-constrained recurrent neural networks | ok |
| C7 | spiking neural network simulation of the whole Drosophila connectome FlyWire in silico neuron silencing | ok |
| C8 | Connectome-constrained modeling identifies neurons and synapses that sustain spontaneous activity in Drosophila | ok |
| C9 | Connectome-driven neural inventory of a complete visual system / optic lobe FlyWire Matsliah | rate limited |
| C10 | Whole-brain annotation and multi-connectome cell typing of Drosophila Schlegel | free quota exhausted, no result |
| C11 | Synaptic transmitter identity prediction from electron microscopy Drosophila connectome Eckstein | rate limited |

### 5.2 WebSearch

| # | Query (abbreviated where long) | Mode |
|---|---|---|
| W1 | Shiu Drosophila computational brain model reveals sensorimotor processing Nature 2024 leaky integrate-and-fire | standard |
| W2 | Shiu 2024 Nature Drosophila brain model silencing MN9 proboscis extension validation optogenetic "Shiu" PMC11446845 results | standard |
| W3 | McAllister 2026 bioRxiv connectome echo state network Drosophila neuron importance degree | standard |
| W4 | Pospisil effectome "The fly connectome reveals a path to the effectome" Nature 2024 | standard |
| W5 | Lappalainen "Connectome-constrained networks predict neural activity across the fly visual system" Nature 2024 | standard |
| W6 | Sapkal "Neural circuit mechanisms underlying context-specific halting in Drosophila" Nature 2024 | standard |
| W7 | Braun "Descending networks transform command signals into population motor control" Nature 2024 | standard |
| W8 | Eon Systems fruit fly whole-brain emulation embodied connectome Drosophila 2026 | extended |
| W9 | GPU PyTorch re-implementation Shiu Drosophila whole-brain leaky integrate-and-fire connectome model github | standard |
| W10 | Eon Systems github fly brain model Shiu NeuroMechFly embodied emulation code repository | standard |
| W11 | "How sparse can a fly-brain model be" function-preserving compression Drosophila connectome Shiu An bioRxiv | standard |
| W12 | Shiu 2024 Drosophila brain model accuracy "91%" predicted neurons sugar water gustatory ... | standard |
| W13 | Shiu Nature 2024 computational model fly brain "silencing" individual neurons top 200 MN9 ... Ir94e bitter | extended |
| W14 | State of Brain Emulation Report 2025 Drosophila Shiu 164 predictions 91% accuracy leaky integrate-and-fire | standard |
| W15 | Schlegel "Whole-brain annotation and multi-connectome cell typing of Drosophila" Nature 2024 | standard |
| W16 | Eckstein "Neurotransmitter classification from electron microscopy images at synaptic sites in Drosophila melanogaster" Cell 2024 | standard |
| W17 | Matsliah "Neuronal parts list and wiring diagram for a visual system" Nature 2024 | standard |
| W18 | Lin "Network statistics of the whole-brain connectome of Drosophila" Nature 2024 rich club published | standard |
| W19 | BANC brain and nerve cord connectome Drosophila female whole central nervous system bioRxiv Bates | standard |
| W20 | male central nervous system connectome Drosophila Janelia MaleCNS brain and ventral nerve cord neurons synapses | extended |
| W21 | hemibrain connectome excludes subesophageal zone SEZ gustatory feeding circuits FlyWire proboscis motor neurons | standard |
| W22 | MANC (Takemura) and FANC (Phelps) title query | standard |
| W23 | Pugliese "Connectome simulations identify a central pattern generator circuit for fly walking" bioRxiv 2026 Shiu model ventral nerve cord | standard |
| W24 | "Shiu et al." leaky integrate-and-fire whole-brain Drosophila model used to predict circuit activation neurons 2025 bioRxiv ... | extended |
| W25 | critique limitations of connectome-based whole-brain spiking model fly: neurotransmitter sign errors, synaptic weight scaling, sensitivity analysis Shiu model | extended |
| W26 | "Whole-brain connectomics of Drosophila reveals a robust" inhibitory architecture predator evasion bioRxiv December 2025 | standard |
| W27 | Shiu model extended pairwise neuron silencing combinations synergy redundancy in silico fly brain connectome double knockout | extended |
| W28 | Randi Sharma Dvali Leifer "Neural signal propagation atlas of Caenorhabditis elegans" Nature 2023 | standard |
| W29 | Beiran Litwin-Kumar "Prediction of neural activity in connectome-constrained recurrent networks" Nature Neuroscience 2025 | standard |
| W30 | Zhang "Network structure governs Drosophila brain functionality" arXiv 2404.17128 reconnect rate Shiu comparison ... | standard |
| W31 | individual variability connectome Drosophila left-right hemisphere comparison FlyWire hemibrain synaptic weights across animals ... | extended |
| W32 | in silico lesion neuron ablation Drosophila connectome simulation network centrality predicts functional importance hubs vulnerability | extended |
| W33 | "The Drosophila connectome reveals axo-axonic synapses on descending neurons" iScience 2026 leaky integrate-and-fire ... | standard |
| W34 | "Flow-Based Network Analysis of the Caenorhabditis elegans Connectome" Walker PLoS Computational Biology 2016 single and double neuron ablations | standard (the "Walker" author was wrong in my query; the result gave Bacik et al.) |
| W35 | Corradini "A Complex Network-Based Approach for Detecting and Characterizing Power Neurons in Drosophila" Neuroinformatics 2026 | standard |
| W36 | A Drosophila computational brain model reveals sensorimotor processing silencing candidate neurons reduced MN9 firing ... (domain filter: ncbi, biorxiv, nature, pmc) | extended |
| W37 | "From Sensory Detection to Motor Action: The Comprehensive Drosophila Taste-Feeding Connectome" bioRxiv 2025 | standard |
| W38 | Eon Systems fruit fly embodied brain emulation March 2026 blog update behaviors accuracy methodology ... (domain filter: eon.systems, the-decoder.com, theregister.com) | standard |
| W39 | Vaxenburg "Whole-body physics simulation of fruit fly locomotion" Nature 2025 flybody | standard |
| W40 | Sapkal Bidaye halting Drosophila "connectome" "computational model" Shiu leaky integrate-and-fire ... | standard |
| W41 | combinatorial silencing of multiple neuron types Drosophila behavior redundancy parallel pathways ... | **refused, search budget exhausted** |
| W42 | BANC connectome subesophageal zone gustatory sensory neurons proboscis motor neurons ... "Distributed control circuits" | **refused, search budget exhausted** |
| W43 | Drosophila connectome-constrained spiking model sensitivity to synaptic weight noise connectome proofreading errors ... | **refused, search budget exhausted** |

### 5.3 Local / repository work (not literature search)

- Read `/home/user/fly_or_fail/management/STRATEGY.md`.
- Read `/home/user/external/Drosophila_brain_model/{Readme.md, model.py, utils.py, example.ipynb, figures.ipynb}`; counted rows, signs and minimum weights in the two connectivity parquet files and checked MN9 IDs in the completeness CSVs with pandas (in a throwaway venv in the scratchpad; read-only analysis, no simulation).
- Listed (not unpickled) `sez_neurons.pickle` with `pickletools`: its first key is `aDT6`; the full list of cell-type groups was not enumerated.
- `git clone --depth 1` (scratchpad `.../scratchpad/clones/`), treated as untrusted, nothing executed: `eonsystemspbc/fly-brain`, `Kisame76/drosophila-brain-mlx`, `UditAkhourii/StrokeSim`, `gianlucamazza/flymsg`. Read READMEs and two short scripts (`StrokeSim/experiments/p1_static_paths.py`, `k5_controls.py` header).
