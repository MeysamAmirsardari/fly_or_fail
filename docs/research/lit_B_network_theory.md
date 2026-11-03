# LIT-B: Network-science and theoretical foundations for structure → perturbation consequences

_Agent LIT-B (Sonnet 5.5, high effort). Written 2026-11-03. Scope: Drosophila-agnostic network theory. Companion reports: LIT-A (fly models), LIT-C (ground truth), NOV (novelty)._

---

## 0. Scope and search coverage limits

**Evidence tags** (all claims about a paper's content carry one):

| Tag | Meaning |
|---|---|
| `[V-abs·C]` | Supported by the verbatim abstract returned by the Consensus index (`mcp__Consensus__search`) in this session. The URL is the Consensus record. |
| `[V-abs·W]` | Supported by a `WebSearch` result in this session. **Caveat:** WebSearch returns a server-side synthesised summary of the pages it found, not a verbatim abstract, so paraphrases and details (including DOIs) are weaker evidence than `·C`. Items resting only on `·W` should be re-checked by the citation auditor against the primary page. |
| `[V-src]` | Supported by primary code or data inspected in this session (cloned GitHub repos, read locally). |
| `[MEM]` | Background knowledge, not confirmed this session. Allowed but must be confirmed before final use. |
| "ours" | A derivation or design suggestion by LIT-B, not a literature claim. |

**Tools actually used.** `WebSearch` (78 queries: 72 standard, 6 extended), `mcp__Consensus__search` (17 calls, of which 9 were rate-limited and returned nothing; the Consensus quota then showed "1 credit left this month; resets December 1", so the last third of the work used WebSearch only), and two shallow `git clone`s of public GitHub repos into the scratchpad (`kuffmode/msa`, `danilo-lazovic/fly-bottlenecks`). Both were read as untrusted data and **no code from them was run**. WebFetch, curl to publishers, PubMed and similar were not used (blocked).

**Coverage limits (read before relying on absence-of-evidence statements).**

1. No full texts were read. Every statement about a paper's content rests on an abstract or on a search-tool summary. Methods details, effect sizes, and figures are therefore mostly unknown to us.
2. "We found no paper that does X" means "the searches listed in §5 did not surface one". It does not mean that none exists. The strongest negatives (no peer-reviewed threshold-margin theory, no between/within-pathway pair framing on LIF models) rest on 2–3 extended queries each.
3. DOIs are recorded only where a search result displayed one; they are marked "(displayed)". Several were displayed inside a WebSearch synthesis. None was written from memory.
4. Two Consensus records have internal inconsistencies, flagged in the entries: François et al. 2025 (first author "Paul François" but copyright line "Fuentes Valenzuela et al.") and Jonas & Kording (Consensus says 2016; journal volume year is believed to be 2017 `[MEM]`).
5. Theme 5 (max-flow/vertex cuts in connectomes) was searched hardest, because it is the crucial one. It turned up a **directly relevant public repo** (§1, entry 5.12) that should be read by NOV and the PI before H-A and H-C are framed.

---

## 1. Annotated bibliography

Relevance codes: **H-A** model ladder, **H-B** threshold-margin theory, **H-C** neural epistasis, **H-D** task specificity, **H-E** external validity. "Stance" refers to STRATEGY §3.

### Theme 1. Lesion modelling on connectomes; structural predictors of lesion impact

**1.1 Honey CJ, Sporns O (2008). Dynamical consequences of lesions in cortical networks. *Human Brain Mapping* 29(7):802–809. DOI 10.1002/hbm.20579 (displayed).** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6870962
- Two simplified oscillatory cortical models on macaque connectivity; individual regions were removed in turn. Lesions of parietal and frontal regions had the greatest potential to disrupt integrative function; the authors note that in vivo lesion effects depend on local circuitry. `[V-abs·W]`
- Relevance: the earliest "remove a node in a dynamical model on a real connectome" template. Centrality/hub-ness predicts impact, partially. **H-A** (global centrality baseline), **H-E**.

**1.2 Alstott J, Breakspear M, Hagmann P, Cammoun L, Sporns O (2009). Modeling the impact of lesions in the human brain. *PLoS Computational Biology* 5(6):e1000408. DOI 10.1371/journal.pcbi.1000408 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2688028/
- Large-scale model on a human structural connectome; sequential single-node deletions and localised area removal; effects measured on functional connectivity. Effect size tracked lesion location and was *partly* predicted by structural properties of the lesioned node; removing highly central nodes disrupted interactions much more than peripheral ones; midline/temporo-parietal lesions had widespread effects, primary sensory/motor lesions more local effects. `[V-abs·W]`
- Relevance: canonical "structure partially predicts lesion impact" result; sets the baseline we must beat. Its outcome is global FC change, not a specified source→target task output (**H-A, H-D** contrast). Circularity caveat (stance 2): the dynamics are built on the same W.

**1.3 Kaiser M, Hilgetag CC (2004). Edge vulnerability in neural and metabolic networks. *Biological Cybernetics* 90:311–317. DOI 10.1007/s00422-004-0479-1 (displayed). arXiv q-bio/0403015.** URL: https://arxiv.org/abs/q-bio/0403015
- Compared several edge-ranking measures on biological and benchmark networks; *edge frequency in all shortest paths* correlated best with vulnerability and singled out inter-cluster connections in biological networks (not in random or scale-free benchmarks). `[V-abs·W]`
- Relevance: an early "path-based predictor beats degree-type predictor" result. Edge-level, structural vulnerability only (no dynamics). **H-A** (path structure vs global hub centrality).

**1.4 Kaiser M, Martin R, Andras P, Young MP (2007). Simulation of robustness against lesions of cortical networks. *European Journal of Neuroscience* 25(10):3185–3192. DOI 10.1111/j.1460-9568.2007.05574.x (displayed).** URL: https://arxiv.org/abs/0704.0392
- Cat and macaque cortical networks vs random, small-world, scale-free and rewired benchmarks, node and connection removal. Decay resembled scale-free networks; hubs and bottleneck connections give a structural basis for conditional robustness. `[V-abs·W]`
- Relevance: example of benchmarking against rewired nulls (theme 7); structural (not dynamic) lesions. **H-A**.

**1.5 Aerts H, Fias W, Caeyenberghs K, Marinazzo D (2016). Brain networks under attack: robustness properties and the impact of lesions. *Brain* 139(12):3063–3083. DOI 10.1093/brain/aww194 (displayed).** URL: https://acuresearchbank.acu.edu.au/item/887yx/brain-networks-under-attack-robustness-properties-and-the-impact-of-lesions
- Review: human brain networks appear resilient to different lesion types compared with random or scale-free networks; lesions change global topology wherever they fall, but the direction of change is unclear. `[V-abs·W]` (abstract-level only)
- Relevance: review entry point for structural-lesion literature. **H-A**.

**1.6 Yan G, Vértes PE, Towlson EK, Chew YL, Walker DS, Schafer WR, Barabási A-L (2017). Network control principles predict neuron function in the *Caenorhabditis elegans* connectome. *Nature* 550(7677):519–523. DOI 10.1038/nature24056 (displayed).** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC5710776
- Structural-controllability analysis of the worm connectome predicted that muscle/motor-neuron control needs 12 neuron classes including a previously uncharacterised neuron (PDB); laser ablation supported the PDB prediction and subset predictions within the DD class (DD04/DD05 ablations affect posterior movement; DD02/DD03 do not); predictions reported robust to weak-connection deletion, missing and rewired connections. `[V-abs·W]`
- Relevance: **the template for H-E** ("structure-derived prediction of neuron necessity, validated by ablation"). Also the cautionary tale: see 1.7.

**1.7 Tu C, et al. (2018). Warnings and caveats in brain controllability. *NeuroImage* 176:83–91. DOI 10.1016/j.neuroimage.2018.04.010 (displayed). arXiv 1705.08261.** URL: https://arxiv.org/abs/1705.08261v1 *(The search result named only "Tu et al."; Suweis appears as author of the follow-up commentary.)*
- Critique of Gu et al. 2015 brain controllability: no statistical evidence that brain networks are controllable from a single node; random null models reproduce the observed controllability–weighted-degree relationship; fMRI resting-state networks cannot be assigned specific control roles. Follow-up exchange: Suweis et al. 2019 "Brain controllability: Not a slam dunk yet" (NeuroImage) and a response by Pasqualetti, Gu & Bassett (titles/venues not verified). `[V-abs·W]`
- Relevance: controllability measures can be reproduced by degree-preserving nulls → every structural predictor needs a null-model control (theme 7). **H-A, H-E**.

**1.8 Liu Y-Y, Slotine J-J, Barabási A-L (2011). Controllability of complex networks. *Nature* 473(7346):167–173.** URL: https://ideas.repec.org/a/nat/nature/v473y2011i7346d10.1038_nature10011.html
- Analytical tools for driver nodes of directed networks; sparse inhomogeneous networks are hardest to control; driver-node count tied to maximum matching (the matching statement is from a secondary wiki note: weak). `[V-abs·W]`
- Relevance: background to Yan 2017; linear-dynamics assumptions (not thresholded spiking). **H-A** (model ladder rung: linear control).

**1.9 Randi F, Sharma AK, Dvali S, Leifer AM (2023). Neural signal propagation atlas of *Caenorhabditis elegans*. *Nature* 623(7986):406–414. DOI 10.1038/s41586-023-06683-4 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10632145/
- Optogenetic activation + whole-brain imaging across ~23,400 neuron pairs: signal propagation differs from anatomy-based predictions; extrasynaptic (peptidergic) signalling contributes; the measured atlas predicts spontaneous dynamics better than anatomy. `[V-abs·W]`
- Relevance: **limits H-E**. In the worm, anatomy is a weak predictor of measured functional influence. Stance 1: model necessity ≠ biological necessity. FlyWire-based models share the "synapses only, no neuromodulation" blind spot.

**1.10 Seguin C, Sporns O, Zalesky A (2023). Brain network communication: concepts, models and applications. *Nature Reviews Neuroscience*.** URL: https://consensus.app/papers/details/7d7005a8d4425fe1ab659386b61f9edf/?utm_source=claude_desktop
- Review challenging the assumption that signalling is only via shortest paths; organises communication models and measures into a taxonomy with pros, cons, and interpretations; applications and recommendations for validation. `[V-abs·C]`
- Relevance: taxonomy of structural "communication" predictors (shortest-path, diffusion, communicability, navigation, ...) to use as the L1–L2 rungs of **H-A**.

**1.11 Seguin C, et al. (2020). Network communication models improve the behavioral and functional predictive utility of the human structural connectome. *Network Neuroscience*.** URL: https://consensus.app/papers/details/c8687ec9ed215270807d91eef55c1db0/?utm_source=claude_desktop *(Consensus displayed first author "Caio Seguin" only.)*
- 889 HCP adults; 15 communication models; communicability and navigation improved behavioural prediction; communication increased structure–function coupling (navigation and shortest-path models gave 35–65% stronger FC association); benefit largest in sparse high-resolution connectomes. `[V-abs·C]`
- Relevance: evidence that non-shortest-path (communicability-type) predictors beat raw connectivity. **H-A**.

**1.12 Seguin C, et al. Communication dynamics in the human connectome shape the cortex-wide propagation of direct electrical stimulation (preprint 2022; Consensus lists copyright 2023 Elsevier; venue believed to be *Neuron* 2023 `[MEM]`/AMiner listing `[V-abs·W]`).** URL: https://consensus.app/papers/details/4161cbb519fe57cd99427ba04a17af5e/?utm_source=claude_desktop
- 29,055 single-pulse stimulations in 550 individuals; network communication models on diffusion-MRI SC explain causal propagation of focal stimuli; a parsimonious structural+functional+spatial model predicted cortex-wide effects with R² = 46% in held-out medical centres. `[V-abs·C]`
- Relevance: gold-standard design for **H-E**: structural predictors of *causal perturbation* effects validated on held-out groups (grouped CV, theme 7). Mixes spatial distance as a confound predictor.

**1.13 Seguin C, Mansour L S, Sporns O, Zalesky A, Calamante F. Network communication models narrow the gap between the modular organization of structural and functional brain networks.** (venue and year not displayed) URL: https://doaj.org/article/679397cb76d4484e9e6e4639a4c59405
- Diffusion-type polysynaptic models, especially communicability, narrow the structural–functional modularity gap by 20–60%, shortest-path routing does not. `[V-abs·W]`
- Relevance: communicability > shortest-path again. **H-A**.

**1.14 Avena-Koenigsberger A, Mišić B, Sporns O (2018). Communication dynamics in complex brain networks. *Nature Reviews Neuroscience* 19:17–33. DOI 10.1038/nrn.2017.149 (displayed).** URL: https://earbmc.sitehost.iu.edu/pubs/Sporns_comm_dynamics_NRN.pdf
- Review framing communication dynamics as the link between structural and functional connectivity. `[V-abs·W]`

**1.15 Avena-Koenigsberger A, Mišić B, Hawkins RXD, Griffa A, Hagmann P, Goñi J, Sporns O (2017). Path ensembles and a tradeoff between communication efficiency and resilience in the human connectome. *Brain Structure and Function* 222(1):603–618.** URL: https://cibm.ch/wp-content/uploads/Avena-Koenigsberger2017_Article_PathEnsemblesAndATradeoffBetwe.pdf
- Uses k-shortest-path ensembles instead of the single shortest path; reports a correlation indicating a trade-off between communication efficiency and resilience of pathways. `[V-abs·W]`
- Relevance: **an explicit path-redundancy measure in brain networks**; the closest network-neuroscience cousin of vertex-disjoint-path counting (theme 5). **H-C**.

**1.16 Estrada E, Hatano N (2008). Communicability in complex networks. *Physical Review E* 77:036111** (Consensus record says 2007, journal "Physical review. E"; the 2008/77/036111 reference is as cited in the 2009 Estrada abstract). URL: https://consensus.app/papers/details/4475dd64ad2e565f9a6584ea9eecc68b/?utm_source=claude_desktop
- New communicability measure, a generalisation of the shortest path; classifies networks by structure–dynamics correlation. `[V-abs·C]` (year discrepancy 2007 vs 2008: unresolved)

**1.17 Estrada E, et al. (2009). Communicability betweenness in complex networks. *Physica A*.** URL: https://consensus.app/papers/details/419d7de567865d9d86b74e36f68bec6e/?utm_source=claude_desktop
- Betweenness that allows all walks with longer walks down-weighted; characterised via the matrix exponential; related to a Fréchet derivative of the matrix exponential, so it **describes network sensitivity to infinitesimal perturbation of a node's edges**. `[V-abs·C]`
- Relevance: a one-line bridge from communicability to "node lesion sensitivity". **H-A**.

**1.18 Estrada E, et al. (2011). The physics of communicability in complex networks. (Consensus lists it as ArXiv, 2011; journal not displayed.)** URL: https://consensus.app/papers/details/d50ea691a002594d805eda57cd8f3cc6/?utm_source=claude_desktop
- Review of communicability functions (exponential, resolvent, hyperbolic) of adjacency or Laplacian; notes routes beyond shortest paths and sparsity-exploiting computation. `[V-abs·C]`

**1.19 De la Cruz Cabrera O, Jin J, Noschese S, Reichel L (2021/2022). Communication in complex networks. arXiv / *Applied Numerical Mathematics* 172:186–205.** URL: https://consensus.app/papers/details/eb2f905d71b85ee18c9bf650bd60314b/?utm_source=claude_desktop (+ Schweitzer M, 2023, arXiv, "Sensitivity of matrix function based network communicability measures", https://consensus.app/papers/details/1c72aa1b1bd35149854485fe25134f9c/?utm_source=claude_desktop)
- Sensitivity of total communicability to changing a single edge weight or adding/removing an edge (directed, weighted); node-removal case in Schweitzer. `[V-abs·C]` (venue of the former from Schweitzer's abstract)
- Relevance: analytic "what happens to communicability if I delete a node/edge" — a structural perturbation-response theory we can reuse for single-neuron predictions (**H-A**).

**1.20 Schlegel P, Bates AS, Stürner T, et al. (2021). Information flow, cell types and stereotypy in a full olfactory connectome. *eLife* 10:e66018.** URL: https://elifesciences.org/articles/66018
- Graph-traversal model assigns neurons to layers by distance from the sensory periphery; hemibrain olfactory neurons (4,732 cells, 966 types) with FAFB comparison; code on GitHub `flyconnectome/hemibrain_olf_data`. `[V-abs·W]`
- Relevance: probabilistic traversal is the standard fly "information-flow" predictor. LIT-A should cover it in depth. **H-A, H-D**.

**1.21 Pointer to LIT-A:** Pospisil DA, Aragon MJ, Dorkenwald S, … Pillow JW (2024). The fly connectome reveals a path to the effectome. *Nature* 634(8032):201–209, DOI 10.1038/s41586-024-07982-0 (displayed). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11446844/ — estimator for a *linear dynamical model* of the fly brain from perturbation data with the connectome as a prior; argues dynamics are a collection of small, largely independent circuits. `[V-abs·W]` Directly relevant to the linear-response rung of **H-A** (theme 6).

### Theme 2. Causal attribution under multiple lesions

**2.1 Keinan A, Sandbank B, Hilgetag CC, Meilijson I, Ruppin E (2004). Fair attribution of functional contribution in artificial and biological networks. *Neural Computation* 16(9):1887–1915. DOI 10.1162/0899766041336387 (displayed).** URL: https://mlanthology.org/neco/2004/keinan2004neco-fair
- Introduces multi-perturbation Shapley value analysis (MSA); axiomatic, scalable; shown on a neurophysiological model and reversible-deactivation data; MATLAB package released. `[V-abs·W]`
- msapy docstring cites this paper's "section 2.3" for the two-dimensional (pairwise) interaction analysis. `[V-src]`
- Relevance: the reference method for **H-C** (pairwise) and for any "single-lesion rankings mislead under redundancy" argument.

**2.2 Keinan A, Hilgetag CC, Meilijson I, Ruppin E (2004). Causal localization of neural function: the Shapley value method. *Neurocomputing* 58–60:215–222. DOI 10.1016/j.neucom.2004.01.046 (displayed).** URL: https://fis.uke.de/portal/en/publications/causal-localization-of-neural-function-the-shapley-value-method(2670252b-36f3-40d6-9401-cc217b536404).html
- Earlier conference-style version; cited by the msapy README as the method's origin. `[V-abs·W]`, `[V-src]` (README citation)

**2.3 Kaufman A, Keinan A, Meilijson I, Kupiec M, Ruppin E (2005). Quantitative analysis of genetic and neuronal multi-perturbation experiments. *PLoS Computational Biology* 1(6):e64. DOI 10.1371/journal.pcbi.0010064 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1289391/
- Applies MSA ("MPA") to yeast DNA-repair multi-knockouts and a *C. elegans* chemotaxis neural circuit; also introduces the functional influence network (FIN) algorithm; a predictor trained on a subset of experiments estimates the rest because the full 2^N set is impractical. `[V-abs·W]`
- Relevance: **the earliest explicit bridge between genetic multi-knockout and neural multi-lesion analysis** (the analogy behind **H-C** is therefore not new). The predictor-from-subset trick is relevant to budgeting.

**2.4 Fakhar K, Hilgetag CC (2022). Systematic perturbation of an artificial neural network: a step towards quantifying causal contributions in the brain. *PLoS Computational Biology* 18(6):e1010250. DOI 10.1371/journal.pcbi.1010250 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9246164/
- Exhaustively lesioned a small ANN playing an arcade game; MSA derives contributions from all multi-element lesion combinations vs single-perturbation analysis (SPA); a key finding: not every perturbation reveals causation. `[V-abs·W]`
- Relevance: ground-truth demonstration that single-lesion rankings and multi-lesion Shapley rankings diverge. **H-A** (what "necessity" means), **H-C**.

**2.5 Fakhar K, Dixit S, Hadaeghi F, Kording KP, Hilgetag CC (2024). Downstream network transformations dissociate neural activity from causal functional contributions. *Scientific Reports* (January 2024).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10808222/ *(journal/year/authors from the WebSearch synthesis; DOI not displayed)*
- Multi-site perturbation framework giving time-varying causal contributions; in toy examples and ANNs, recorded activity may not indicate causal contribution because of downstream transformations. A bioRxiv version is titled "When Neural Activity Fails to Reveal Causal Contributions" (https://www.biorxiv.org/content/10.1101/2023.06.06.543895.full.pdf). `[V-abs·W]`
- Relevance: supports **stance 3** (activity ≠ necessity) and motivates baseline activity as a *predictor to beat*, not a filter.

**2.6 Fakhar K, et al. (2025). A general framework for characterizing optimal communication in brain networks. *eLife*, 17 April 2025. DOI 10.7554/eLife.101780 (displayed).** URL: https://elifesciences.org/articles/101780
- Virtual multi-site lesioning + game theory in models of human brain dynamics yields the exact influence each node has on every other ("optimal influence"); optimal pattern resembles a broadcasting regime using multiple parallel channels; reviewers note model-dependence and weaker fit on directed networks. `[V-abs·W]`
- Relevance: **closest "game-theoretic influence vs structural communication models" paper**; a head-to-head of Shapley influence against communication measures — close to the circularity question of stance 2. **H-A**. First-author/co-author list unresolved (two searches gave "Fakhar and Hilgetag" and "Fakhar et al.").

**2.7 Dixit S, Fakhar K, Hadaeghi F, Mineault P, Kording KP, Hilgetag CC (2025). Who does what in deep learning? Multidimensional game-theoretic attribution of function of neural units. arXiv 2506.19732 (June 2025).** URL: https://arxiv.org/pdf/2506.19732
- MSA for models with multidimensional outputs ("Shapley Modes": contribution maps with the output's dimensionality), applied from MLPs to Mixtral-8x7B and GANs; shows regularisation concentrating computation in a few hubs. `[V-abs·W]` (preprint; authors/title from the arXiv listing in the search result)
- Relevance: methods precedent for a multi-output readout (MN9 plus other motor neurons) in **H-D**.

**2.8 Toba MN, Zavaglia M, Rastelli F, Valabrégue R, Pradat-Diehl P, Valero-Cabré A, Hilgetag CC (2017). Game theoretical mapping of causal interactions underlying visuo-spatial attention in the human brain based on stroke lesions. *Human Brain Mapping* 38(7):3454–3471. DOI 10.1002/HBM.23601 (displayed).** URL: https://hal-u-picardie.archives-ouvertes.fr/hal-03607136
- MSA on 25 right-hemisphere stroke patients to estimate causal contributions *and interactions* of nodes in an attention network. `[V-abs·W]`
- Also: Toba et al. 2020 *Human Brain Mapping* (white-matter bundles, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7336155/) and Toba et al. 2025 *Frontiers in Neuroscience* 19:1409107 (stroke motor deficits; `[V-abs·W]`, whether pairwise interactions are reported was not confirmed).
- Relevance: MSA used for pairwise interaction from observed lesion data (**H-C**), but with naturally occurring, not designed, lesion combinations.

**2.9 msapy toolbox (Fakhar K, Dixit S). `kuffmode/msa`, version 1.7.3, Python ≥ 3.11, MIT license declared in `LICENSE`, last commit 2025-07-14.** URL: https://github.com/kuffmode/msa
- `[V-src]` Read `docs/README.md` and `msapy/msa.py`. Key facts for us:
  - Players can be nodes or links; the game function receives the *complement set* (lesioned elements) and must return one number. Coalition contributions are isolated by lesioning the complement. Shapley values come from sampled permutations; exact needs 2^N.
  - `interaction_2d(pair=(i,j))` returns `(γ_ij, γ_i|j-lesioned, γ_j|i-lesioned)`: Shapley value of the merged unit {i,j}, Shapley value of i in the sub-game with j lesioned, and the reverse. `network_interaction_2d` fills a matrix with `γ_AB − γ_A − γ_B`. This is Keinan 2004 §2.3's "2-D MSA", **not** the Grabisch–Roubens index (see §2.1 of this report).
  - `estimate_causal_influences` runs MSA once per target node with the target's activity as the game value; docstring warns that the objective must be non-negative and bounded, handle the all-lesioned edge case, and that Shapley values should sum to the intact value (otherwise too few permutations, randomness in the objective, or a poor objective).
  - Author-recommended ≥ 1000 permutations per element; runtime scales linearly with N for the all-targets variant.
- Relevance: practical route for **H-C** and Shapley baselines. Cost, not code, is the obstacle: full-network Shapley with a LIF simulator per game is infeasible, so restrict players (on-path cell types) or use the 2×2 design directly.

**2.10 Grabisch M, Roubens M (1999). An axiomatic approach to the concept of interaction among players in cooperative games. *International Journal of Game Theory* 28(4):547–565. DOI 10.1007/s001820050125 (displayed).** URL: https://ideas.repec.org:443/a/spr/jogath/v28y1999i4p547-565.html
- Axiomatises interaction indices (linearity, dummy, symmetry) extending Shapley and Banzhaf values; expresses them via pseudo-Boolean functions. `[V-abs·W]` (byline order differs between Springer and RePEc records.)

**2.11 Sundararajan M, Dhamdhere K, Agarwal A (2020). The Shapley Taylor Interaction Index. *ICML 2020*, PMLR 119:9259–9268. arXiv 1902.05622.** URL: https://proceedings.mlr.press/v119/sundararajan20a.html
- Generalises Shapley to interactions among subsets up to size k; adds an "interaction distribution" axiom; the older Shapley interaction index does not satisfy efficiency, Shapley–Taylor does. `[V-abs·W]`
- Relevance: if we report interactions that must sum to the total effect (efficiency), use Shapley–Taylor rather than Grabisch–Roubens.

**2.12 Jonas E, Kording KP. Could a neuroscientist understand a microprocessor? *PLoS Computational Biology*.** (Consensus: 2016; volume year likely 2017 `[MEM]`.) URL: https://consensus.app/papers/details/7d2c16f2bdca5f51a1533689e177cbb6/?utm_source=claude_desktop
- A microprocessor with a known ground truth was used as a model organism; popular neuroscience analyses (including lesion-style) revealed structure but did not meaningfully describe the hierarchy of information processing. Argues for complex non-linear systems with known ground truth as validation platforms. `[V-abs·C]` (the specific "transistor lesion" results are `[MEM]`; the abstract does not mention lesions.)
- Relevance: the **argument for using the Shiu LIF model as an in-silico ground-truth lab**, and a warning that single-lesion effects may not map onto functional hierarchy. **H-A, H-E**.

**2.13 Morcos AS, et al. (2018). On the importance of single directions for generalization. arXiv.** URL: https://consensus.app/papers/details/6a7e3c72bfc4567cb93485d1364978da/?utm_source=claude_desktop *(only "Ari S. Morcos et al." displayed)*
- Reliance on single directions predicts generalisation; class selectivity is a poor predictor of task importance: individually selective units may not be necessary for strong performance. `[V-abs·C]`
- Companions: Zhou B et al. 2018 (https://consensus.app/papers/details/f25ce9507fe85ce2a86bf5784d7e3272/?utm_source=claude_desktop) — ablating any single unit barely changes overall accuracy but damages specific classes; selectivity predicts *class-level* but not overall importance `[V-abs·C]`. Ranadive et al. 2023, TMLR (https://consensus.app/papers/details/c01a9991165550e3a32d33992f999896/?utm_source=claude_desktop): class-selective neurons are ablatable late but important early in training `[V-abs·C]`. Amjad et al. 2018, IEEE TNNLS (https://consensus.app/papers/details/0b8d029f898c5a47a3eccb4695068442/?utm_source=claude_desktop): cumulative ablation ordered by information quantities can be used to form hypotheses about redundancy and synergy `[V-abs·C]`. Jiang 2026 (https://consensus.app/papers/details/266d491f25505015996033d9b88b5d4c/?utm_source=claude_desktop, preprint-like, venue "Unknown"): single-direction ablation does not remove what it targets (a refitted probe recovers) `[V-abs·C]`.
- Relevance: **H-D** (selectivity/hub-ness ≠ importance for a given task; importance is task-conditional). Zhou 2018 supports computing necessity per task, not overall.

### Theme 3. Redundancy, degeneracy, compensation

**3.1 Tononi G, et al. (1999). Measures of degeneracy and redundancy in biological networks. *PNAS*.** URL: https://consensus.app/papers/details/a0ffa601cf365e3289e773d025fa039e/?utm_source=claude_desktop
- Degeneracy: structurally different elements performing the same function; redundancy: identical elements. Information-theoretic measures with respect to a set of outputs; simulations show degeneracy is high only when many different elements can affect the output similarly *and* have independent effects; low for independent-effect systems and for purely redundant ones. `[V-abs·C]`
- Relevance: vocabulary for **H-B/H-C**: our "parallel routes" are degenerate (different cell types, same output), not redundant duplicates.

**3.2 Edelman GM, Gally JA (2001). Degeneracy and complexity in biological systems. *PNAS* 98(24):13763–13768. DOI 10.1073/pnas.231499798 (displayed).** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC61115
- Degeneracy is widespread, necessary for and an inevitable outcome of natural selection; contrasted with engineering redundancy. `[V-abs·W]`

**3.3 Price CJ, Friston KJ (2002). Degeneracy and cognitive anatomy. *Trends in Cognitive Sciences* 6(10):416–421. DOI 10.1016/S1364-6613(02)01976-9 (displayed in a Wikipedia-mirror reference list; lower trust).** URL: https://www.fil.ion.ucl.ac.uk/~karl/Degeneracy%20and%20cognitive%20anatomy.pdf
- Degeneracy as more than one neuronal system producing the same response; imaging in healthy subjects may fail to show multiple routes if more than one sufficient system is active; link to recovery after damage. `[V-abs·W]`
- Relevance: the "silencing one of two sufficient parallel routes shows nothing" argument at the system level (**H-B/H-C**).

**3.4 Prinz AA, Bucher D, Marder E (2004). Similar network activity from disparate circuit parameters. *Nature Neuroscience* 7:1345–1352. DOI 10.1038/nn1352 (displayed).** URL: https://researchwith.njit.edu/en/publications/similar-network-activity-from-disparate-circuit-parameters/
- Three-cell pyloric model, > 20 million parameter combinations: nearly identical output from widely different parameter sets. `[V-abs·W]`
- Relevance: motivates population-of-models robustness analysis: our result should not hinge on a single parameter set of the Shiu model (**H-B, H-E**).

**3.5 Marder E, et al. (2006). Variability, compensation and homeostasis in neuron and network function. *Nature Reviews Neuroscience*.** URL: https://consensus.app/papers/details/8f7c4562bd825043bc727fb16939ae65/?utm_source=claude_desktop
- Homeostatic mechanisms are needed for stability across a lifetime; compensatory mechanisms allow multiple solutions for similar behaviour; examines how tightly tuned synaptic and intrinsic properties must be. `[V-abs·C]`
- Marder E (2011) *PNAS* "Variability, compensation, and modulation in neurons and circuits" (https://consensus.app/papers/details/0aa42e6be41157adb468ff482d6a0ce9/?utm_source=claude_desktop): compensations and correlations among parameters; use families of models. `[V-abs·C]`
- Relevance: **a key external-validity limit for H-E**: real flies compensate (plasticity, homeostasis) after chronic silencing, which the static LIF model lacks. Acute (optogenetic) vs chronic (genetic) silencing data should be distinguished (LIT-C).

**3.6 Albert R, Jeong H, Barabási A-L (2000). Error and attack tolerance of complex networks. *Nature* 406:378–382. DOI 10.1038/35019019 (displayed).** URL: https://arxiv.org/abs/cond-mat/0008064
- Scale-free networks are tolerant to random failures but fragile under targeted removal of the most connected nodes. `[V-abs·W]`
- Relevance: the hub-attack baseline for **H-A** (the "global hubs are rarely necessary for one task" claim of **H-D** is a task-conditional analogue); topology-only, connectivity-based damage metric.

**3.7 Bacik KA, Schaub MT, Beguerisse-Díaz M, Billeh YN, Barahona M (2016). Flow-based network analysis of the *Caenorhabditis elegans* connectome. *PLoS Computational Biology* 12(8):e1005055.** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4975510/
- Flow-based community detection (Markov Stability) and role-based similarity; an in silico evaluation of **all single and double neuron ablations** to find those most disrupting the multi-scale flow structure; the most strongly supra-additive pairs were dominated by interneurons in one partition and motor neurons in another; most disruptive ablations linked to functionally relevant neurons. `[V-abs·W]`
- Relevance: **prior art for double-ablation, non-additivity analysis on a connectome**, structure-only. Closest *worm* precedent for **H-C**.

**3.8 Towlson EK, Barabási A-L (2020). Synthetic ablations in the *C. elegans* nervous system. *Network Neuroscience*. DOI 10.1162/netn_a_00115 (displayed). arXiv 1907.11297.** URL: https://arxiv.org/abs/1907.11297v1
- Network-control prediction of ablation of neuron **pairs and triplets**: 58 pairs and 46 triplets reduce muscle controllability, clustering in distinct regions of the nervous system. Explicit genetics analogy: neurons are "**synthetic essential**" if individually dispensable but jointly required (context: locomotor response to gentle touch). `[V-abs·W]`
- Relevance: **the most direct prior art pre-empting the *framing* of H-C** (neural analogue of synthetic lethality / genetic interaction between neuron pairs). It uses linear structural controllability, not a thresholded spiking model, and a structure-only criterion; the between- vs within-pathway distinction was not seen in the search summary. Must be cited and distinguished.

**3.9 Kim et al. (2024, bioRxiv; 2026 *European Journal of Neuroscience*). Bilateral symmetry and asymmetry in the *C. elegans* connectome: a graph-theoretic analysis based on redundancy measures** (bioRxiv title) / **Bilateral neuron pairs share redundant network roles despite incomplete connection symmetry in *Caenorhabditis elegans*** (title as seen for the 2026 EJN/PMC13385459 record; the two titles appear to be preprint and journal versions, **not confirmed to be the same work**).
URLs: https://www.biorxiv.org/content/10.1101/2024.10.03.616419.full.pdf ; https://pmc.ncbi.nlm.nih.gov/articles/PMC13385459/ ; https://onlinelibrary.wiley.com/doi/10.1111/ejn.70629 (DOI suffix from the URL, not shown as a DOI)
- Path-compensation index (global efficiency after removing each neuron alone vs both), connectivity similarity and motif fingerprints; bilateral pairs show elevated redundancy relative to other pairs, checked against degree-preserving nulls; interneurons most redundant, sensory neurons least; asymmetry prevents complete redundancy (degeneracy). `[V-abs·W]` (first-author "Kim", co-authors Song, Kralik, Jeong for the preprint; abstracts only partly indexed)
- Also: Birari & Rabinowitch, "Asymmetry in synaptic connectivity balances redundancy and reachability in the *Caenorhabditis elegans* connectome" (*iScience*; title seen at https://scholars.huji.ac.il/ithairabinowitch/node/27405; content `[V-abs·W]` only that partners have similar synapse counts but different identities).
- Relevance: left–right homologs are by design *partially redundant*, which matters for **H-E** (homolog reproducibility is not independent replication; also the effect of silencing one of a pair vs both).

**3.10 Whole-brain connectomics of *Drosophila* reveals a robust, distributed architecture for the suppression of feeding during escape (bioRxiv 2025, DOI 10.64898/2025.12.14.694122, displayed in the URL).** URL: https://www.biorxiv.org/content/10.64898/2025.12.14.694122.full.pdf
- Connectome-constrained spiking model on FlyWire v783 (127,400 neurons, ~50M synapses); escape circuit suppresses feeding via upstream disfacilitation rather than lateral inhibition at MN9; combinatorial silencing: silencing any single inhibitor fails to restore MN9 firing, silencing two gives partial recovery; feeding and grooming suppression use separate pathways. `[V-abs·W]` (body fragments only; authors not displayed)
- Relevance: **flag for LIT-A/NOV**: same model family and same readout (MN9) with combinatorial silencing and a redundancy interpretation, which touches **H-B and H-C**. It is not a pairwise screen and has no structural predictor, from what we saw.

**3.11 Pointers not read:** Paclet et al. 2026 (degeneracy along the sensorimotor hierarchy, Consensus, venue unknown) https://consensus.app/papers/details/4bce103e37ec508593244ff65516d671/?utm_source=claude_desktop `[V-abs·C]`; Yang & Prescott 2023, *Frontiers in Cellular Neuroscience* (degeneracy and pleiotropy in homeostatic regulation) https://consensus.app/papers/details/0cc39d7402cf5d98a6c53ad4cacfc579/?utm_source=claude_desktop `[V-abs·C]`.

### Theme 4. Genetic-interaction analogies

**4.1 Jeong H, Mason SP, Barabási A-L, Oltvai ZN (2001). Lethality and centrality in protein networks. *Nature* 411(6833):41–42. DOI 10.1038/35075138 (displayed). arXiv cond-mat/0105306.** URL: https://arxiv.org/abs/cond-mat/0105306
- Most highly connected proteins in the yeast PPI network are the most important for survival. `[V-abs·W]`

**4.2 He X, Zhang J (2006). Why do hubs tend to be essential in protein networks? *PLoS Genetics* 2(6):e88. DOI 10.1371/journal.pgen.0020088 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1569888/ (the PMC id appeared in the result list; the title was taken from the user's lead and the "PLoS Genetics 2(6):e88" reference from the summary)
- Hubs are more likely essential because they take part in more interactions and some of those are essential (~43% of essentiality attributable to essential interactions in the PPI network). `[V-abs·W]`
- Challenge: a 2008 *PLoS Computational Biology* reanalysis (title as seen: "Why Do Hubs in the Yeast Protein Interaction Network Tend To Be Essential: Reexamining the Connection between the Network Topology and Essentiality", https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2467474/; attributed to Zotenko and colleagues by the summary) argues hub essentiality is better explained by membership in densely connected, essential modules. Batada et al. 2006 *PLoS Biology* argued date hubs are not required for tolerance to node deletion. `[V-abs·W]`
- Relevance: **centrality–lethality is a correlation whose mechanism is contested; modular structure confounds it.** Exactly the "global hub ≠ task-specific necessity" lesson for **H-A/H-D**.

**4.3 Kelley RM, et al. (2005). Systematic interpretation of genetic interactions using protein networks. *Nature Biotechnology*.** URL: https://consensus.app/papers/details/20772a364b7f58fdb5a9398ec00caad6/?utm_source=claude_desktop
- Combining > 4,800 yeast genetic interactions with physical networks: 1,922 interactions significantly associated with either between- or within-pathway explanations (~40% coverage); between-pathway explanations better than within-pathway at interpreting systematic-screen interactions. `[V-abs·C]`
- Relevance: **the conceptual source of H-C**. Between-pathway ⇔ parallel/compensating routes (synergistic/aggravating); within-pathway ⇔ same linear pathway. Note the **ratio in real data favours between-pathway**; the mapping to threshold circuits is ours.

**4.4 Segrè D, DeLuna A, Church GM, Kishony R (2005). Modular epistasis in yeast metabolism. *Nature Genetics* 37:77–83. DOI 10.1038/ng1489 (displayed).** URL: https://www.nature.com/articles/ng1489
- Flux-balance-predicted growth phenotypes of single and double knockouts; a new scale for epistasis revealed a **trimodal** distribution (buffering, aggravating, non-interacting); extends from genes to functional modules; infers modules from epistasis. `[V-abs·W]`
- Relevance: **the epistasis-on-a-model template**: epistasis computed from a mechanistic network model, with modular structure emerging. Also supports a flux-model-first approach before any "experiment".

**4.5 Deutscher D, Meilijson I, Kupiec M, Ruppin E (2006). Multiple knockout analysis of genetic robustness in the yeast metabolic network. *Nature Genetics* 38(9):993–998.** URL: https://www.cs.unm.edu/~eschulte/dissertation/refs/deutscher2006multiple
- In silico multiple knockouts in a flux-balance model of yeast metabolism, building on single/double knockouts. `[V-abs·W]` (the "MSA" component of this paper is `[MEM]`; the search did not confirm it. Lead title "Multi-perturbation Shapley value analysis of yeast metabolism" was not found.)

**4.6 Mani R, et al. (2008). Defining genetic interaction. *PNAS* 105(9):3461–3466. DOI 10.1073/pnas.0712255105 (displayed).** URL: https://consensus.app/papers/details/740e1003597a5ba1b482a3ee3469b3a8/?utm_source=claude_desktop
- Four mathematically distinct definitions (Product, Additive, Log, Min); the choice has "profound consequences": 52% of known synergistic interactions in yeast were inferred according to Min, but Product and Log (practically equivalent) are better than Min for identifying functional relationships; Additive and Log lead to different conclusions in population genetics. `[V-abs·C]` The Min rule treats the double mutant as matching the less-fit single mutant; all four coincide in classification when one single mutant has wild-type fitness. `[V-abs·W]`
- Relevance: **a design requirement for H-C.** Without a pre-registered neutrality function (§2.1), "synergy" is arbitrary.

**4.7 Costanzo M, et al. (2010). The genetic landscape of a cell. *Science* 327(5964):425–431. DOI 10.1126/science.1180823 (displayed).** URL: https://rothlab.csb.pitt.edu/publications/Costanzo_Science_2010.pdf
- 5.4 million gene–gene pairs; interaction profiles cluster into a functional map; genetic-interaction degree correlates with gene attributes. `[V-abs·W]`
- **Costanzo M, et al. (2016). A global interaction network maps a wiring diagram of cellular function. *Science*.** URL: https://consensus.app/papers/details/3b335d079bd756199f4e3399b6d809e6/?utm_source=claude_desktop — > 23 million double mutants; ~550,000 negative and ~350,000 positive interactions; negative interactions connect functionally related genes; positive interactions often map general regulatory connections; essential genes are dense hubs. `[V-abs·C]`
- Relevance: the benchmark for "what fraction of pairs interact and with what sign", giving **base-rate expectations** for **H-C** (a sparse, mostly negative, functionally clustered network).

**4.8 Baryshnikova A, et al. (2010). Quantitative analysis of fitness and genetic interactions in yeast on a genome scale. *Nature Methods* 7(12):1017–1024. DOI 10.1038/nmeth.1534 (displayed).** URL: https://www.nature.com/articles/nmeth.1534 — fitness-based interaction measurement from colony size; positive interactions connect distinct complexes. `[V-abs·W]`
**Phillips PC (2008). Epistasis—the essential role of gene interactions in the structure and evolution of genetic systems. *Nature Reviews Genetics* 9:855–867.** URL: https://www.nature.com/articles/nrg2452.pdf — review arguing for a unified quantitative view. `[V-abs·W]`

**4.9 Scale and higher-order caveats.**
- Wang X, et al. (2010). The meaning of interaction. *Human Heredity* — statistical interaction depends on measurement scale. https://consensus.app/papers/details/85b0dc8a67c056e7ad1f51700503744a/?utm_source=claude_desktop `[V-abs·C]`
- Kuzmin E, et al. (2018). Systematic analysis of complex genetic interactions. *Science* — ~200,000 yeast triple mutants; trigenic interactions tend to be weaker than digenic, ~100× as many as digenic. https://consensus.app/papers/details/46cdef1f83e95cb6844568d466bf367b/?utm_source=claude_desktop `[V-abs·C]`
- Chitra U, et al. (2025). Resolving discrepancies between chimeric and multiplicative measures of higher-order epistasis. *Nature Communications* — chimeric formula (multiplicative model on additive scale) gives same sign for pairs but may change sign for higher-order terms; 10–60% of inferred higher-order interactions change sign. https://consensus.app/papers/details/c7c3e3c8fef25fef94876ecd7e9fb1bd/?utm_source=claude_desktop `[V-abs·C]`
- Katagiri F (2023). An averaging model for analysis and interpretation of high-order genetic interactions. *PLOS ONE*. https://consensus.app/papers/details/3766bf2af99753d1877bc39f7ffbcddc/?utm_source=claude_desktop `[V-abs·C]`
- François P, et al. (2025). The Product neutrality function defining genetic interactions emerges from mechanistic models of cell growth. *eLife*. (Consensus first author "Paul François"; copyright line "Fuentes Valenzuela et al.": inconsistent, to be resolved by the auditor.) https://consensus.app/papers/details/909bb69a3c155ef3907c25043b789101/?utm_source=claude_desktop — on yeast colony growth data, Product beats Additive and Minimum neutrality functions; Product emerges from interdependent cellular processes in growth models. `[V-abs·C]`
- Relevance (all): scale-dependence of "interaction" is the main statistical hazard for **H-C** (§2.1).

**4.10 Kacser H, Burns JA (1981). The molecular basis of dominance. *Genetics* 97(3–4):639–666.** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC1214416
- Dominance as an inherent property of metabolic pathways: flux is nearly insensitive to the activity of any single enzyme (control shared among enzymes; summation theorem); Cornish-Bowden (1987) showed the inference fails when substrate concentrations are large relative to the relevant K_M. `[V-abs·W]` (secondary descriptions; full text not retrieved)
- Relevance: the analogy for **H-B** "sensitivity shift": partial loss of a component along a saturating chain shifts the dose–response curve but may leave the plateau intact.

**4.11 Foucquier J, Guedj M (2015). Analysis of drug combinations: current methodological landscape. *Pharmacology Research & Perspectives* 3(3). DOI 10.1002/prp2.149 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4492765/
- Reviews reference models for combination effects (Bliss independence, Loewe additivity); no universal reference methodology. Per a secondary source: Bliss excess = observed − (E1 + E2 − E1E2) for effects in [0,1]; Bliss expected for independent action on separate pathways, Loewe rests on dose equivalence. `[V-abs·W]`
- Relevance: pharmacology has already solved the "which null for two dose-dependent perturbations" problem; for dose-dependent neuron silencing (graded stimulus intensity), Bliss/Loewe-type nulls are worth considering alongside Mani's.

**4.12 Flux-balance prediction vs topology (context only).**
- A 2025 arXiv preprint (Boone J, "A topology-based machine learning model decisively outperforms flux balance analysis in predicting metabolic gene essentiality", https://arxiv.org/abs/2507.20406v1) claims the reverse (topology beats FBA on the E. coli core network); it is **not peer-reviewed** and the claim is only from a search summary `[V-abs·W]`.
- The "analysis of metabolic networks fails to find correlations between topology and essentiality; approaches combining topology and biochemical parameters (FBA) do better" claim came from an untitled MIT DSpace record (https://dspace.mit.edu/handle/1721.1/59195) with no author attributed in the snippet. **Do not cite**; see §4.
- Relevance: **if the lesson holds for neurons, topology alone is weak and dynamics-aware (flux-like) predictors win** — consistent with the ladder in **H-A**.

### Theme 5. Graph-theoretic tools for source→target necessity and redundancy

**5.1 Menger's theorem / max-flow–min-cut (background).** For distinct non-adjacent vertices s,t, the maximum number of internally vertex-disjoint s–t paths equals the minimum size of an s–t vertex cut; with unit node capacities, max-flow decomposes into vertex-disjoint paths; connectivity counts redundant independent routes. Sources: Freiburg algorithms lecture notes https://ac.informatik.uni-freiburg.de/teaching/ws21_22/algo2122/pdf/Chapter6_PartIV.pdf and a generic engineering page https://metricgate.com/docs/vertex-edge-connectivity-menger/ `[V-abs·W]`. Newman M (2004), "Analysis of weighted networks", *Phys Rev E*, abstract mentions a simple proof of the max-flow–min-cut theorem via a weighted→multigraph mapping https://consensus.app/papers/details/892c50fb207b565480a83fa366f44e82/?utm_source=claude_desktop `[V-abs·C]`. The original Menger (1927) and Ford–Fulkerson (1956) papers are `[MEM]`, unverified.

**5.2 Freeman LC, Borgatti SP, White DR (1991). Centrality in valued graphs: a measure of betweenness based on network flow. *Social Networks* 13(2):141–154.** URL: https://escholarship.org/uc/item/5rd2w4qf
- Flow betweenness uses all independent paths (not only geodesics) between all pairs; defined for valued graphs. The `sna` R documentation defines raw flow betweenness of node k as the sum over pairs (i,j) of maxflow(i,j) with k present minus maxflow(i,j) with k removed; a normalised variant divides by the total max flow. `[V-abs·W]` (https://search.r-project.org/CRAN/refmans/sna/html/flowbet.html)
- Relevance: **this is exactly a pairwise flow-drop lesion score**; a ready all-pairs baseline vs source→target-specific flow (**H-A**).

**5.3 Newman MEJ (2005). A measure of betweenness centrality based on random walks. *Social Networks* 27(1):39–54. DOI 10.1016/j.socnet.2004.11.009 (displayed). arXiv cond-mat/0309045.** URL: https://arxiv.org/abs/cond-mat/0309045
- Counts how often a node is traversed by a random walk between two others; calculable by matrix methods. `[V-abs·W]` (the O(mn²) cost remark came from a non-primary source, ignore).
- Relevance: electrical-network/current-flow analogue; for signed networks not defined as is (§2).

**5.4 Lengauer T, Tarjan RE (1979). A fast algorithm for finding dominators in a flowgraph. *ACM TOPLAS* 1(1):121–141. DOI 10.1145/357062.357071 (displayed).** URL: https://www.cs.princeton.edu/courses/archive/spring03/cs423/download/dominators.pdf
- Almost-linear dominator-tree algorithm. `[V-abs·W]` Definition (d dominates v if every path from the root to v passes through d; immediate dominators form a tree) is standard graph theory, stated in the search summary but not from a primary source in this session (`[MEM]`).

**5.5 Dominator trees on biological networks.** ZDOG: zooming in on dominating genes with mutations in cancer pathways (*Bioinformatics*? venue not displayed; PMC6937862, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6937862/): dominator-tree model assesses a gene's positional importance in cancer signalling pathways from a chosen entry node; cannot distinguish inhibitory from stimulatory interactions. `[V-abs·W]` Also "Dominating Biological Networks" (PMC3162560; a different, graph *domination* notion: not the same concept). **No application of dominator trees to connectomes was found** (queries #27 and #87).

**5.6 Daugulis P (2016). Strong connectivity and its applications. arXiv 1609.07355 (cs.DM; cross-lists q-bio.NC, math.CO).** URL: https://arxiv.org/pdf/1609.07355
- Strong vertex/edge connectivity invariants for strongly connected directed graphs, with computational results on public connectome graphs (cat cortex: 65 vertices/1139 edges; a Drosophila mesoscale graph: 1781 vertices/9735 edges); directed strong connectivities reported close to undirected ones. `[V-abs·W]`
- Relevance: **the only vertex-connectivity (Menger-type) number computation on connectomes found by name**, at tiny whole-network scale, global rather than source→target.

**5.7 Li Z-Q (2026). Real-time functional lesion simulation in connectomics: rapid sensitivity analysis of neural pathways via traversal tree-correlated cuts. *Interdisciplinary Sciences: Computational Life Sciences*.** URL: https://consensus.app/papers/details/7bc61091a8f558a8984a9d887e242b7d/?utm_source=claude_desktop
- The min-cut between two regions is the structural bottleneck; algorithm bounding min-cut values via traversal trees; virtually removing a node and querying for precipitous drops in the min-cut bound flags "bridge" nodes; ~3 orders of magnitude faster than standard max-flow; on high-resolution connectome data (neurosurgical planning; abstract does not say which connectome). `[V-abs·C]`
- Relevance: **a direct application of "min-cut drop under node removal" as a lesion proxy on connectomes** (human, tractography-scale), the same score as H-C's structural predictor. Peer-reviewed status unverified beyond the journal name. 

**5.8 Irzan H, et al. (2020). Min-cut max-flow for network abnormality detection: application to preterm birth.** URL: https://consensus.app/papers/details/7baf0c2ca3c75402ad15d318a9157b60/?utm_source=claude_desktop — casts subject-level structural-connectome abnormality detection as min-cut/max-flow. `[V-abs·C]` (venue "Unknown" in the index.) Relevance: precedent only for max-flow on connectome graphs, not for lesions. Also: Jensen P, et al. (2022) *IEEE TPAMI*, review of serial/parallel min-cut/max-flow solvers (OR-Tools-type engineering choice): https://consensus.app/papers/details/658d78652c2b5fb4a2e084e579efca53/?utm_source=claude_desktop `[V-abs·C]`.

**5.9 Ganguly I, et al. (Columbia). Efficient connectome analyses for identifying bottleneck neurons in behaviorally-relevant pathways (Krell Institute CSGF conference abstracts 2022–2024; not a paper).** URL: https://krellinst.org/csgf/conf/2024/abstracts/ganguly2021
- Influence metric over pathways of arbitrary length between source and target; algorithm finds the smallest neuron set accounting for a chosen share of influence ("bottleneck neurons"); gain parameter penalises long pathways; validated on the hemibrain by recovering sensory→descending pathways; later abstract applies it to sensory periphery → mushroom body. `[V-abs·W]`
- Relevance: **fly-specific source→target bottleneck prior art** (an influence-share cover, not vertex-cut). Relevant to **H-A**. Abstract-only; a full paper may exist.

**5.10 Sabrin KM, Wei Y, van den Heuvel MP, Dovrolis C (2020). The hourglass organization of the *Caenorhabditis elegans* connectome. *PLoS Computational Biology* 16(2):e1007526. DOI 10.1371/journal.pcbi.1007526 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7029875/
- Feed-forward flow from sensory to motor neurons traverses a small core ("hourglass waist") of 10–15 interneurons, mostly the C. elegans rich club. `[V-abs·W]` (a bottleneck/waist analysis, not max-flow.)

**5.11 Bacik 2016 (3.7) and Towlson & Barabási 2020 (3.8)** also belong here: flow-based pair ablation and network-control pair ablation respectively.

**5.12 [V-src] `danilo-lazovic/fly-bottlenecks` (public GitHub, last commit 2026-09-27 "Add whole-CNS LIF simulation and ablation of the taste -> MN9 cut"): "Max-flow / min-cut bottlenecks in the male *Drosophila* CNS connectome, validated by in-silico ablation".** URL: https://github.com/danilo-lazovic/fly-bottlenecks (cloned to `/tmp/claude-0/-home-user-fly-or-fail/27fea6bb-f99b-5a22-9d9c-b68b632bd803/scratchpad/clones/fly-bottlenecks`; README, PROJECT_CONTEXT.md and `src/sim.py` skimmed; **no code run, results not reproduced**). **Not peer-reviewed, a hobby/portfolio project** (PROJECT_CONTEXT calls it "a portfolio piece"), and its own README flags several caveats. What it reports:
  - Data: male CNS v1.0 via neuPrint (174,386 neurons with edges; 25.9M edges); signs from `consensusNt` (ACh excitatory; GABA/Glu/His inhibitory). FlyWire is mentioned only as an optional comparison.
  - Model: its own numba re-implementation of the **Shiu et al. 2024 LIF model parameters** (v_th −45 mV, τ_m 20 ms, τ_syn 5 ms, 0.275 mV/synapse, Poisson drive 150 Hz × 250, 30 × 1 s trials); silencing removes a neuron's output synapses "as in the original". Not validated against the original here.
  - Method: **node min-cut with unit capacity** between a sensory source set and an identified target; the "cut to all 1,314 descending neurons" is trivially the first relay layer (cut sizes 1,142–12,454 depending on modality) and "says nothing"; the informative analysis is **single identified targets**: photoreceptors → giant fiber DNp01 (cut of 21 neurons at ≥ 1% input share; 1,267 on the full graph, dominated by LPLC2 and LC4) and head taste → MN9 (cut of 34 at ≥ 1%; 355 on the full graph).
  - Result for taste → MN9 (stimulus: the 121 head-taste neurons of the 8 of 37 types that drive MN9 ≥ 10 Hz alone): intact ≈ 106–108 Hz; **silencing the 34-neuron min cut → 0.38 ± 0.21 Hz (0.4% of intact)**; top-34 path-betweenness → 44.3 Hz (41%); top-34 PageRank → 107.8 Hz (≈ 100%); top-34 out-strength → 118 Hz (110%); 20 random on-path sets → 107.3 Hz (≈ 100%).
  - Author-stated caveats: the random baseline is weak; the stimulus types were chosen with the same model (the cut was not); out-strength silencing raises MN9 (removing inhibitory hubs); a per-edge input-share filter breaks convergent small-input pathways (e.g., T4/T5 → LPLC2), so a cell-type-level graph is the "natural next step".
  - **Relevance and pre-emption: see §3.2.** It tests *set-level* silencing of a structural min-cut vs centrality baselines in a Shiu-parameter LIF model. It does **not** test single-neuron necessity, operating-point dependence, linear response, or pairs.

**5.13 Cell 2026 male-CNS paper: Sexual dimorphism in the complete *Drosophila* male central nervous system connectome. *Cell* 2026, 189(18):5504–5526.e15. DOI 10.1016/j.cell.2026.08.015 (displayed).** URLs: https://www.janelia.org/publication/sexual-dimorphism-in-the-complete-drosophila-male-central-nervous-system-connectome ; https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6 ; preprint https://www.biorxiv.org/content/10.1101/2025.10.09.680999.full.pdf
- Existence, venue, graph size (≈ 166,000 neurons, 25.6M edges), intact neck connective: `[V-abs·W]`. Two of three WebSearch syntheses also state that the paper "ran maximum flow analysis on the synaptic graph" for each sensory-modality × motor-domain pair on a presynaptic-input-normalised graph, with the neck connective as bottleneck; a third search did not mention max flow. **Treated as unconfirmed (see §4, U-3).**

### Theme 6. Linear response, effective connectivity, threshold-linear and threshold models

**6.1 Trousdale J, Hu Y, Shea-Brown E, Josić K (2012). Impact of network structure and cellular response on spike time correlations. *PLoS Computational Biology* 8(3):e1002408. DOI 10.1371/journal.pcbi.1002408 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3310711/
- Linear response theory expresses correlations in terms of connectivity and single-cell properties, matching integrate-and-fire simulations; correlations depend strongly on the neurons' operating point even at fixed connectivity; expansion in powers of the matrices describing the architecture; strengthening inhibition may synchronise activity. `[V-abs·W]`
- Relevance: **theoretical anchor for H-A top rung and for H-B**: structure → response is an operating-point-dependent power series, i.e. (I − DW)⁻¹.

**6.2 Ocker GK, Josić K, Shea-Brown E, Buice MA (2017). Linking structure and activity in nonlinear spiking networks. *PLoS Computational Biology* 13(6):e1005583. DOI 10.1371/journal.pcbi.1005583 (displayed).** URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5507396/
- Diagrammatic fluctuation expansion beyond linearisation; nonlinear input–rate transfer couples higher-order statistics to lower-order ones; linear methods can fail to predict spiking statistics and can misjudge stability. `[V-abs·W]`
- Relevance: formal reason the "gap" between the linear-response rung and truth measures nonlinearity (**H-A**); a warning that stability of linearisation can be wrong.

**6.3 Curto C, Geneson J, Morrison K (2019). Fixed points of competitive threshold-linear networks. *Neural Computation* 31(1):94–155.** URL: https://pure.psu.edu/en/publications/fixed-points-of-competitive-threshold-linear-networks/
- Two characterisations of fixed points (sign condition; domination) and graph rules for combinatorial threshold-linear networks (CTLNs, connectivity from directed graphs); results for networks built from subnetworks. `[V-abs·W]`
- Also: Morrison K, Curto C, "Predicting neural network dynamics via graphical analysis" (arXiv 1804.01487, https://arxiv.org/abs/1804.01487); "Graph rules for recurrent neural network dynamics" (Curto & Morrison; NSF-hosted copy, venue not displayed, https://par.nsf.gov/servlets/purl/10439752): graph structure alone constrains, sometimes determines, stable and unstable fixed points. `[V-abs·W]`
- Relevance: **proof that graph structure can determine threshold-network dynamics**, but for *competitive (inhibition-dominated)* TLNs; transfer to excitation-driven feedforward-heavy LIF circuits is untested (our judgement). **H-B**.

**6.4 Watts DJ (2002). A simple model of global cascades on random networks. *PNAS* 99(9):5766–5771. DOI 10.1073/pnas.082090499 (displayed).** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC122850/
- Threshold-fraction cascade model: nodes adopt state 1 if ≥ φ of neighbours are 1; in sparse networks cascade sizes follow a power law, in dense networks stability limits cascades; heterogeneous thresholds increase vulnerability, heterogeneous degrees decrease it. `[V-abs·W]`
- Relevance: the generic theory that *threshold margin* sets who matters (**H-B**); deterministic binary, no weights/signs.

**6.5 Kitsak M, et al. (2010). Identification of influential spreaders in complex networks. *Nature Physics* 6:888–893.** URL: https://arxiv.org/abs/1001.5285 — k-shell index, not degree or betweenness, best predicts spreading; hubs in the periphery are poor spreaders; with multiple spreaders, distance between them matters. `[V-abs·W]`
**Morone F, Makse HA (2015). Influence maximization in complex networks through optimal percolation. *Nature* 524:65–68. DOI 10.1038/nature14604 (displayed).** URL: https://arxiv.org/abs/1506.08326 — optimal percolation; "weak nodes" outrank hubs; Collective Influence. `[V-abs·W]`
- Relevance: **precedent that the best structural predictor of node importance depends on the dynamics (spreading/percolation) and that degree is often a poor predictor** (**H-A**); k-core as a candidate L1 predictor.

**6.6 Feizi S, Marbach D, Médard M, Kellis M (2013). Network deconvolution as a general method to distinguish direct dependencies in networks. *Nature Biotechnology* 31(8):726–733. DOI 10.1038/nbt.2635 (displayed).** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC3773370
- Infers direct effects from an observed matrix of direct+indirect effects; inverse of network convolution. `[V-abs·W]`
- Relevance: the matrix-inverse "direct vs indirect" logic that (I−W)⁻¹ also inverts (cf. msapy note that causal-contribution matrices do not mirror the connectome). 

**6.7** Estrada's resolvent and exponential communicability (1.16–1.19) and Seguin (1.10–1.13) are the "total influence" counterparts in network neuroscience. Pospisil 2024 (1.21) is the closest fly-brain linear-dynamics paper.

### Theme 7. Null models and statistical pitfalls

**7.1 Maslov S, Sneppen K (2002). Specificity and stability in topology of protein networks. *Science* 296(5569):910–913. DOI 10.1126/science.1065103 (displayed in a result title). arXiv cond-mat/0205380.** URL: https://arxiv.org/abs/cond-mat/0205380
- Degree-preserving random rewiring (reshuffling links while keeping each node's in- and out-degree constant) as the null for yeast PPI and regulatory networks; the null had to respect the directed bait/prey asymmetry; links between hubs suppressed. `[V-abs·W]`

**7.2 Squartini T, Garlaschelli D (2011). Analytical maximum-likelihood method to detect patterns in real networks. *New Journal of Physics* 13:083001. arXiv 1103.0701.** URL: https://arxiv.org/pdf/1103.0701 — maximum-entropy, fully analytical (no randomised samples) for binary, weighted, directed or undirected networks; argues common modularity-type expressions are based on incorrect null expectations. `[V-abs·W]` (A second lead, "Reconnecting statistical physics and combinatorics beyond ensemble equivalence", was not found.)

**7.3 Váša F, Mišić B (2022). Null models in network neuroscience. *Nature Reviews Neuroscience* 23(8):493–504.** URL: https://kclpure.kcl.ac.uk/portal/en/publications/null-models-in-network-neuroscience/ — spectrum from liberal to conservative nulls; randomisation and generative approaches; spatially embedded, annotated, and correlation-derived networks. `[V-abs·W]`

**7.4 Spatial and geometric nulls.** Roberts JA, et al. (2016) *NeuroImage* 124:379–393, "The contribution of geometry to the human connectome": spatial embedding contributes a major, but not definitive, part of topology https://findanexpert.unimelb.edu.au/scholarlywork/1008726-the-contribution-of-geometry-to-the-human-connectome `[V-abs·W]`. Burt JB, Helmer M, Shinn M, Anticevic A, Murray JD (2020) *NeuroImage* 220:117038, "Generative modeling of brain maps with spatial autocorrelation" (BrainSMASH): variogram-matched surrogate maps https://www.biorxiv.org/content/10.1101/2020.02.18.955054.full.pdf `[V-abs·W]`. A result titled "Generative models for network neuroscience: prospects and promise" (PMC5721166, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5721166/) was seen but its authors/venue were not displayed. Relevance: for fly, spatial embedding is of unknown importance; a distance-aware null belongs next to the degree-preserving null.

**7.5 Non-independence and leakage.** Roberts DR, et al. (2017) *Ecography* 40(8):913–929, DOI 10.1111/ecog.02881: random CV gives misleadingly good error on data with dependence structure; block CV nearly always more appropriate when predicting to new data/predictor space or selecting causal predictors; blocks can force extrapolation https://pred.uni-regensburg.de/id/eprint/1455/ `[V-abs·W]`. Kapoor S, Narayanan A (2023) *Patterns* 4(9):100804, DOI 10.1016/j.patter.2023.100804: leakage affects ≥ 294 papers in 17 fields; fixing it removes apparent advantages of complex ML https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856 `[V-abs·W]`. Dekker D, Krackhardt D, Snijders TAB (2007) *Psychometrika* 72(4):563–581, DOI 10.1007/s11336-007-9016-1: permutation (MRQAP) tests for regression on matrix data; Freedman–Lane and double semi-partialling robust to collinearity/autocorrelation https://www.cambridge.org/core/journals/psychometrika/article/abs/sensitivity-of-mrqap-tests-to-collinearity-and-autocorrelation-conditions/57FB719C456B7A43EB073DEBFF0411AB `[V-abs·W]`. Relevance: neurons share cell types, left–right homologs and neighbours; random neuron-level CV leaks. Group by type / homolog pair / region (**H-A, H-E**).

**7.6 Multiple comparisons.** No source was searched. Benjamini–Hochberg (1995) FDR and permutation-based max-statistics (§4, U-8) are `[MEM]`. With ~10⁴–10⁸ candidate pairs (§2.1), a pre-registered, hypothesis-limited pair list matters more than correction.

---

## 2. Formal toolkit

All notation: directed weighted signed graph with weight matrix W (W_ij = signed synaptic weight j→i; sign by presynaptic neuron j under Dale-like transmitter assignment), neurons i ∈ {1..n}, source set S, target set T, performance/readout P(·) (e.g. MN9 spike rate), P₀ = intact value. "a, b" are two neurons. Formulas marked "ours" are derivations; named-literature formulas carry the evidence tag of the source.

### 2.1 Pairwise epistasis (Mani et al. 2008 and extensions)

Let w_a = P(a silenced)/P₀, w_b likewise, w_ab = P(a, b silenced)/P₀, all in [0, ~1] (w can exceed 1 if a silenced neuron was inhibitory). Mani et al. define four neutrality functions for the expected double-mutant fitness (`[V-abs·C]` for the names and for the Min description; the algebra below is `[MEM]` standard, restated by us):

| Definition | Expected double ŵ_ab under no interaction | Interaction score ε |
|---|---|---|
| Product (multiplicative; = Bliss independence if w is a fraction of normal) | w_a w_b | ε_P = w_ab − w_a w_b |
| Additive | w_a + w_b − 1 | ε_A = w_ab − (w_a + w_b − 1) |
| Log | w_a w_b on the log scale | ε_L = log w_ab − log w_a − log w_b |
| Min | min(w_a, w_b) | ε_M = w_ab − min(w_a, w_b) |

Sign convention (as in yeast genetics): ε < 0 aggravating/synergistic ("synthetic sick/lethal"), ε > 0 alleviating/buffering. The 2005 Segrè scale and later work (Baryshnikova 2010) use further variants (`[V-abs·W]` for existence, algebra `[MEM]`).

**Worked behaviour for neural circuits (ours; check numerically before relying on it).**
- *Perfect parallel redundancy* (either of a or b alone sustains output): w_a = w_b = 1, w_ab = 0. All four rules agree in sign (ε_P = ε_A = ε_M = −1; ε_L = −∞, so Log needs a floor/pseudocount). This is the case where Mani et al. say all definitions give identical classification (`[V-abs·W]`).
- *Series bottleneck* (each of a, b is necessary): w_a = w_b = w_ab = 0 → ε_P = ε_M = 0 (and ε_A = +1 only because the additive expectation w_a + w_b − 1 = −1 is below the physical floor; floor it at 0 and ε_A = 0): **no interaction, because the first removal already abolishes the output**. Positive epistasis (ε_P > 0) needs partial single effects and masking: e.g. w_a = w_b = 0.5, w_ab = 0.5 (b masks a): ε_P = +0.25, ε_A = +0.5, **ε_M = 0**. So "series pairs show masking" depends on the rule: under **Min**, a masked pair is "non-interacting", under **Product** it is "positive". H-C's claim "series → positive epistasis" is therefore a statement about partially effective single silencings, not about abolishing ones.
- *Floor effect*: P ≥ 0 and the model has no spontaneous activity (stance 3). When both single effects are large, ε_P is bounded in [−w_a w_b, +...]; large |ε| can arise from the floor alone. **Report w_a, w_b, w_ab and the rule; never only ε.**
- *Graded drive*: with dose-dependent readouts (rate vs stimulus intensity λ), compute ε on the *curve* (shift of EC50, plateau, slope), or use Bliss/Loewe-type nulls (4.11) at matched λ. A scalar ε at one λ is operating-point dependent (H-B).
- *Noise*: ε requires an interval; with LIF stochasticity, w̄_ab − w̄_a w̄_b has variance from four independent cells (delta method or bootstrap over trials). Estimate noise floor from pairs known to be non-interacting (e.g., neurons far off-path).

**Recommendation (for design):** pre-register Product (Mani et al. recommend Product/Log over Min for functional relationships, `[V-abs·C]`) as the primary rule, with Min and Additive as sensitivity analyses, plus a "Bliss on curves" version. Report the sign classification stability across rules.

### 2.2 Shapley value and interaction indices

**Setup (Keinan et al. 2004; msapy `[V-src]`).** Players N = {1..n}; value function v(S) = performance when only S is intact (complement lesioned); conventionally v(∅) = 0 or the all-lesioned baseline (msapy requires the user to handle the all-lesioned edge case, `[V-src]`).

Shapley value (standard, `[MEM]` formula; MSA purpose `[V-abs·W]`):

φ_i = Σ_{S ⊆ N∖{i}} [ |S|! (n − |S| − 1)! / n! ] · ( v(S ∪ {i}) − v(S) )  =  E_π [ v(Pre_i(π) ∪ {i}) − v(Pre_i(π)) ]

(π a uniformly random ordering, Pre_i(π) the players preceding i). Efficiency: Σ_i φ_i = v(N) − v(∅). msapy's docstring says Shapley values sum to the intact value `[V-src]` (with v(∅)=0). Estimation by sampled permutations (msapy) needs ≥ ~1000 permutations per element by the authors' advice `[V-src]`.

Shapley interaction index of a pair (Grabisch & Roubens 1999; existence `[V-abs·W]`, formula `[MEM]`):

I_ij = Σ_{S ⊆ N∖{i,j}} [ |S|! (n − |S| − 2)! / (n − 1)! ] · Δ_ij v(S),   Δ_ij v(S) = v(S∪{i,j}) − v(S∪{i}) − v(S∪{j}) + v(S).

Efficiency does not hold for this index; the **Shapley–Taylor index** (Sundararajan et al. 2020) restores efficiency (`[V-abs·W]`).

**Which "interaction" do we mean?** Three different objects, not interchangeable:
1. *Context-free pairwise epistasis* (§2.1): the 2×2 design in the intact background (S = N∖{i,j}), 4 simulations per pair.
2. *Shapley interaction index*: the same second difference averaged over **all backgrounds S** with Shapley weights; needs sampling of many contexts per pair.
3. *msapy 2-D MSA* `[V-src]`: γ_ij − γ_i|j − γ_j|i, where γ are Shapley values from sub-games with a partner lesioned or merged. It is a related but distinct scalar, defined by Keinan et al. 2004 §2.3 `[V-src]` and not the Grabisch–Roubens index.

**Assumptions and pitfalls.**
- MSA needs the objective to be well-defined for every coalition, including nearly-empty ones, where a thresholded LIF model with no spontaneous activity gives P = 0 for most coalitions. Marginal contributions of irrelevant neurons are then zero by construction, which concentrates Shapley mass on neurons on source→target paths (and is the same as stance 3).
- Exact computation is 2^n; msapy docs give 2^52 ≈ 4.5×10¹⁵ for 52 regions `[V-src]`. For a 10⁵ neuron brain, **only a restricted player set** (e.g. the on-path cell types, ~10²–10³ players) is feasible; this is a design choice that changes the game.
- Shapley values answer "average marginal contribution across all contexts", not "what happens if I silence this neuron in the intact brain". The two disagree under redundancy (Fakhar & Hilgetag 2022 `[V-abs·W]`). Use both: single-lesion necessity (SPA) as the primary outcome and Shapley as a secondary causal-attribution score.
- Sampling noise: with LIF simulation noise, "sum to intact value" is only approximate (msapy note on randomness `[V-src]`).
- Interaction indices of higher order than 2 and Shapley–Taylor with k > 2 explode combinatorially; Kuzmin et al. 2018 `[V-abs·C]` suggest trigenic effects are weaker in magnitude but far more numerous.

### 2.3 Max-flow / vertex-cut redundancy (source→target)

**Construction (standard `[MEM]`, concepts `[V-abs·W]`).** Add super-source s* → every s ∈ S with infinite capacity, every t ∈ T → super-sink t* with infinite capacity. Vertex-split each internal neuron v into v_in → v_out with capacity c_v (c_v = 1 for vertex-disjoint paths; c_v = ∞ for edge-capacitated flow; or c_v = a firing-capacity proxy). Edge u_out → v_in with capacity κ_uv (unit; synapse count; input-share w_uv/Σ_u w_uv; or max(0, W_vu) for excitatory only).

Quantities:
- **F(S,T)** = max-flow. With unit vertex capacities, F = number of internally vertex-disjoint S–T paths = size of a minimum vertex cut (Menger) `[V-abs·W]`.
- **Flow drop (single lesion):** ΔF(x) = F − F_{−x}. With unit vertex capacities ΔF(x) ∈ {0,1}; ΔF(x) = 1 iff every maximum flow carries flow through x (testable by one extra max-flow computation with x removed; algorithmic detail `[MEM]`).
- **Fractional flow loss (ours):** f_x = ΔF(x)/F with capacities proportional to weights. The proposed H-B/H-C theory in `docs/design/theory_note.md` uses f_k in an EC50-shift law (not reviewed here).
- **Structural pair interaction (inclusion–exclusion, ours = Freeman-style second difference):** E^flow_ab = F − F_{−a} − F_{−b} + F_{−ab} (the flow analogue of the Mani second difference with additive scale). For **parallel disjoint routes** each carrying 1 unit and F = 2 with a, b on different routes: F_{−a}=F_{−b}=1, F_{−ab}=0 → E = 2−1−1+0 = 0 in flow (flow is additive across disjoint parallel routes!), whereas a threshold readout turns the flow loss from 1 to "below threshold" nonlinearly. This is the core difficulty for H-C: **max-flow additivity vs output thresholding**. A pair that is jointly necessary (a∥b both required to cross a threshold) is not detectable in flow without a transfer function. Series pair on one route: F = 1, F_{−a} = F_{−b} = F_{−ab} = 0 → E = 1−0−0+0 = +1 (masking in flow).
- **Dominators / single-vertex cuts:** with a single root r (or super-source), d dominates v iff every r→v path passes d; dominator tree via Lengauer–Tarjan (`[V-abs·W]`). The set of vertices that dominate t* = the F=1 vertex cuts; in multi-source settings with many sources they are few (each source has its own routes).
- **Flow betweenness (Freeman 1991)** `[V-abs·W]`: C_F(k) = Σ_{i<j; i,j≠k} [ m_ij − m_ij(k) ] where m_ij(k) is the maximum flow i→j in the graph with k removed (sna definition above). This is the all-pairs analogue of ΔF; the source→target version is the specific-task variant.
- **Random-walk (current-flow) betweenness (Newman 2005)** `[V-abs·W]`: expected net traversals of k in random walks from i absorbed at j; matrix-inverse computation. Not defined for signed weights as is; use |W| or the excitatory subgraph.

**Assumptions and pitfalls.**
- Flow is **sign-blind**. Inhibitory edges either must be dropped (excitatory subgraph only; the fly-bottlenecks repo takes ACh-only edges, `[V-src]`) or modelled as negative gates, which max-flow cannot represent. Photoreceptors being histaminergic leaves "an ACh-only graph with no edges leaving the visual sensory set" `[V-src]`.
- **Capacity choice dominates the answer.** Unit vertex capacity ignores weight and drive; the fly-bottlenecks authors find the 1%-input-share filter changes the cut (Jaccard 0.34 for 0.5% vs 1% in vision) and breaks convergent small-input pathways `[V-src]`. Weighted/capacitated versions need a model of when a weak input matters (this is where thresholds enter, H-B).
- **Cutting to all of T is uninformative**: the min cut is just the first relay layer `[V-src]`. Choose a single identified target or a weighted objective.
- **Minimum cut is non-unique;** the cut reported depends on the solver. Use all minimum cuts (enumerate via the residual DAG) or define membership as "in at least one min cut".
- Max-flow counts *capacity*, LIF necessity depends on *coincident* input exceeding threshold: flow can overstate redundancy (many weak routes that never reach threshold) and understate synergy (see E^flow above).
- Directed cycles and feedback are ignored by flow (steady-state).

### 2.4 Linear-response influence (Green's function)

For a rate-like network r = f(Wr + h) with operating-point gains D = diag(f′(u_i)) (u = Wr+h at the intact solution), the linearised response to a small input perturbation δh is δr = (I − DW)⁻¹ D δh = Σ_{k≥0} (DW)^k D δh (Neumann series, converges iff spectral radius ρ(DW) < 1). `[MEM]` standard; the LIF/correlation version is Trousdale et al. 2012 (`[V-abs·W]`: expansion in powers of architecture matrices; operating-point dependence), nonlinear extension Ocker et al. 2017 (`[V-abs·W]`).

**Lesion of neuron j (clamp r_j = 0) to first order (ours):** with j removed from the dynamics, δr_{−j} = −(I − D W)^{-1}_{−j,−j} D_{−j} W_{−j,j} r_j. So the predicted effect on target t is proportional to **the baseline activity r_j of the silenced neuron** and the gain-weighted walk-sum from j to t in the network *without j*. Three consequences: (i) baseline activity is a built-in multiplier (stance 3: it must also be a baseline predictor); (ii) cancellation between excitatory and inhibitory walks in signed W is inherent (can make total influence ≈ 0 although both routes are strong); (iii) validity requires |δr| small relative to margins: for abolition-scale silencing the linear prediction fails, and that failure is the threshold effect we want to measure (H-A residual).

**Communicability family (structural analogues):**
- Exponential: G^exp = exp(A) = Σ_k A^k/k!; resolvent (Katz-type): G^res = (I − αA)⁻¹ = Σ_k α^k A^k (α < 1/ρ(A)); weights longer walks less (Estrada & Hatano; Estrada, Hatano & Benzi review, `[V-abs·C]`). Setting A = DW gives the linear-response matrix above with α absorbed. Communicability betweenness = sensitivity (Fréchet derivative) of exp(A) to node-edge perturbation (`[V-abs·C]`).
- Sensitivity of total communicability to a single edge change or node removal has analytic bounds (De la Cruz Cabrera et al.; Schweitzer 2023; `[V-abs·C]`).

**Assumptions and pitfalls.**
- Requires choosing D (operating point): gains for LIF depend on mean drive and noise (Trousdale `[V-abs·W]`); D≈I is the "structure-only" case and is wrong near threshold.
- Signed, non-normal (non-symmetric) W: ρ(DW) may exceed 1 even in stable thresholded networks because D differs by neuron; a divergent series means the linearisation predicts instability (Ocker `[V-abs·W]`). Normalise by strength or use an effective D.
- The walk-sum treats all routes additively; threshold-gating makes route contributions **non-additive** (coincidence detection). Use as a rung, not a theory of redundancy.
- **Circularity (stance 2):** the LIF model is parameterised from the same W, so (I − DW)⁻¹ agreeing with simulations is a consistency check of the linearisation, not evidence about biology.

### 2.5 Threshold-gating margin (ours, for H-B; check against `docs/design/theory_note.md`)

For a postsynaptic neuron i with presynaptic set P_i, drive u_i = Σ_{j∈P_i} W_ij r_j and threshold θ_i, define the *margin* m_i = u_i − θ_i (> 0 means it fires in a rate-threshold caricature). Silencing j ∈ P_i changes u_i by −W_ij r_j. In this caricature j is **necessary for i** iff W_ij r_j > m_i; j is **dispensable** if W_ij r_j ≤ m_i; two dispensable inputs j,k become jointly necessary iff W_ij r_j + W_ik r_k > m_i with each term ≤ m_i: **threshold-induced synergy**. A vertex-disjoint parallel pair into a common AND-like target is synergistic exactly when the sum of their contributions exceeds the margin, which flow (§2.3) cannot see. Watts-type threshold-fraction models and CTLN fixed-point theory (6.3–6.4) are the literature homes, though neither addresses signed, weighted, noise-driven spiking networks.

### 2.6 Null models and cross-validation protocol (summary of theme 7)

- *Degree-preserving rewiring* (Maslov–Sneppen): repeatedly pick edges (a→b), (c→d) and swap targets to (a→d), (c→b) if no self-loop/multi-edge arises; keeps each node's in- and out-degree (`[V-abs·W]` for the idea; the swap step `[MEM]`). For us also keep (i) presynaptic neurotransmitter sign (Dale's law), (ii) a weight-distribution constraint (weights are synapse counts, not 0/1; permute weights among swapped edges or rewire at synapse level), (iii) source/target membership (swapping edges across the source and target sets changes the question). Variants: strength-preserving weighted nulls, maximum-entropy ensembles (Squartini–Garlaschelli `[V-abs·W]`), spatially constrained nulls (Roberts, Burt `[V-abs·W]`).
- Choose the null to match the claim: a *degree-preserving* null tests whether a predictor adds information beyond degree sequences; a *geometry-preserving* null tests whether it adds beyond spatial embedding; a *type-label-permuting* null tests whether it adds beyond cell-type-level structure. The controllability critique (Tu et al. 2018 `[V-abs·W]`) is the cautionary example.
- *Grouped CV* (Roberts 2017 `[V-abs·W]`): leave out whole cell types, hemisphere-pairs, or neuropil blocks, so test neurons share no type or homolog with training neurons. Report the performance drop vs random-fold CV as a leakage diagnostic (Kapoor & Narayanan 2023 `[V-abs·W]`).
- *Regression on node-pairs*: MRQAP-style permutation (Dekker et al. 2007 `[V-abs·W]`) for pair-level predictors (e.g., ε vs structural relation).
- *Multiple comparisons*: pre-register the pair list; Benjamini–Hochberg FDR or max-T permutation `[MEM]`.

---

## 3. Established vs open: what network theory says about structure → lesion impact

### 3.1 Established (with the strength of our evidence)

1. **Structure partially predicts dynamical lesion impact in brain-network models.** Central/hub nodes tend to cause larger global disruption; location matters; structural predictors explain only part of the variance (Honey & Sporns 2008, Alstott 2009; `[V-abs·W]`). Those results are *global* measures (FC, integration), in models built from the same connectivity (circularity).
2. **Hub-based predictors are system- and mechanism-dependent.** Centrality–lethality in yeast PPI is real but its mechanism is contested (essential interactions vs essential modules; He & Zhang 2006, the 2008 reanalysis, Batada 2006; `[V-abs·W]`); scale-free networks fail under targeted hub attack but tolerate random failure (Albert 2000); in brain networks the picture is "remarkably resilient" (Aerts 2016).
3. **Path-based and walk-based predictors beat plain degree**: edge frequency in shortest paths for edge vulnerability (Kaiser & Hilgetag 2004); communicability/navigation beat raw SC for behaviour and structure–function coupling (Seguin 2020 `[V-abs·C]`); k-shell/percolation beat degree for spreading (Kitsak, Morone & Makse). Which predictor wins depends on the dynamics.
4. **Single-lesion effects mislead under redundancy; multi-perturbation attribution (MSA) is the axiomatic remedy** (Keinan 2004, Kaufman 2005, Fakhar & Hilgetag 2022; `[V-abs·W]`). Activity and causal contribution can dissociate through downstream transformations (Fakhar 2024 `[V-abs·W]`). Selectivity/hub status is a poor predictor of overall importance in ANNs (Morcos 2018 `[V-abs·C]`) but a good one of class-specific importance (Zhou 2018 `[V-abs·C]`).
5. **Degeneracy ≠ redundancy; compensation is the rule.** Degeneracy/redundancy measures (Tononi 1999 `[V-abs·C]`), many parameter sets giving one output (Prinz 2004 `[V-abs·W]`), compensation/homeostasis (Marder & Goaillard 2006 `[V-abs·C]`).
6. **"Interaction" is scale-dependent.** Mani 2008 `[V-abs·C]` shows four neutrality functions classify differently (Min called 52% of known yeast synergies); Wang 2010, Chitra 2025, Katagiri 2023 `[V-abs·C]` extend this to measurement scale and higher order. Between-pathway vs within-pathway explanations of genetic interactions (Kelley & Ideker 2005 `[V-abs·C]`) are testable against networks, and between-pathway explanations were better in real data.
7. **Epistasis can be computed on a mechanistic network model and shows modular structure** (Segrè 2005 `[V-abs·W]`), a precedent for model-first work.
8. **Max-flow/min-cut/vertex-cut tools are textbook** (Menger, Freeman 1991), and have been applied to connectome graphs in at least five ways: global strong connectivity (Daugulis 2016), subject-level abnormality detection (Irzan 2020), real-time min-cut sensitivity to node removal in human connectomes (Li 2026), influence-share bottlenecks in the fly (Ganguly abstract), and a public max-flow/min-cut-then-silence repo on the male fly CNS (§1, 5.12). Flow-based **double ablations** on a connectome exist for the worm (Bacik 2016), as do control-theoretic **pair and triplet ablations framed as synthetic lethality** (Towlson & Barabási 2020).
9. **Linear response gives structure → correlation/response with operating-point dependence** (Trousdale 2012), with a known nonlinear failure mode (Ocker 2017).
10. **Controllability-style structure→function claims need null models and ablation validation** (Yan 2017 vs Tu 2018). **Anatomy is a weak predictor of measured functional influence in the worm** (Randi 2023).

### 3.2 Prior art that pre-empts, in whole or part, H-A, H-B, H-C (decision-relevant)

| Hypothesis | Nearest prior art found | What it already covers | What remains unclaimed (given our searches) |
|---|---|---|---|
| **H-A** (task-specific flow > global centrality; ladder up to operating-point linear response) | `fly-bottlenecks` repo (5.12, `[V-src]`): min-cut set vs path-betweenness vs PageRank vs out-strength vs random, silenced in a Shiu-parameter LIF model, taste → MN9, male CNS; Ganguly bottleneck-neuron abstract (5.9); Kaiser & Hilgetag 2004 path-frequency vs degree; Seguin communication models; Pospisil 2024 effectome | **The headline "task-specific cut/flow beats global centrality for abolishing a target's output" at the level of a ~34-neuron set, in an LIF model, on a Shiu-type readout (MN9), including the PageRank/out-strength null results.** Not peer-reviewed, one stimulus, FlyWire not used, set-level only. | (i) *single-neuron* necessity prediction (rank quality, AUC) rather than a set cut; (ii) the **ladder** with operating-point-aware linear response (I−DW)⁻¹ and the quantified nonlinear residual; (iii) FlyWire v783 and the original Shiu code; (iv) multi-intensity/dose-response; (v) grouped CV and nulls. **Reframe H-A as the ladder and its residual, not as "flow beats centrality".** |
| **H-B** (threshold-margin theory; abolition vs sensitivity-shift phenotypes) | Watts 2002 (threshold cascades); CTLN graph rules; Kacser–Burns 1981 (flux-sharing, haplosufficiency analogy); Trousdale 2012 (operating-point dependence of linear response); the 2025 FlyWire preprint (3.10) on distributed redundancy for escape/feeding | General threshold-network theory; the idea that effects depend on the operating point; redundancy seen in a Shiu-type model by combinatorial silencing (no theory of margins, no dose-response taxonomy seen). | A **margin-based, dose-response (EC50 shift vs plateau loss) theory for necessity in a thresholded spiking connectome model**: no peer-reviewed match found (query #94, extended, plus #80 and #64). Treat as unclaimed but **weakly searched**. |
| **H-C** (neural epistasis; between- vs within-pathway; max-flow inclusion–exclusion predictor) | Towlson & Barabási 2020 ("synthetic essential" neuron pairs, network control, worm); Bacik 2016 (supra-additive double ablations, flow structure); Kaufman 2005 and Keinan 2004 (MSA 2-D interactions on neural circuits and genetic data); Kelley & Ideker 2005 (between/within-pathway); Segrè 2005; Kim et al. (pairwise redundancy by path compensation, C. elegans) | **The framing "neuron pairs jointly but not singly essential = synthetic lethality analogue"**, structural-only criteria for it, pairwise ablation screens in a connectome, and Shapley interaction analysis of neural data. | A **dynamics-based (spiking) pair screen with a stated neutrality function (Mani), classification into between-pathway synergy vs within-pathway masking, and a flow-based (Menger inclusion–exclusion) predictor, benchmarked against a structure-only (Towlson-type) predictor**, with the threshold/flow-additivity issue made explicit (§2.3). Must cite Towlson & Barabási 2020 and Bacik 2016 as nearest prior art. No source found for between/within-pathway pair framing on neurons. |
| **H-D** (task specificity) | Zhou 2018 (class-level vs overall importance); Morcos 2018; Kaiser/Hilgetag edge-frequency (all-pairs vs specific) | The general point that importance is task-conditional and that selectivity/hubness does not give overall importance. | Neuron-resolved, multi-task necessity overlap in a connectome model. (LIT-A/NOV scope.) |
| **H-E** (external validity) | Yan 2017 (prediction → ablation, worm), Tu 2018 (critique), Randi 2023 (anatomy ≠ function), Seguin stimulus-propagation study (held-out sites) | The design template for validated structural predictions, and the warnings: null-model controls, neuromodulation/extrasynaptic blind spots, compensation | Fly experimental validation (LIT-C). |

### 3.3 Open (not established by what we found)

- **Whether any compression of W** (degree, path-based flow, communicability, linear response) predicts *single-neuron* necessity in a **thresholded, spiking, signed** model beyond baseline activity and distance to the output; the existing evidence is for continuous/oscillator models (Alstott), structural vulnerability (Kaiser), or set-level cuts (fly-bottlenecks).
- **How operating point (drive, noise, cell gains) reorders necessity**; the linear-response literature says correlations depend strongly on it (Trousdale), but no necessity-ranking analysis was found.
- **A theory linking margins to abolition vs sensitivity-shift phenotypes** (H-B), and a defensible scalar for "redundancy" that is stable across operating points.
- **Non-additivity classification of pairs** by structural relation (series, parallel, shared target) with a stated neutrality function, and how well max-flow inclusion–exclusion (additive) can anticipate threshold-induced synergy.
- **Which null model is the right control** for source→target flow predictors (degree-preserving, geometry-aware, type-preserving) in a connectome with Dale's-law signs.
- **Circularity**: whether model-necessity ↔ structure agreement says anything about biology when W defines both; only external data (LIT-C), other connectomes, and homolog replication can break it; left–right homologs are partially redundant by design (3.9).
- **Compensation/homeostasis** in the real fly (acute vs chronic silencing) vs the static model (3.5).
- **Statistical practice**: grouped CV by type/homolog, handling ~10⁴–10⁸ candidate pairs, noise floors for ε.

---

## 4. Unconfirmed leads (not in the main bibliography)

| ID | Lead | Why unconfirmed |
|---|---|---|
| U-1 | Gu S, Pasqualetti F, Bassett DS, et al. (2015) *Nature Communications*, "Controllability of structural brain networks" | Mentioned only as the target of Tu et al. 2018's critique (`[V-abs·W]`); a direct search (#89) did not return the paper itself. Title and authors are `[MEM]`. |
| U-2 | Keinan A, Sandbank B, Hilgetag CC, Meilijson I, Ruppin E (2006) *Artificial Life* 12(3):333–352, "Axiomatic scalable neurocontroller analysis via the Shapley value" | Appears as a citation in the msapy README `[V-src]`; the paper itself was not searched. |
| U-3 | Male-CNS *Cell* 2026 paper "ran maximum flow analysis" (sensory modality × motor domain, neck connective bottleneck) | Two of three WebSearch syntheses say so, one does not; no abstract text seen mentioning it. Existence and venue of the paper are confirmed (`[V-abs·W]`), the max-flow component is not. PI/NOV should read the Methods. |
| U-4 | Deutscher, Ruppin et al. "multi-perturbation Shapley value analysis of yeast metabolism" | The title was not found; the 2006 *Nature Genetics* paper (4.5) is "Multiple knockout analysis of genetic robustness in the yeast metabolic network". Whether MSA was used there is `[MEM]`. |
| U-5 | Wunderlich & Mirny (2006), Palumbo et al., Papp, Pál & Hurst (2004): topology vs flux-balance essentiality prediction in metabolic networks | query #52 did not return them. The related claim "topology fails for metabolic essentiality; FBA+topology works better" came from an unattributed MIT DSpace record (https://dspace.mit.edu/handle/1721.1/59195) and a non-peer-reviewed preprint (Boone, arXiv 2507.20406). |
| U-6 | Menger (1927); Ford & Fulkerson (1956) original theorems | Not searchable here; standard-text statements only (5.1). |
| U-7 | Pernice, Staude, Cardanobile & Rotter (2011) "How structure determines correlations in neuronal networks" *PLoS Comput Biol*; Hawkes-process linear-response papers | Not searched; `[MEM]` leads for the linear-response rung (theme 6). |
| U-8 | Benjamini & Hochberg (1995) FDR; max-statistic permutation tests | Not searched (theme 7.6). |
| U-9 | Betzel & Bassett, "Generative models for network neuroscience: prospects and promise" (title seen at PMC5721166; authors and venue not displayed) | Cite only after verification. |
| U-10 | Zotenko E, et al. (2008) *PLoS Comput Biol*, challenge to He & Zhang; Batada et al. (2006) *PLoS Biol* on date hubs | Known only through a WebSearch synthesis of the He & Zhang record; the 2008 title is as seen but first-author and year are from the summary. |
| U-11 | Fakhar et al. (2025) *eLife* author list; Seguin et al. *Neuron* 2023 author list and publication details; Jonas & Kording volume year | Inconsistent or absent in search results. |
| U-12 | Distinct statements in Consensus records with internal inconsistencies: François et al. 2025 *eLife* (first author vs copyright line); Estrada & Hatano year (2007 vs 2008) | Needs the auditor. |
| U-13 | Any peer-reviewed full paper behind the Ganguly (Krell CSGF) bottleneck-neuron abstract; any journal version of `fly-bottlenecks` | Not found. |

---

## 5. Query log

**Tool key:** C = `mcp__Consensus__search`; W = `WebSearch` (std = standard, ext = extended); G = Bash `git clone` of a public GitHub repo (shallow). "RL" = Consensus rate-limited, no results returned.

| # | Tool | Query |
|---|---|---|
| 1 | C | Honey Sporns cortical lesion network structural lesion effects functional connectivity computational model (RL) |
| 2 | C | Alstott Breakspear Hagmann Cammoun Sporns modeling the impact of lesions in the human brain (RL) |
| 3 | C | Yan Vértes Barabási network control principles predict neuron function in the Caenorhabditis elegans connectome (RL) |
| 4 | W std | Multi-perturbation Shapley value analysis Fakhar Hilgetag downstream network transformations dissociate activity from causal contribution |
| 5 | W std | Honey Sporns 2008 "Dynamical consequences of lesions in cortical networks" Human Brain Mapping |
| 6 | W std | Alstott 2009 "Modeling the impact of lesions in the human brain" PLoS Computational Biology |
| 7 | W std | Yan 2017 Nature "Network control principles predict neuron function in the Caenorhabditis elegans connectome" |
| 8 | W std | Mani 2008 PNAS "Defining genetic interaction" multiplicative additive min log |
| 9 | C | Defining genetic interaction Product Additive Log Min definitions |
| 10 | W std | Keinan Sandbank Hilgetag Meilijson Ruppin "Fair attribution of functional contribution in artificial and biological networks" Neural Computation 2004 |
| 11 | W std | Kaufman Keinan Meilijson Kupiec Ruppin "Quantitative analysis of genetic and neuronal multi-perturbation experiments" PLoS Computational Biology 2005 |
| 12 | W std | Fakhar Hilgetag 2022 "Systematic perturbation of an artificial neural network: a step towards quantifying causal contributions in the brain" PLoS Computational Biology |
| 13 | C | Could a neuroscientist understand a microprocessor? (RL) |
| 14 | C | On the importance of single directions for generalization ablation class selectivity |
| 15 | C | Shapley interaction index game theory interaction between players (RL) |
| 16 | W std | msapy multi-perturbation Shapley value analysis python github |
| 17 | G | `git clone --depth 1 https://github.com/kuffmode/msa` (read README, `msapy/msa.py`, `pyproject.toml`, `LICENSE`; no code run) |
| 18 | W std | "Who Does What in Deep Learning? Multidimensional Game-Theoretic Attribution of Function of Neural Units" Fakhar Hilgetag Shapley |
| 19 | W ext | Fakhar Hilgetag Shapley value pairwise interaction brain regions lesion "network" 2025 causal contributions whole-brain model |
| 20 | C | Could a neuroscientist understand a microprocessor? (RL, second attempt) |
| 21 | C | Jonas Kording could a neuroscientist understand a microprocessor lesion transistors |
| 22 | W std | Fakhar Hilgetag "A general framework for characterizing optimal communication in brain networks" eLife abstract |
| 23 | W std | Randi Sharma Dvali Leifer "Neural signal propagation atlas of Caenorhabditis elegans" Nature 2023 anatomy functional connectivity |
| 24 | W std | Seguin Sporns Zalesky "Brain network communication: concepts, models and applications" Nature Reviews Neuroscience 2023 |
| 25 | C | max-flow min-cut connectome neurons minimum cut structural connectivity |
| 26 | W std | connectome node-disjoint paths vertex connectivity Menger theorem neurons redundancy C. elegans OR Drosophila OR mouse |
| 27 | W std | dominator tree neural network connectome sensory to motor bottleneck neurons graph |
| 28 | W std | Seguin Mansour Sporns Zalesky Batista-Garcia "Network communication models narrow the gap between the modular organization of structural and functional brain networks" OR "communication models predict stimulation propagation" Neuron 2023 |
| 29 | W std | Ganguly "bottleneck neurons" Drosophila hemibrain connectome pathway influence source target algorithm |
| 30 | C | network communication models predict propagation of electrical stimulation human brain intracranial structural connectome |
| 31 | C | Schlegel Bates Jefferis olfactory connectome information flow Drosophila synaptic pathway analysis (RL) |
| 32 | W std | Daugulis "Strong connectivity and its applications" arXiv 1609.07355 connectome abstract |
| 33 | C | Schlegel Bates Jefferis Synaptic transmission parallels neuromodulation in a central food-intake circuit OR "Information flow, cell types and stereotypy in a full olfactory connectome" (RL) |
| 34 | C | Aerts Fias Caeyenberghs Marinazzo brain networks under attack robustness properties and the impact of lesions (RL) |
| 35 | C | Estrada Hatano communicability in complex networks |
| 36 | W std | Schlegel 2021 eLife "Information flow, cell types and stereotypy in a full olfactory connectome" information flow algorithm |
| 37 | W std | Aerts 2016 "Brain networks under attack: robustness properties and the impact of lesions" Brain |
| 38 | W std | Kaiser Hilgetag 2004 "Edge vulnerability in neural and metabolic networks" Biological Cybernetics |
| 39 | W std | Tu Rocha Gu "Warnings and caveats in brain controllability" NeuroImage |
| 40 | W std | Yan 2017 C. elegans controllability critique Tang Wang "structural controllability" connectome neurons ablation reanalysis |
| 41 | C | Tononi Sporns Edelman measures of degeneracy and redundancy in biological networks |
| 42 | W std | Edelman Gally 2001 "Degeneracy and complexity in biological systems" PNAS |
| 43 | W std | Price Friston 2002 "Degeneracy and cognitive anatomy" Trends in Cognitive Sciences |
| 44 | W std | Prinz Bucher Marder 2004 "Similar network activity from disparate circuit parameters" Nature Neuroscience |
| 45 | C | Marder Goaillard variability, compensation and homeostasis in neuron and network function (response: "1 credit left this month") |
| 46 | W std | Albert Jeong Barabási 2000 "Error and attack tolerance of complex networks" Nature |
| 47 | W std | Jeong Mason Barabási Oltvai 2001 "Lethality and centrality in protein networks" Nature |
| 48 | W std | He Zhang 2006 "Why do hubs tend to be essential in protein networks?" PLoS Genetics |
| 49 | W std | Segrè DeLuna Church Kishony 2005 "Modular epistasis in yeast metabolism" Nature Genetics |
| 50 | W std | Deutscher Ruppin Kupiec "Multi-perturbation Shapley value analysis of yeast metabolism" OR "Multiple knockout analysis of genetic robustness in the yeast metabolic network" Nature Genetics 2006 |
| 51 | W std | Costanzo 2010 "The genetic landscape of a cell" Science genetic interaction map yeast |
| 52 | W std | flux balance analysis gene essentiality prediction versus network centrality metabolic network Wunderlich Mirny OR Palumbo OR "Papp Pál Hurst" |
| 53 | W std | Freeman Borgatti White 1991 "Centrality in valued graphs: A measure of betweenness based on network flow" Social Networks |
| 54 | W std | Newman 2005 "A measure of betweenness centrality based on random walks" Social Networks |
| 55 | W ext | maximum flow connectome Drosophila OR "C. elegans" neurons "max-flow" OR "maximum flow" OR "minimum cut" sensory motor pathway neurons critical |
| 56 | G | `git clone --depth 1 https://github.com/danilo-lazovic/fly-bottlenecks` (read README, PROJECT_CONTEXT.md, grep of `src/sim.py`; no code run) |
| 57 | W std | "Sexual dimorphism in the complete Drosophila male central nervous system connectome" Cell maximum flow sensory motor neck connective |
| 58 | W std | "Flow-Based Network Analysis of the Caenorhabditis elegans Connectome" PLoS Computational Biology Kunert-Graf Shlizerman Kutz |
| 59 | W ext | "maximum flow" analysis male CNS connectome sensory modality motor domain "weakest link" neck connective neurons bioRxiv |
| 60 | W std | Sabrin Kim Dovrolis "The hourglass organization of the Caenorhabditis elegans connectome" PLoS Computational Biology 2020 |
| 61 | W std | Bacik Schaub Beguerisse-Díaz Billeh Barahona flow-based C. elegans connectome single and double neuron ablations disrupt flow structure abstract |
| 62 | W std | Trousdale Hu Shea-Brown Josić 2012 "Impact of network structure and cellular response on spike time correlations" PLoS Computational Biology |
| 63 | W std | Ocker Josić Shea-Brown Buice 2017 "Linking structure and activity in nonlinear spiking networks" PLoS Computational Biology |
| 64 | W std | Curto Morrison "Graph rules for recurrent neural network dynamics" combinatorial threshold-linear networks Notices AMS OR "Pattern completion in symmetric threshold-linear networks" |
| 65 | W std | Curto Geneson Morrison "Fixed points of competitive threshold-linear networks" Neural Computation 2019 |
| 66 | W std | Váša Mišić "Null models in network neuroscience" Nature Reviews Neuroscience 2022 |
| 67 | W std | Maslov Sneppen 2002 "Specificity and stability in topology of protein networks" Science degree-preserving rewiring |
| 68 | W std | Squartini Garlaschelli "Analytical maximum-likelihood method to detect patterns in real networks" New Journal of Physics 2011 OR "Reconnecting statistical physics and combinatorics beyond ensemble equivalence" directed weighted maximum entropy |
| 69 | W std | Roberts Mitchell Breakspear 2016 "The contribution of geometry to the human connectome" OR Betzel Bassett "Generative models for network neuroscience: prospects and promise" spatial null models |
| 70 | W std | Roberts 2017 "Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure" Ecography blocked cross-validation |
| 71 | W std | Kapoor Narayanan "Leakage and the reproducibility crisis in machine-learning-based science" Patterns 2023 |
| 72 | W std | Dekker Krackhardt Snijders 2007 "Sensitivity of MRQAP tests to collinearity and autocorrelation conditions" Psychometrika network regression node-level permutation |
| 73 | W std | Burt Helmer Murray "Generative modeling of brain maps with spatial autocorrelation" NeuroImage 2020 brainSMASH OR Alexander-Bloch spin test |
| 74 | W ext | double neuron ablation synergistic redundancy connectome model "pairwise" lesions non-additive effects network neuroscience epistasis between neurons |
| 75 | W std | Toba Hilgetag "Game theoretical mapping of causal interactions underlying visuo-spatial attention in the human brain based on stroke lesions" Human Brain Mapping 2017 |
| 76 | W ext | synthetic lethality analogy neural circuits combinatorial silencing "genetic interaction" neurons Drosophila connectome pairwise silencing screen |
| 77 | W std | "Synthetic ablations in the C. elegans nervous system" arXiv 1907.11297 abstract |
| 78 | W std | "Bilateral Neuron Pairs Share Redundant Network Roles Despite Incomplete Connection Symmetry in Caenorhabditis elegans" abstract path compensation |
| 79 | W std | "Whole-brain connectomics of Drosophila reveals a robust, distributed architecture for the suppression of feeding during escape" abstract |
| 80 | W std | Watts 2002 "A simple model of global cascades on random networks" PNAS threshold |
| 81 | W std | Morone Makse 2015 "Influence maximization in complex networks through optimal percolation" Nature collective influence |
| 82 | W std | Kitsak 2010 "Identification of influential spreaders in complex networks" Nature Physics k-shell |
| 83 | W std | Feizi Marbach Médard Kellis 2013 "Network deconvolution as a general method to distinguish direct dependencies in networks" Nature Biotechnology |
| 84 | W std | Grabisch Roubens 1999 "An axiomatic approach to the concept of interaction among players in cooperative games" International Journal of Game Theory |
| 85 | W std | Sundararajan Dhamdhere Agarwal "The Shapley Taylor Interaction Index" ICML 2020 |
| 86 | W std | Lengauer Tarjan "A fast algorithm for finding dominators in a flowgraph" ACM TOPLAS 1979 dominator tree |
| 87 | W std | dominator tree OR "dominator nodes" biological network signaling regulatory essential nodes source target all paths pass through |
| 88 | W std | Seguin Tian Zalesky "Communication dynamics in the human connectome shape the cortex-wide propagation of direct electrical stimulation" Neuron 2023 |
| 89 | W std | Liu Slotine Barabási 2011 "Controllability of complex networks" Nature; Gu Pasqualetti Bassett 2015 "Controllability of structural brain networks" Nature Communications |
| 90 | W std | Phillips 2008 "Epistasis — the essential role of gene interactions in the structure and evolution of genetic systems" Nature Reviews Genetics; Baryshnikova 2010 "Quantitative analysis of fitness and genetic interactions in yeast on a genome scale" Nature Methods |
| 91 | W std | Kaiser Martin Andras Young 2007 "Simulation of robustness against lesions of cortical networks" European Journal of Neuroscience |
| 92 | W std | Avena-Koenigsberger Mišić Hawkins Griffa Hagmann Goñi Sporns "Path ensembles and a tradeoff between communication efficiency and resilience in the human connectome" Brain Structure and Function |
| 93 | W std | Avena-Koenigsberger Misic Sporns "Communication dynamics in complex brain networks" Nature Reviews Neuroscience 2018 |
| 94 | W ext | neural circuit redundancy threshold margin silencing neuron effect depends on stimulus intensity operating point dose-response shift versus abolition connectome-constrained spiking model |
| 95 | W std | Kacser Burns 1981 "The molecular basis of dominance" Genetics metabolic control flux summation theorem |
| 96 | W std | Foucquier Guedj 2015 "Analysis of drug combinations: current methodological landscape" Bliss independence Loewe additivity synergy definitions |
| 97 | W std | Pospisil Aguirre Cadena? "The fly connectome reveals a path to the effectome" Nature 2024 linear response connectome-constrained predicts functional connectivity |

_Note on counts:_ the log above lists 97 calls (Consensus 17 including 9 rate-limited; WebSearch 78 including 6 extended and 72 standard; 2 `git clone`s). The count line in §0 ("78 queries") refers to WebSearch calls only. The Consensus results returned in #9, #14, #21, #25, #30, #35, #41 and #45 supply the `·C` tags.
