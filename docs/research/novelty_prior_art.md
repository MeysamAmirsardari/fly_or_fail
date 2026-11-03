# Prior-art and novelty audit (agent NOV)

_Date: 2026-11-03. Scope: seed hypotheses H-A to H-E in `management/STRATEGY.md` §4._

Evidence tags:
- **[V-abs]** means the claim is supported by an abstract or search snippet retrieved in this session. The URL is given.
- **[V-src]** means the claim is supported by code or data inspected in this session.
- **[MEM]** means unverified background knowledge.

"Snippet" means text that the WebSearch tool returned or summarized. It is weaker than an abstract, because the tool paraphrases and can misattribute. Snippet-level claims are marked **[V-abs, snippet]** and must be re-checked against full text before they are used in a deliverable.

---

## 0. Method and coverage limits

**Tools.**
- WebSearch: 44 successful calls by this agent (standard and extended) plus 1 refused for budget, logged in §6.
- `mcp__Consensus__search`: 8 successful calls, 3 rate-limited, and 1 refused because the monthly free quota was used up.
- `git clone` / raw.githubusercontent of public repos.
- Local reading of the Shiu model repo at `/home/user/external/Drosophila_brain_model` (commit `91bdd1e`).

**Hard limits on coverage. Read these before trusting any "no prior art found".**
1. **Abstract or snippet level only.** No full texts were read, because bioRxiv, arXiv, PubMed and publisher sites are blocked. Methods-section details (exact null models, which pairs were tested, intensities) are unknown unless a snippet quoted them.
2. **The search budget ran out before the audit was complete.** WebSearch hit the shared per-turn limit of 200 calls across all agents. Consensus hit its monthly free quota ("resets on December 1"). Queries **not run** as planned:
   - dominator trees / articulation points on connectomes;
   - a Consensus query on stimulus-intensity-dependent redundancy;
   - follow-ups for the full texts of Jacobs et al. 2024, Chen et al. 2025 and arXiv 2610.33881.
3. **Indexing lag.** Consensus indexes preprints with a delay, and WebSearch is US-centric and ranks by popularity. A 2026 preprint with no citations and an unusual title could be missed. Three 2026 items were found only through WebSearch, never through Consensus: arXiv 2610.33881 (24 Oct 2026), the EPFL seminar (June 2026), and the StrokeSim GitHub repo (Oct 2026). That suggests the coverage of very recent work is **patchy**.
4. **Non-peer-reviewed sources** (GitHub repos, a seminar abstract) are reported as precedent, because a reviewer could cite them. They are flagged as such.

**Bottom line on coverage.** For H-B and H-C the very closest work is in Shiu et al. 2024 itself and in **Jacobs et al. 2024 (Cell Reports)**. Both use the same model and both are confirmed. The residual "no prior art found" claims below are about the **specific formal predictors and phenotype decompositions**, not about the phenomena.

---

## 1. Per-hypothesis audit

### What the Shiu repo itself already does [V-src]

From `figures.ipynb`, `model.py` and `Readme.md` in `/home/user/external/Drosophila_brain_model`:

- **Fig. 1F.** Each of the top 200 sugar-responsive neurons is silenced singly at **8 sugar-GRN input rates, 50–120 Hz**, and MN9 rate is read out. The rate range is a stimulus-intensity sweep of single-neuron necessity.
- **Fig. 4c.** The same for water, top 200 neurons at **160–220 Hz** (7 rates).
- **Fig. 5d.** The same for JON neurons, top 300 at **140–180 Hz**, with DN1 and DN2 (aDN) readouts.
- **Fig. 5g / S5.** One **combinatorial** silencing: 3 inhibitory neurons silenced together, with the input rate swept from 20 to 220 Hz.
- **Figs. 3 and 4e.** Two-input interaction maps (sugar×bitter, sugar×Ir94e, sugar×water rate grids). These are interactions between *activations*, not silencings.
- **The `silence()` function zeroes only *outgoing* synapses** (docstring: "setting weights of all synapses from it to 0"). The README says "to and from", so the README and the code disagree. The community `drosophila-brain-mlx` README independently notes the same discrepancy.
- The model has no spontaneous activity. With v_rest = v_reset = −52 mV, v_th = −45 mV and no background input, any neuron that does not fire under the stimulus has zero silencing effect by construction.

---

### H-A: model ladder (centrality < path/flow < operating-point-aware linear response)

**Closest prior art, ranked:**

1. **StrokeSim** (GitHub, U. Akhouri / Lossfunk; commit `b0939f4`, 2026-10-27) [V-src].
   - Runs the Shiu LIF model (v783, with v630 for replication) under sugar drive.
   - Runs a 402-neuron single-knockout screen in the PRW region.
   - Asks "Can wiring (± one intact run) predict the 402-neuron knockout screen?" It reports, for the 21 active neurons, Spearman correlation with effect size of **0.70 for static paths and 0.81 for activity-weighted paths**. It also reports that sign-blind paths rank an inhibitory neuron first.
   - In other words, it ran a small version of the H-A ladder (structure → structure + activity) inside the Shiu model.
   - It is not peer-reviewed, uses one readout (serotonin cells) and n = 21.
2. **Xie, Zhao et al., arXiv 2512.06934 (Dec 2025)**, "Visual Function Profiles via Multi-Path Aggregation…" [V-abs, snippet, https://arxiv.org/abs/2512.06934v1]. Uses adjacency-matrix powers and finite-path aggregation, "grounded in neural network steady-state theory", on the ~140k-neuron FlyWire matrix to predict neuron-level responses (ON/OFF, direction selectivity). This is a linear-response / path-sum predictor applied to FlyWire, but it predicts activity, not necessity.
3. **Pospisil et al. 2024, Nature, "The fly connectome reveals a path to the effectome"** [V-abs, https://consensus.app/papers/details/f6ce203983045abfbfc72df85d2fa9ff/]. Uses a linear dynamical model with the connectome as a prior, and "recovers a linear approximation to the nonlinear dynamics of more biophysically realistic simulations". This is the canonical "linear response of W" reference.
4. **Fletcher & Wennekers 2016, Int J Neural Syst** [V-abs, https://consensus.app/papers/details/ee70388db5d45cdc8dc8ce7603c6ccf6/]. In LIF networks, Katz centrality (a resolvent, (I − αA)⁻¹-type measure) predicts firing rate almost perfectly, while degree, betweenness and PageRank do worse. This is exactly the "centrality < resolvent" step of H-A, but for activity, not necessity.
5. **Ganguly (Columbia), CSGF abstracts 2022–2024**, "Efficient Connectome Analyses for Identifying Bottleneck Neurons in Behaviorally-Relevant Pathways" [V-abs, https://krellinst.org/csgf/conf/2024/abstracts/ganguly2021]. Defines an influence metric over arbitrary-length source→target paths with a path-length gain parameter, and the smallest neuron set carrying a given fraction of influence. Validated on hemibrain sensory→descending pathways. This is the "task-specific s→t path structure" rung, with no simulation-based necessity test.
6. **Yan et al. 2017, Nature (C. elegans network control)** [V-abs, https://consensus.app/papers/details/ee87e57c14d05e0d851c9fbed3e4301d/]. A structural (control-theoretic) predictor of single-neuron necessity, validated by ablation (PDB; DD04/DD05 vs DD02/DD03). This is the strongest "structure predicts necessity" precedent, in a different organism.
7. **Seguin et al. 2023, Nat Rev Neurosci (communication models)** [V-abs, https://consensus.app/papers/details/7d7005a8d4425fe1ab659386b61f9edf/]. A taxonomy of path, diffusion and communicability measures, which is the menu any H-A rung will be judged against.
8. **Li et al. 2026, bioRxiv 10.64898/2026.08.21.745055** [V-abs, https://consensus.app/papers/details/d402f7a05ec7586cb55513877e178ab3/]. A FlyWire-constrained model fit to spontaneous calcium data. Systematic in-silico perturbations find "inhibitory hub neurons… necessary and sufficient" for resting dynamics. A snippet mentions a 73×73 "effectome" of signed loss changes from silencing [V-abs, snippet].

**Overlap.** Every rung of the ladder exists separately: centrality vs LIF activity (Fletcher), path/influence bottlenecks (Ganguly), linear response (Pospisil; Xie), and structure → necessity validated experimentally (Yan). The exact ladder inside the Shiu model has a non-peer-reviewed precedent (StrokeSim).

**Non-overlap.** No peer-reviewed or preprint study was found that systematically ranks global centrality vs s→t flow vs (I − DW)⁻¹-type linear response as predictors of **in-silico single-neuron necessity** in the Shiu FlyWire model across several tasks. The specific claim that "the residual is a measure of threshold nonlinearity" was not found as a stated claim.

**Verdict: INCREMENTAL.**
- That a resolvent beats degree is expected from Fletcher 2016 and from how LIF models work.
- The ladder is a necessary *baseline section*, not a headline contribution.
- It is also partly circular (STRATEGY §3.2), because the model is built from the same W.

**How to sharpen.** Turn the ladder into a falsifiable *validity-domain* claim: "the linear-response predictor fails exactly where pathway neurons sit near threshold, and its error scales with a measurable margin statistic". See Alt-2 in §4. Report against StrokeSim's 0.70/0.81 as a public baseline.

---

### H-B: threshold-margin theory; operating-point-dependent necessity; abolition vs sensitivity shift

**Closest prior art, ranked:**

1. **Shiu et al. 2024, Nature** [V-src for the design; V-abs, snippet for the interpretation; https://www.nature.com/articles/s41586-024-07763-9, PMC11446845].
   - Single-neuron silencing was run at 8 sugar rates (50–120 Hz) [V-src: figures.ipynb; snippet: "sugar-sensing neurons were activated at frequencies ranging from 50 to 120 Hz in 10 Hz increments for silencing"].
   - Silencing phenotype = MN9 ≤ 80% of control "at any of the 8 sugar activation frequencies" [V-abs, snippet]. The authors therefore already treated necessity as intensity-dependent and collapsed it with an "any" rule.
   - One WebSearch summary attributes to this paper the statements "redundancy in the circuit increases as sensory stimulation rises" and "silencing of individual neurons had the greatest effect when sugar GRNs were activated at low frequencies" [V-abs, snippet, weak]. The search result listed nature.com/s41586-024-07763-9 and researchgate; a second search reproduced only the truncated sentence "silencing of individual neurons had the greatest effect when sugar GRNs were active…".
   - **Treat this as likely, not confirmed. It must be checked in the full text.** If it is confirmed, the qualitative core of H-B ("necessity is operating-point dependent; redundancy grows with intensity") is already published.
2. **Jacobs et al. 2024, Cell Reports 43(10):114782**, "Overlap and divergence of neural circuits mediating distinct behavioral responses to sugar" (Devineni lab, per search summary) [V-abs, snippet, https://www.cell.com/cell-reports/fulltext/S2211-1247(24)01133-1; DOAJ https://doaj.org/article/ceaa8d56d34943c2928ff7f7560e0ecf]. Uses the Shiu model. Individual silencing of most second-order neurons leaves Fdg, Foxglove and Bluebell activity unaffected; silencing several at once has stronger effects; "individual neurons are largely redundant, consistent with the negative results observed with experimental silencing". This is redundancy in the same circuit and model. Whether they varied intensity is unknown.
3. **Pharmacological receptor reserve ("spare receptors")** [V-abs, https://litfl.com/ec50-and-spare-receptors/]. Partial receptor loss shifts the dose–response curve rightward (EC50 up) while the maximal response is preserved until the reserve is used up. This is the conceptual twin of H-B's "sensitivity shift vs abolition". A reviewer will spot it, so H-B should **cite it as an analogy and not claim the dichotomy as new**.
4. **An 2026, bioRxiv, "How sparse can a fly-brain model be?"** [V-abs, https://consensus.app/papers/details/1e64a2d47bdf59e0994a132ddd54b9b9/]. In the Shiu model, which edges are needed depends on "task and network state". Failure changes character in the active state: "output over-excites instead of vanishing". This is operating-point dependence of *edge* removal, not of neuron necessity across stimulus intensity.
5. **Yeon et al. (C. elegans thermosensation), chronic vs acute silencing reveals degeneracy** [V-abs, snippet, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7812381/]. Apparent necessity depends on how you perturb.
6. **Barrett, Denève & Machens, "Optimal compensation for neuron loss" (eLife)** [V-abs, snippet, https://elifesciences.org/articles/12454; author names are MEM]. A theory of when networks compensate for loss.

**Overlap.**
- "Necessity depends on stimulus intensity" is already a design feature of Shiu (sweeps plus the "any frequency" rule). It may also be an explicit finding there (snippet, unconfirmed).
- "Individually redundant neurons in the sugar circuit" is a Jacobs 2024 finding.
- "Sensitivity shift vs loss of maximum" is the receptor-reserve concept.

**Non-overlap (no prior art found within the coverage above).**
1. A *quantitative* threshold-margin theory: a per-neuron predictor of the input intensity at which that neuron becomes necessary, built from the contribution δᵢ of neuron i to the downstream drive relative to the margin above threshold.
2. A systematic classification of full silencing dose–response curves into Emax-loss ("abolition") vs EC50-shift ("sensitivity shift"), and *prediction of that class from s→t graph structure* (series cut-vertex vs parallel route).
3. A test of either against fly experiments.

**Verdict: PARTIALLY NOVEL.**
- The phenomenon is **NOT NOVEL** (Shiu sweeps, Jacobs redundancy, pharmacology analogy).
- The structural *prediction* of the phenotype class and of the intensity at which each neuron becomes necessary has **no prior art found** at the coverage stated in §0.

**How to sharpen.** Drop "necessity is operating-point dependent" as a claim, because it is Shiu's premise. Claim instead: *"the s→t vertex connectivity / residual max-flow after removal predicts whether silencing costs Emax or shifts EC50, and the size of the EC50 shift"*. This is falsifiable, and it reuses Shiu's own intensity sweeps as a replication check. See Alt-3.

---

### H-C: neural epistasis (between- vs within-pathway)

**Closest prior art, ranked:**

1. **Jacobs et al. 2024, Cell Reports** [V-abs, snippet, URL above]. In the **Shiu model**, they "tested every single neuron and every pair" of second-order sugar neurons, and combinations of three or more among excitatory neurons only. Simultaneous silencing had stronger effects than single silencing. **This is pairwise and higher-order silencing in the same model and circuit, published in 2024.** It is the most likely referent of the student's "recent work". Unknown from snippets: whether they computed an interaction score with a null model, varied intensity, or related interactions to graph structure.
2. **Towlson & Barabási 2020, Network Neuroscience 4(1)**, "Synthetic ablations in the C. elegans nervous system" (arXiv 1907.11297, 2019) [V-abs, https://consensus.app/papers/details/7a8d69554fda5ec093a65d64b9c5df9d/; PMC7055645].
   - They *explicitly* port synthetic lethality to neurons ("synthetic essential" neurons). Using network control, they predict 58 pairs and 46 triplets that reduce muscle controllability for gentle touch.
   - **The "neural analogue of genetic interactions" framing is therefore taken.**
   - The DOI 10.1162/netn_a_00115 appeared in a search summary [V-abs, snippet] and must be re-verified.
3. **Bacik et al. 2015, PLoS Comput Biol**, "Flow-based network analysis of the C. elegans connectome" [V-abs, https://consensus.app/papers/details/65d4649de6fd54519f491eb5c10ce621/; arXiv 1511.00673]. Evaluates the "full set of single and double neuron ablations" in silico on flow structure and searches for "synergistic pairs… whose simultaneous ablation induces supra-additive disruption" [V-abs, snippet]. This is flow-based pairwise synergy on a connectome, without spiking dynamics or a behavioural readout.
4. **Multi-perturbation Shapley value analysis (MSA).**
   - Keinan et al. 2004, Neural Comput [V-abs, https://consensus.app/papers/details/761821312a9850bb800a618fa7b17c3e/].
   - Zavaglia et al. 2016, Brain Struct Funct, which found "redundant interactions… within each hemisphere, and synergistic interactions between bilateral regions" [V-abs, https://consensus.app/papers/details/f9c3b5817c25560abc107dd95f0a1223/].
   - Fakhar & Hilgetag, PLoS Comput Biol (Consensus lists 2021, WebSearch says 2022) [V-abs, https://consensus.app/papers/details/a375aacc94e354fca415c6cd06ae55ad/].
   - Dixit et al. 2025 arXiv (MSA at LLM scale) [V-abs, https://consensus.app/papers/details/0167c00a17d45ac1915bedf4ef128c65/].
   - Together these give an established formalism for pairwise interaction and synergy/redundancy from multi-lesions. **No application to FlyWire / Shiu was found** (WebSearch extended, Q2).
5. **Chen et al. (authors not confirmed; one summary said "Chen & Xi"), bioRxiv 10.64898/2025.12.14.694122 (Dec 2025)**, "Whole-brain connectomics of Drosophila reveals a robust, distributed architecture for the suppression of feeding during escape" [V-abs, snippet, https://www.biorxiv.org/content/10.64898/2025.12.14.694122v1.full]. A FlyWire v783 LIF model with feeding (MN9) as readout. Silencing any single inhibitor did not restore feeding; silencing two gave only partial recovery, "demonstrating an additive gain". This is pairwise silencing in a Shiu-type model with an explicit additivity statement.
6. **arXiv 2610.33881 (24 Oct 2026)**, "Sensorimotor behaviour from an untrained brain-and-nerve-cord connectome" [V-abs, snippet, https://arxiv.org/html/2610.33881]. A Shiu-parameter model on BANC (172,433 neurons). Silencing cell types together produces drops larger than "the sum of their single falls". This is supra-additive (synergistic) combined silencing in a Shiu-type model, in the olfactory / Kenyon-cell context.
7. **Li et al. 2026 bioRxiv (spontaneous activity)** [V-abs, snippet]. "Silencing one inhibitory hub can release its excitatory partner into runaway activity… co-silencing that partner restores the resting regime". This is a suppressive (rescue) pairwise interaction in a FlyWire-constrained model.
8. **Gross (EPFL seminar, 9 June 2026)**, "From systematic interneuron perturbations to connectome-constrained dynamics" [V-abs, https://memento.epfl.ch/event/from-systematic-interneuron-perturbations-to-conne]. C. elegans, 7 head interneurons silenced singly and in pairs (chemogenetic) with whole-brain imaging; "pairwise silencing reveals structured non-additivity", compared with a connectome-constrained model. This is the experimental and model counterpart of H-C. No preprint was found.
9. **Genetics side.**
   - Kelley & Ideker 2005, Nat Biotechnol: between- vs within-pathway models [V-abs, https://consensus.app/papers/details/20772a364b7f58fdb5a9398ec00caad6/].
   - **Bellay et al. 2011, Genome Res: "most… negative genetic interactions fit the between-pathway model", but "current models for positive genetic interactions fail to explain 80% of the modular structures"** [V-abs, https://consensus.app/papers/details/4e9925ef5efa54438fe74856c3ea9a6c/]. This is a direct warning against the "serial → positive/masking" half of H-C.
   - Phenix et al. 2011, PLoS Comput Biol: a quantitative epistasis model for pathways "responding to an external signal" [V-abs, https://consensus.app/papers/details/b86ad8cd00ec5925806388e7d7bfb9ae/]. This is the closest genetics precedent for signal-dependent epistasis.

**Overlap.**
- Pairwise and higher-order silencing in the Shiu model: Jacobs 2024.
- Additive or supra-additive combined silencing in FlyWire- or BANC-based LIF models: Chen 2025 and arXiv 2610.33881.
- The synthetic-lethality analogy for neurons: Towlson 2020.
- Flow-based pairwise synergy on a connectome: Bacik 2015.
- A formal interaction calculus: MSA.
- Experimental pairwise neural non-additivity: Gross 2026, C. elegans.

**Non-overlap (no prior art found within the coverage).**
1. An **epistasis score with a declared null** (multiplicative / min / additive on a bounded MN9 rate) computed systematically over pairs in the Shiu model.
2. **Prediction of the sign and size of that score from s→t graph structure**, i.e. parallel convergent vs serial, using an inclusion–exclusion of max-flow (Menger) as the predictor.
3. **Dependence of the interaction sign on input intensity.**

**Verdict: INCREMENTAL as stated** (concept and data type both exist). It is **PARTIALLY NOVEL** only if reframed around (2) + (3).

**Technical red flag.** In a thresholded model with no spontaneous activity, "serial pairs show masking" is close to *true by construction*. If silencing A already abolishes the output, AB cannot do worse, so the interaction is positive under a multiplicative null. A reviewer will call this trivial. The informative half is the parallel/synergy half, together with its intensity dependence.

**How to sharpen.** Do not claim "neural epistasis" or "synthetic lethality for neurons" as new (Towlson 2020). Claim instead: *"interaction sign is a predictable function of the operating point. Synergy peaks at intermediate input, where the margin lies between δᵢ and δᵢ + δⱼ, and vanishes at both low input (singles already abolish) and high input (pairs still redundant)."* That is a theory-derived, non-monotonic, falsifiable prediction. See Alt-1.

---

### H-D: task specificity (sugar vs water → MN9; hubs rarely necessary)

**Closest prior art, ranked:**

1. **Shiu et al. 2024** [V-src: figures.ipynb runs top-200 silencing screens for sugar (Fig. 1F) *and* water (Fig. 4c) with the same MN9 readout; V-abs, snippet: the "sugar and water pathways… form a partly shared appetitive feeding initiation" route, supported by calcium imaging and behaviour; for water "nearly all of the tested neurons were predicted to produce water-silencing phenotypes, with the exception of Usnea"]. The two necessity sets for the H-D comparison already exist in Shiu's own analysis. Comparing their overlap by layer is a re-analysis of Shiu Figs. 1F and 4c.
2. **Jacobs et al. 2024 Cell Reports** [V-abs]. Circuits for different sugar-evoked behaviours "are partially overlapping and diverge at the second and third layers". This is the mirror design (shared input, different outputs) and an experimental precedent for the depth-dependent overlap logic.
3. **Sabrin et al. 2020, PLoS Comput Biol, "The hourglass organization of the C. elegans connectome"** [V-abs, https://consensus.app/papers/details/6e06d4ee354a5c2ab0beffc20a0f5457/]. Sensory→motor flow passes through a small "waist". This is a structural theory of where tasks converge.
4. **Lin et al. 2024, Nature, "Network statistics of the whole-brain connectome of Drosophila"** [V-abs, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10402125/]. Defines a rich club (~30% of neurons; degree > 37 in the preprint) and integrator/broadcaster subsets. This is the "global hub" definition H-D would test.
5. **Li et al. 2026 bioRxiv** [V-abs]. Inhibitory hubs are necessary for *spontaneous* dynamics. This is a counterpoint: hubs can be necessary, for a different "task".
6. **StrokeSim** [V-src]. MN9 survives silencing of 49 of 51 regions; only GNG is a single point of failure.

**Overlap.** The data needed already exist in Shiu. Depth-dependent overlap and divergence has experimental precedent (Jacobs) and structural theory (hourglass).

**Non-overlap.** No study was found that quantifies necessity overlap *as a function of synaptic depth* across tasks with a shared output, or that tests "hubs are rarely necessary" against Lin et al.'s rich-club and broadcaster definitions in the Shiu model.

**Verdict: INCREMENTAL.** It is a useful secondary analysis that is cheap because it reuses screens, but it would not carry a paper.

**How to sharpen.** Fold it into Alt-1/Alt-3 as a generalisation test (does the margin/flow predictor transfer from sugar to water and JON tasks?). Also pre-register a rich-club null using the Lin et al. definition.

---

### H-E: external validity (model necessity beats centrality against experiments; L–R and cross-connectome reproducibility)

**Closest prior art, ranked:**

1. **Shiu et al. 2024** [V-abs, snippet, PMC11446845 / researchgate]. In-silico silencing was compared with optogenetic silencing. For water, of the neurons examined, "4 of these 5 neurons did not have a water silencing phenotype, as predicted, although one, Usnea, did significantly decrease proboscis extension when silenced with GtACR1". A secondary review reports "91% accuracy across 164 experimental predictions" [V-abs, snippet, https://arxiv.org/pdf/2510.15745, State of Brain Emulation Report 2025]. That figure covers all prediction types, not silencing specifically.
2. **Yan et al. 2017** [V-abs]. Structure-based (control) necessity predictions were validated experimentally in C. elegans. This is a precedent for "structure predicts biological necessity".
3. **Jacobs et al. 2024** [V-abs, snippet]. Model redundancy was "consistent with the negative results observed with experimental silencing". This is a qualitative comparison of model and experiment, in the same circuit.
4. **Shiu, Sterne et al. 2022, eLife** [V-abs, https://consensus.app/papers/details/5383396b28db5b36be6baf983f3d5ccf/]. "Most neurons in this pathway are necessary and sufficient for proboscis extension". A snippet adds that silencing Rattle and Usnea reduced PER to 100 mM sucrose while silencing other second-order neurons did not [V-abs, snippet, https://elifesciences.org/articles/79887/figures]. This is a ground-truth label source.
5. **Cross-connectome / homolog precedent (non-peer-reviewed)** [V-src].
   - StrokeSim replicated a single-neuron necessity result across FlyWire v630/v783 and the Janelia male CNS, and across left/right twins.
   - `drosophila-brain-mlx` runs the Shiu model on MaleCNS v1.0, and reports that a degree-preserving shuffled connectome leaves MN9 silent.
   - arXiv 2610.33881 runs Shiu parameters on BANC.
   - Cross-connectome execution is therefore technically established, but no systematic necessity-reproducibility study was found.
6. **Randi et al. 2023, Nature (C. elegans signal propagation atlas)** [V-abs, snippet, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10632145/]. Measured perturbation responses depart from connectome predictions, partly because of extrasynaptic signalling. This is a cautionary precedent for H-E: connectome-only models miss neuromodulatory necessity.

**Overlap.** Model vs experiment for silencing was done in Shiu on a small set. Cross-connectome execution of the Shiu model exists in community code.

**Non-overlap.** No study was found that **head-to-head compares in-silico necessity vs graph centrality as predictors of experimentally reported necessity labels**, or that systematically measures L–R or cross-connectome reproducibility of necessity screens.

**Verdict: PARTIALLY NOVEL, but power-limited.**
- The experimental label set for the PER circuit is probably on the order of 10–20 named types. That count is [MEM] and the ground-truth agent must count it.
- With ~5 true positives, "model beats centrality" will rarely reach significance.
- The L–R and cross-connectome reproducibility component is the more defensible novel piece, and it partly breaks the circularity of STRATEGY §3.2.

---

## 2. The "multiple-perturbation interaction" literature (task 3)

**Most likely referent of the student's remark: Jacobs et al. 2024, Cell Reports** (Devineni lab, per search summary). It uses the **Shiu model** to silence every single second-order sugar neuron, every pair, and excitatory triples or larger. It finds that individual silencing barely affects Fdg, Foxglove and Bluebell, that combinations do, and that this matches the negative experimental single-silencing results [V-abs, snippet; https://www.cell.com/cell-reports/fulltext/S2211-1247(24)01133-1]. **This answers STRATEGY §7, open question 1: yes, pairwise and higher-order silencing has been done in the Shiu model.** Unknown: the null model, the intensities, and the structural explanation.

### Computational

| Work | System | What was perturbed | Finding | Tag |
|---|---|---|---|---|
| Jacobs et al. 2024, Cell Rep | Shiu LIF, sugar circuit | all singles, all pairs of 2nd-order sugar neurons; ≥3 (excitatory only) | singles redundant; combos stronger | V-abs, snippet |
| Chen et al. 2025, bioRxiv 10.64898/2025.12.14.694122 | FlyWire v783 LIF | single and double silencing of inhibitors during escape | single: no feeding rescue; double: partial, "additive gain"; "robust, distributed" suppression | V-abs, snippet |
| arXiv 2610.33881 (Oct 2026) | Shiu-parameter LIF on BANC | cell-type output silencing, singly and together | joint drop > sum of single drops (synergy) in KC activation | V-abs, snippet |
| Li et al. 2026, bioRxiv 10.64898/2026.08.21.745055 | FlyWire-constrained model fit to spontaneous Ca²⁺ | systematic neuron and synapse perturbations; 73×73 silencing "effectome" | inhibitory hubs necessary and sufficient; co-silencing a partner rescues a single silencing (suppression) | V-abs (+ snippet) |
| An 2026, bioRxiv | Shiu LIF | edge-removal operators at matched budgets | function depends on placement × strength; task- and state-dependent cliffs | V-abs |
| Towlson & Barabási 2020, Netw Neurosci | C. elegans, network control | all pairs and triples | 58 pairs and 46 triples "synthetic essential" for touch-response controllability | V-abs |
| Bacik et al. 2015, PLoS CB | C. elegans flow structure | all single and double ablations | synergistic (supra-additive) pairs, enriched for interneurons | V-abs (+ snippet) |
| Kim et al. 2016, PLoS CB | C. elegans graph | all single neurons and synapses | 12 critical neurons; "both parallel and serial design elements" | V-abs, https://consensus.app/papers/details/2863cf4e45ff59a6bf088e319387575f/ |
| MSA line (Keinan 2004; Zavaglia 2016; Fakhar & Hilgetag 2021/22; Zavaglia 2024; Dixit 2025) | ANNs, cat lesions, stroke cohorts, LLMs | multi-lesion coalitions | Shapley contributions plus pairwise synergy/redundancy; single lesions are biased (Fakhar) | V-abs |
| StrokeSim (GitHub, Oct 2026) | Shiu LIF v783 | region "strokes", single-neuron screen, "pairwise chain knockouts" | single relay neuron bottleneck; static vs activity-weighted path predictors | V-src (not peer reviewed) |
| Shiu et al. 2024, Fig. 5g/S5 | Shiu LIF, JON | 3 inhibitory neurons silenced jointly across input rates | joint silencing alters aBN1 response (details not read) | V-src (design only) |

### Experimental

| Work | System | Finding | Tag |
|---|---|---|---|
| Gross, EPFL seminar 2026-06-09 | C. elegans, 7 head interneurons, chemogenetic single and pairwise silencing + whole-brain imaging | "structured non-additivity"; two opposing forward/reverse controllers; matched by a connectome-constrained model | V-abs (seminar abstract, no preprint found) |
| Towlson 2020, citing classic ablations | C. elegans | AVA+AVD double ablation abolishes backward movement, unlike either alone; ADF+ASG+ASI+ASJ ablation produces dauers | V-abs, snippet (secondary citation) |
| Syed, Ravbar & Simpson, eLife 2026 (art. 106446) | Drosophila grooming, 13A/13B GABAergic neurons | silencing or activating subsets of 3–6 has marked effects; "redundant inhibition" motif; authors note a lack of reagents for finer combinatorics | V-abs, snippet, https://elifesciences.org/articles/106446 |
| Guo, Zhang & Simpson (descending neurons for anterior grooming) | Drosophila | "partially redundant ways to achieve a behavioral outcome" | V-abs, snippet (venue and year unconfirmed) |
| Jacobs 2024 (experimental arm) | Drosophila sugar circuit | single silencing negative, consistent with model redundancy | V-abs, snippet |
| Sapkal et al. 2024, Nature (halting) | Drosophila | FG or BB silencing does not affect PER | V-abs, snippet, https://www.nature.com/articles/s41586-024-07854-7 |

**Synthesis.**
- Combinatorial silencing in Shiu-type models is now **common practice**: at least 4 independent studies from 2024–2026.
- So far it is used *descriptively* ("redundant", "additive", "supra-additive"). None of the retrieved abstracts reports a formal interaction score with a stated null, a structural predictor of interaction sign, or intensity dependence of the interaction.
- That is the remaining gap, and it is narrow.

---

## 3. Targeted checks (task 4)

**(a) Graph centrality vs in-silico silencing effects in FlyWire / Shiu-type models, 2024–2026.**
- **No peer-reviewed or preprint study found.**
- Precedents found:
  - StrokeSim (GitHub): paths vs activity-weighted paths, Spearman 0.70/0.81, n = 21 [V-src].
  - An 2026: degree-preserving rewiring abolishes output at matched budgets [V-abs].
  - drosophila-brain-mlx: a degree-preserving shuffle silences MN9 [V-src].
  - Fletcher 2016: Katz centrality predicts LIF *activity* [V-abs].
- Coverage: Q9, Q10, Q38, Q43, Q46.

**(b) In-silico necessity as a function of stimulus strength.**
- **Already built into Shiu et al. 2024** [V-src: silencing screens at 8, 7 and 5 input rates for sugar, water and JON], and possibly stated as a result ("redundancy increases as sensory stimulation rises") [V-abs, snippet, weak]. The "any of 8 frequencies" criterion is confirmed at snippet level.
- An 2026 shows network-*state* dependence for edge removal [V-abs].
- No study found that *models* the intensity at which a neuron becomes necessary, or that classifies dose–response phenotypes.

**(c) Interaction or epistasis scores from paired perturbations in connectome models.**
- Pairwise data exist: Jacobs 2024, Chen 2025, arXiv 2610.33881, Li 2026 (fly); Towlson 2020, Bacik 2015 (worm).
- Bacik defines "synergistic pairs" as supra-additive on a structural flow measure.
- MSA provides interaction indices, but no application to FlyWire or Shiu was found.
- **No retrieved abstract defines a genetics-style epistasis score (ε = f_ab − f_a·f_b or similar) in a spiking connectome model.**

**(d) Flow or cut measures on connectomes to predict function.**
- Bacik 2015: flow and double ablations, C. elegans.
- Ganguly CSGF abstracts: s→t influence bottlenecks, hemibrain.
- Varshney 2016: "effective bottleneck capacity… predictive of behavioral speed" in C. elegans [V-abs, https://consensus.app/papers/details/76f26cfa9b3553868a5f6cf0d76d767e/].
- Sabrin 2020: hourglass waist.
- Li 2026, Interdiscip Sci: fast approximate min-cut for virtual node removal in human connectomes [V-abs, https://consensus.app/papers/details/7bc61091a8f558a8984a9d887e242b7d/].
- arXiv 1609.07355: Menger-type connectivity invariants on connectome graphs [V-abs, snippet].
- **No study found that uses s→t max-flow, vertex connectivity or dominators on FlyWire and checks them against simulated or experimental necessity.** The dominator/articulation query could not be run because the budget was exhausted.

**(e) Validation of in-silico necessity against fly experiments beyond Shiu.**
- Jacobs 2024: qualitative agreement with negative single silencing [V-abs, snippet].
- Chen 2025 has a section titled "Computational Predictions Guide Experimental Dissection", but whether experiments were done is unconfirmed [V-abs, snippet].
- An iScience 2026 / bioRxiv 2025.09.04.674108 axo-axonic DN paper validated a model-predicted *activation* effect optogenetically, not silencing [V-abs, snippet, https://www.biorxiv.org/content/10.1101/2025.09.04.674108v3].
- Sapkal 2024 is described as using the model for halting circuits; the extent is not read [V-abs, snippet, secondary].
- **No systematic, quantitative validation of in-silico silencing against a curated experimental label set was found.**

---

## 4. Sharper alternative hypotheses (≤ 3)

All three reuse the Shiu model, the sugar (and water) → MN9 task, and the public FlyWire v630/v783 data. Each is listed with its closest prior art. They are ordered by recommendation.

### Alt-1 (recommended): operating-point-dependent neural interaction ("synergy window")

**Hypothesis.**
- For two individually dispensable neurons i, j on parallel routes converging on thresholded targets, the pairwise interaction ε_ij(r) (on normalised MN9 output, with a pre-declared null, e.g. multiplicative) is a **non-monotonic function of input rate r**.
- ε is ≈ 0 at low r, where the singles already abolish the output. It is strongly negative (synergistic) in a window where the downstream margin lies between max(δᵢ, δⱼ) and δᵢ + δⱼ. It returns towards 0 at high r, where the pair is still redundant.
- The window's location is predicted from structure plus baseline rates, using a margin estimate from a linearised drive. Interaction *sign* (synergy vs suppression) is predicted by route topology: convergent excitatory routes vs routes containing inhibition.

**Why it is sharper.**
- It merges H-B and H-C into one quantitative, falsifiable prediction (a non-monotonic curve) that a "descriptive redundancy" paper does not make.
- It avoids the trivial serial-masking half.

**Closest prior art.**
- Jacobs 2024 (pairs in the Shiu model, apparently at fixed drive).
- Chen 2025 (pairs, "additive gain").
- arXiv 2610.33881 (supra-additive joint silencing).
- Towlson 2020 (neural synthetic lethality, static control theory).
- Zavaglia 2016 / MSA (synergy and redundancy formalism).
- Phenix 2011 (epistasis in signal-responsive pathways).
- Gross 2026 (experimental structured non-additivity).

**Novelty status:** no prior art found for the intensity dependence of interaction sign in neural circuits, at the coverage in §0.

**MVP.** ~20–30 pre-selected neurons (top single-silencing hits plus individually dispensable parallel-route neurons) → ~200–400 pairs × 5–6 rates. Trial counts and runtime to be set by the feasibility agent. Community engines (`drosophila-brain-mlx`) report ~0.29 s per biological second on Apple M4 [V-src]; container runtime is not measured here.

### Alt-2: validity domain of linear-response necessity (sharpened H-A)

**Hypothesis.** A linear-response predictor of single-neuron necessity (an effectome / (I − DW)⁻¹ path sum restricted to the active subnetwork) predicts in-silico necessity well when the pathway operates far above threshold. Its error grows predictably with the fraction of pathway mass carried by neurons near threshold (a "margin index").

**Why it is sharper.** It makes the "remaining gap = nonlinearity" clause of H-A into a measurable, testable scaling claim.

**Closest prior art.**
- Pospisil 2024 (linear approximation of nonlinear sims).
- Fletcher 2016 (Katz centrality ≈ LIF rate).
- Xie et al. 2025, arXiv 2512.06934 (multi-path steady-state predictor on FlyWire).
- StrokeSim (0.70 vs 0.81 static vs activity-weighted paths).
- Ganguly (s→t influence).

**Novelty status:** INCREMENTAL-to-PARTIAL. It is best used as Aim 1 / baseline for Alt-1, not as the headline.

### Alt-3: neural receptor reserve, i.e. predicting the silencing dose–response phenotype class from s→t vertex connectivity (sharpened H-B)

**Hypothesis.**
- In the Shiu model, single-neuron silencing either lowers the maximal MN9 response (Emax loss) or shifts the input–output curve rightward with Emax preserved (EC50 shift).
- Emax-loss neurons are s→t vertex cuts (dominators) of the *active, sign-aware* subgraph.
- EC50-shift neurons are on routes with parallel alternatives. The shift magnitude scales with the fraction of s→t max-flow they carry.

**Why it is sharper.**
- It makes the "phenotype classes" of H-B into a quantitative predictor.
- It can be checked against Shiu's own multi-rate screens (replication).
- It connects to the pharmacological receptor-reserve literature as an explicit analogy, not a hidden one.
- If published PER sucrose dose–response curves under silencing exist (ground-truth agent), it has a path to external validity.

**Closest prior art.**
- Shiu 2024 (multi-rate single silencing; "any-rate" criterion).
- Receptor reserve (litfl).
- Ganguly bottlenecks.
- Bacik 2015 flow ablations.
- Li 2026 Interdiscip Sci min-cut node removal.
- Kim 2016 ("parallel and serial design elements").

**Novelty status:** no prior art found for structural prediction of Emax vs EC50 silencing phenotypes, at the coverage in §0.

**Single strongest recommendation.**
- **Alt-3 as the 5-week MVP** (singles only; bounded compute; reuses Shiu's design).
- **Alt-1 as the paper extension** (pairs × intensity).
- **Drop "neural epistasis" and "necessity is operating-point dependent" as headline novelty claims**, because Towlson 2020, Shiu 2024 and Jacobs 2024 already cover them.
- **Cite Jacobs 2024 prominently** as the direct predecessor.

---

## 5. Unconfirmed leads (must be checked before use)

1. **Shiu 2024's own statements on redundancy vs stimulation.** The exact sentences "redundancy in the circuit increases as sensory stimulation rises" and "silencing of individual neurons had the greatest effect when sugar GRNs were activated at low frequencies" appeared only in a WebSearch summary. **Highest priority to verify (full text, Fig. 1F legend).** If confirmed, H-B's qualitative claim is fully pre-empted.
2. **Jacobs et al. 2024 methods.** Which neurons and pairs, which input rates, whether an interaction null was used, and whether results were related to connectivity. Lab attribution (Devineni) came from a search summary.
3. **Chen et al. 2025 bioRxiv.** Author list unconfirmed. Whether wet-lab tests were done. Exact definition of "additive gain".
4. **arXiv 2610.33881.** Authors; the combined-silencing numbers; whether the analysis is pairwise or larger sets.
5. **Gross (EPFL) C. elegans pairwise silencing.** No preprint found. Check for a 2026 bioRxiv.
6. **Li et al. 2026 bioRxiv.** The first author "Qian-Zhu Li" comes from Consensus metadata. The "73×73 effectome" and co-silencing rescue come from a snippet. Note also a Tübingen thesis lead, "From Connectome to Computation: Predicting Neural Function with Machine Learning" (https://tobias-lib.ub.uni-tuebingen.de/xmlui/handle/10900/176447), content unknown.
7. **arXiv 2606.17745**, "A frozen rate operator from the complete larval connectome: degree and weight govern the gross response, exact wiring governs input routing and mushroom-body modes". Only the title was retrieved. It may be close to H-A/Alt-2 (structure compression vs response). Read the abstract.
8. **Towlson & Barabási DOI** 10.1162/netn_a_00115 (from a search summary). Re-verify.
9. **Fakhar & Hilgetag publication year** (2021 per Consensus vs 2022 per WebSearch).
10. **Guo, Zhang & Simpson** (grooming DN redundancy). Venue and year unconfirmed. Possible PMC12844901.
11. **Sapkal et al. 2024 Nature**: to what extent the halting work used Shiu-model silencing predictions.
12. **Unidentified IDs** seen in results with no title retrieved: bioRxiv 10.64898/2026.10.07.757185; Frontiers in Neuroscience 10.3389/fnins.2026.1911198.
13. **GitHub `topherchris420/lop-nur-twin` PR #143** claims "removing a single excitatory neuron lowers MN9 by at most 16%" (snippet). Not inspected.
14. [MEM] Environment-dependent epistasis (G×G×E) is well documented in yeast and bacterial genetics. It would support Alt-1's framing, but no source was retrieved this session.
15. [MEM] Classic MSA neural-model applications (Keinan et al. on evolved agents; Kaufman et al.). Not retrieved beyond Keinan 2004.

---

## 6. Full query log

WS = WebSearch (std = standard, ext = extended). CONS = Consensus search. RL = rate-limited.

| # | Tool | Query | Key result(s) |
|---|---|---|---|
| 1 | WS-ext | pairwise silencing neurons whole-brain Drosophila connectome LIF model interactions 2025 | Chen 2025 bioRxiv; Li 2026 bioRxiv; State of Brain Emulation 2025 |
| 2 | WS-ext | multi-perturbation Shapley value analysis connectome-constrained model Drosophila FlyWire | no MSA on FlyWire; VAE+SHAP arXiv 2505.13011 (irrelevant) |
| 3 | CONS | combinatorial in silico silencing of neuron pairs in a whole-brain Drosophila connectome model | An 2026; Li 2026; Pospisil 2024; Zhang 2024; Shiu 2024 |
| 4 | CONS | multi-perturbation Shapley value analysis lesion interactions neural network model | RL |
| 5 | CONS | (retry of 4) | Keinan 2004 ×2; Fakhar & Hilgetag; Zavaglia 2016, 2024; Dixit 2025; Ofir-Geva 2022 |
| 6 | WS-std | Chen Xi "Whole-brain connectomics of Drosophila reveals a robust, distributed architecture…" | abstract: disfacilitation via Roundup; FlyWire v783; authors unconfirmed |
| 7 | WS-std | "Connectome-constrained modeling identifies neurons and synapses that sustain spontaneous activity in Drosophila" Li 2026 | Sciety abstract; Tübingen thesis lead |
| 8 | WS-std | Fakhar Hilgetag multi-site lesion analysis optimal influence connectome linear model Shapley 2025 | no 2025 item; PMC9246164 |
| 9 | WS-std | Shiu Drosophila brain model silencing "stimulus intensity" OR "input frequency"… | nothing specific |
| 10 | CONS | graph centrality versus in silico silencing effect in FlyWire whole-brain spiking model | Fletcher 2016; Seguin 2023; An 2026; Dorkenwald 2024 |
| 11 | WS-ext | FlyWire centrality hub neurons in silico ablation LIF predicts behavior 2025 2026 preprint | none; StrokeSim, neurofly, eonsystems repos |
| 12 | WS-std | "Drosophila" connectome "max-flow" OR "min-cut" OR "vertex cut"… | Ganguly CSGF bottleneck abstract |
| 13 | CONS | max-flow min-cut analysis of connectome to identify bottleneck neurons | Li 2026 Interdiscip Sci; Bacik 2015; Sabrin 2020; Varshney 2016; Kim 2016; Franconville 2018 |
| 14 | CONS | network control principles predict neuron function C. elegans connectome ablation | Yan 2017; **Towlson 2019/2020**; Towlson 2018 FAQ; Uzel 2022 |
| 15 | CONS | epistasis between neurons double ablation genetic interaction analogy nervous system | RL |
| 16 | WS-ext | "neural epistasis" OR "epistasis between neurons" OR "synthetic lethality" neurons combinatorial silencing… | no named concept; circuit redundancy review |
| 17 | WS-std | Ganguly bottleneck neurons connectome influence metric hemibrain… | CSGF 2022/23/24 abstracts |
| 18 | WS-ext | linear response approximation predicts silencing effects spiking connectome model Drosophila effectome perturbation 2025 | Li 2026 effectome/co-silencing snippet; arXiv 2606.17745; arXiv 2512.06934 |
| 19 | CONS | (retry of 15) | Towlson 2020; Domingo 2019; Costanzo 2016; Phillips 2008 |
| 20 | WS-std | "frozen rate operator" larval connectome arXiv 2606.17745 | title only |
| 21 | WS-std | "Visual Function Profiles via Multi-Path Aggregation" Drosophila arXiv 2512.06934 | Xie, Zhao et al., Dec 2025 |
| 22 | CONS | Kelley Ideker systematic interpretation of genetic interactions between-pathway within-pathway models | Kelley 2005; Ulitsky 2007; **Bellay 2011**; Phenix 2011; Zinovyev 2013; Yu 2025; Garcia 2026 |
| 23 | WS-ext | Drosophila proboscis extension sugar circuit silencing combinations redundant interneurons… | Shiu redundancy snippet; Sapkal 2024; Jacobs 2024 |
| 24 | WS-ext | connectome model prediction validated experimentally neuron required silencing Drosophila 2025 Shiu model follow-up behavior | 91%/164 (secondary); Chen 2025; axo-axonic DN paper |
| 25 | CONS | sugar sensing gustatory second-order neurons required for proboscis extension Drosophila connectome | RL |
| 26 | WS-std | Shiu "redundancy" sugar GRN "low frequencies" silencing computational model MN9 Nature 2024 | nothing (irrelevant GRN = gene-network hits) |
| 27 | WS-std | "Overlap and divergence of neural circuits mediating distinct behavioral responses to sugar" silencing | Jacobs 2024 Cell Rep 43(10):114782 |
| 28 | WS-ext | "A Drosophila computational brain model reveals sensorimotor processing" silencing individual neurons greatest effect low frequency redundancy | ≤80% at any of 8 frequencies criterion |
| 29 | CONS | (retry of 25) | Shiu 2022 eLife; Kain 2015; Bohra 2018; others. **Consensus: "1 credit left"** |
| 30 | WS-ext | Shiu 2024 Nature model "sugar GRN" silencing "redundan" stimulation frequency MN9… | 50–120 Hz silencing; Cell Rep (Jacobs) redundancy |
| 31 | WS-std | neuron necessity depends on stimulus strength threshold redundancy silencing "dose-response" neural circuit degeneracy | Yeon (C. elegans degeneracy); Barrett eLife compensation |
| 32 | WS-std | Drosophila sugar water pathways shared neurons MN9 proboscis extension convergence connectome model water GRN silencing | Shiu preprint water screen; Shiu 2022 Rattle/Usnea |
| 33 | WS-ext | Cell Reports Drosophila whole-brain computational model silencing second-order gustatory neurons individually redundant silencing several simultaneously | **Jacobs 2024: all singles + all pairs in Shiu model** |
| 34 | WS-std | C. elegans combinatorial neuron ablation pairs synergistic redundant behavior experimental 2023 2024 2025 | Towlson (synthetic essential; AVA+AVD) |
| 35 | WS-std | Jacobs Devineni 2024 "Overlap and divergence" computational model pairs silencing Fdg Foxglove Bluebell… | nothing |
| 36 | WS-ext | FlyWire Shiu model "silencing" pairs OR "pairwise" OR "combinations" neurons grooming OR walking OR escape OR courtship preprint 2025 2026 | arXiv 2610.33881 (BANC); lop-nur-twin PR |
| 37 | WS-std | arXiv 2610.33881 BANC connectome leaky integrate-and-fire silencing antennal lobe Kenyon cell | not found |
| 38 | WS-std | "Synthetic ablations in the C. elegans nervous system" Towlson Barabasi 2020… | Netw Neurosci 4(1) 2020; DOI in summary |
| 39 | WS-ext | BANC connectome brain and nerve cord spiking model silencing cell types together "more than the sum" 2026 arXiv | arXiv 2610.33881 title and snippets |
| 40 | WS-std | in silico knockout every neuron connectome model compare betweenness PageRank necessity behavior prediction 2025 | **EPFL seminar (Gross) pairwise silencing**; Fletcher; Yan |
| 41 | WS-std | "From systematic interneuron perturbations to connectome-constrained dynamics" C. elegans pairwise silencing non-additivity | seminar details; Creamer/Leifer/Pillow bioRxiv |
| 42 | WS-std | biorxiv 2026.10.07.757185 | not found |
| 43 | WS-std | Drosophila combinatorial silencing redundant neurons behavior double silencing descending neurons grooming parallel pathways experiment | Syed et al. eLife 2026; Guo/Zhang/Simpson |
| 44 | WS-std | Randi Leifer "Neural signal propagation atlas of Caenorhabditis elegans"… | Randi 2023 Nature |
| 45 | WS-ext | linear rate model approximation of Shiu leaky integrate-and-fire Drosophila whole-brain model comparison graph propagation predicts activated neurons | none; drosophila-brain-mlx |
| 46 | WS-std | "connectome" "information flow" model FlyWire "percolation" OR "signal cascade"… | arXiv 2412.13202; Winding larval cascade |
| 47 | WS-std | FlyWire rich club hub neurons "Network statistics of the whole-brain connectome of Drosophila" Lin 2024… | Lin 2024 rich club / integrators / broadcasters |
| 48 | WS-ext | whole-brain fly model perturbation screen hub neurons silencing has little effect task-specific neurons necessary 2026 | Li 2026; Frontiers fnins.2026.1911198 (unidentified) |
| 49 | WS-std | frontiersin.org fnins.2026.1911198 Drosophila connectome | not found |
| 50 | WS-std | receptor reserve spare receptors partial loss rightward shift EC50 maximal response preserved… | litfl receptor reserve |
| 51 | WS-std | lesion deficit depends on input strength spiking network model silencing effect stronger at weak stimulus compensation parallel pathways | nothing direct |
| 52 | WS-std | Shapley value multi-lesion C. elegans connectome model neurons contributions interactions synergy redundancy | Bacik synergistic pairs; Rabinowitch 2024 iScience |
| 53 | WS-ext | "computational model" Shiu et al. 2024 predicted neurons required experimentally confirmed silencing Drosophila 2025… | Shiu water validation 4/5, Usnea |
| 54 | WS-std | left-right homologous neurons reproducibility in silico perturbation connectome model FlyWire hemibrain male CNS… | none; FlyWire L/R inversion caveat |
| 55 | WS-std | vertex-disjoint paths Menger redundancy neural circuit connectome robustness neuron removal predicts function | Kim 2016; Bacik; arXiv 1609.07355 |
| 56 | WS-std | dominator tree OR articulation points connectome sensory to motor necessary neurons graph Drosophila OR C. elegans | **not run: shared WebSearch budget exhausted** |
| 57 | CONS | neuron silencing effect depends on stimulus intensity redundancy parallel pathways threshold network model | **refused: Consensus monthly quota exhausted (resets 1 December)** |

**Source and code inspections [V-src].**
- `/home/user/external/Drosophila_brain_model`: `figures.ipynb` (all cells), `model.py` (`default_params`, `silence()`), `Readme.md`.
- `Kisame76/drosophila-brain-mlx` README via raw.githubusercontent, plus GitHub API metadata.
- `UditAkhourii/StrokeSim`: shallow clone at commit `b0939f4` (2026-10-27) in `/tmp/claude-0/-home-user-fly-or-fail/27fea6bb-f99b-5a22-9d9c-b68b632bd803/scratchpad/clones/StrokeSim`. The README was read. No code was run.

**Per-hypothesis search coverage** (query numbers above).
- H-A: 2, 10, 11, 18, 21, 40, 45, 46 (+ source inspection).
- H-B: 9, 23, 26, 28, 30, 31, 50, 51 (57 refused).
- H-C: 1, 2, 3, 5, 14, 16, 19, 22, 33, 34, 36, 38, 39, 41, 43, 52, 55.
- H-D: 23, 27, 32, 33, 47, 48.
- H-E: 24, 29, 44, 53, 54, 14 (Yan).
