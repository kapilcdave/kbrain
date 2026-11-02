# Opportunities

Things worth building, betting on or doing next. Format: what, why now, evidence (cite), rough cost, next step.

### 1. CPU-Native Protein Engineering Suite (`kbrain-predict`)
- **What:** An open-source, zero-GPU command-line tool and Python package for zero-shot mutation-effect scoring
  combining GEMME (MSA spectral analysis) and ESM2-35M with automated alignment retrieval (ColabFold/MMseqs2).
- **Why now:** ESM2-650M is treated as the default baseline in academic wet-labs, but requires dedicated GPU
  infrastructure (>16GB VRAM) that most protein engineering benches lack. GEMME alone beats ESM2-650M (0.4743 vs 0.4382)
  on ProteinGym v1.3 without touching a GPU.
- **Evidence:** ProteinGym v1.3 leaderboard (`leaderboard_spearman_DMS_level.csv`), Laine et al. 2019 (MBE).
- **Rough cost:** Zero cloud spend; 2-3 engineering shifts on our local CPU machine.
- **Next step:** Validate candidate experiment C6; if CI > 0 over ESM2-650M, package the runner into `lab/`.

### 2. Retrieval-Augmented Fitness Scoring for Commercial Enzymes
- **What:** Service / workflow offering high-resolution DMS ranking for industrial enzyme optimization (thermostability,
  catalytic turnover) using structure-quantized retrieval (VenusREM / ProSST + MSA fusion).
- **Why now:** Top-tier models on ProteinGym have crossed 0.53 Spearman by fusing structure tokens and evolutionary
  retrieval, reducing the screening library size needed by protein engineers by >50%.
- **Evidence:** VenusREM achieves 0.5357 on ProteinGym; demonstrated wet-lab validation on polymerases and VHH antibodies.
- **Rough cost:** CPU evaluation of existing models; minimal inference cost.
- **Next step:** Benchmark published VenusREM / ProSST scores against low-N experimental data to quantify hit rate reduction.

### 3. Automated MaveDB Ingestion Engine for Novel DMS Targets
- **What:** Lightweight automated pipeline to monitor MaveDB for newly published DMS experiments (`urn:mavedb`),
  extract wild-type sequences, fetch ColabFold AlphaFold2 structures, format cross-validation folds, and score zero-shot
  predictions using our CPU suite before targets appear in official benchmark releases.
- **Why now:** ProteinGym benchmark updates are infrequent (v1.0 in 2022, v1.3 in 2023), but MaveDB depositions are
  continuous (>400 experiments; dozens added annually for emerging viral variants, antibody escape, and therapeutic enzymes).
- **Evidence:** MaveDB API (Rubin et al., Genome Biol 2024); AVE Alliance standards.
- **Rough cost:** Zero GPU; purely automated API polling, sequence parsing, and CPU inference.
- **Next step:** Write a Python scraper to query the MaveDB REST API for assays with complete sequence maps and valid UniProt accessions.

### 4. Low-N Active Learning Auditor for Protein Engineering Platforms
- **What:** An open evaluation toolkit and rigorous benchmarking harness that stress-tests commercial active learning
  claims (e.g., directed evolution in 24–96 variants per round) against strict negative controls: frozen zero-shot priors,
  position-disjoint splits (`fold_contiguous_5`), and simple random mutant selection across ProteinGym's 217 assays.
- **Why now:** Startups like Cradle Bio sell SaaS subscriptions promising rapid fitness optimization with minimal wet-lab
  measurements. However, prospective wet-lab customers lack vendor-neutral tools to verify whether complex active learning
  algorithms genuinely beat simple zero-shot ranked screening under realistic experimental noise and position-unseen constraints.
- **Evidence:** The kbrain [augmented low-N regression finding](findings/augmented-low-n-regression.md) passed its
  random-split endpoint (+0.00994 mean per-protein Spearman; 95% CI [+0.00451, +0.01570]) but was null in
  single-mutant-dominated proteins (+0.00071; 95% CI [-0.00393, +0.00474]). This demonstrates why an auditor
  must separate random-split gains from position-unseen design claims. Data and folds: ProteinGym v1.3
  ([Notin et al., arXiv:2306.12204](https://arxiv.org/abs/2306.12204)); augmentation precedent:
  [Hsu et al., 2022, DOI:10.1038/s41587-021-01146-5](https://doi.org/10.1038/s41587-021-01146-5).
- **Rough cost:** Zero cloud spend; purely analytical evaluation using `pg.low_n` and `lab/proteingym.py`.
- **Next step:** Run a frozen, single-substitution-only evaluation on ProteinGym's fixed `fold_contiguous_5`
  splits, with all test positions absent from training and paired improvements clustered by UniProt protein.

### 5. Epistasis & Multi-Mutant Audit Suite for Commercial Protein LLMs
- **What:** A vendor-neutral benchmarking tool and audit report that stress-tests commercial foundation models
  and PLMs on non-additive epistasis, using ProteinGym's 69 multi-mutant assays (~1.77M variants) and the Kalinina
  lab epistasis metric framework.
- **Why now:** Kolchina et al. (bioRxiv Feb 2026) and Woolley et al. (bioRxiv Jun 2026) proved that broad single-mutation
  leaderboards mask catastrophic prediction failure on multi-mutant epistatic combinations. Biotech and pharma teams
  licensing foundation models for combinatorial protein optimization need objective verification of whether a model
  captures real physical epistasis or merely computes trivial additive sums of single-site log-odds.
- **Evidence:** Kolchina et al., 2026 ([bioRxiv:10.64898/2026.02.17.706292](https://doi.org/10.64898/2026.02.17.706292));
  Woolley et al., 2026 ([bioRxiv:10.64898/2026.06.04.730121](https://doi.org/10.64898/2026.06.04.730121)).
- **Rough cost:** Zero GPU spend; analytical scoring over pre-computed published predictions on our 8-core CPU.
- **Next step:** Execute Candidate C8 across the 69 multi-mutant assays in `lab/` to establish exact quantitative
  degradation deltas for GEMME vs ESM2-650M under strong epistatic regimes.

### 6. Forward-Validated 24-Label Model Router
- **What:** A dry-run decision layer that uses an initial batch of 24 measured mutants to choose or weight
  frozen GEMME and ESM2-650M scores for the remainder of a target's mutation library.
- **Why now:** The frozen hard-selection rule has passed a protein-clustered ProteinGym benchmark, while its
  negative label-shuffle control shows that the gain depends on real label-model association. The result is
  not ready for operational use because it has only been tested with random within-assay splits.
- **Evidence:** The kbrain
  [label-efficient model-selection finding](findings/label-efficient-model-selection.md) reports a
  **+0.01645** mean per-protein held-out Spearman gain over GEMME (95% CI **[+0.00776, +0.02608]**;
  186 proteins). A label-free blend gained **+0.01583**, and secondary softmax weighting gained **+0.03183**,
  so a forward test must compare all frozen alternatives. Data and protocol are based on ProteinGym v1.3
  ([Notin et al., arXiv:2306.12204](https://arxiv.org/abs/2306.12204)); model references are GEMME
  ([Laine et al., 2019](https://doi.org/10.1093/molbev/msz179)) and ESM2
  ([Lin et al., 2023](https://doi.org/10.1126/science.ade2574)).
- **Rough cost:** Zero cloud spend for packaging and a replay-only dry run on published scores. For one
  completely unseen target lacking published ESM2-650M scores, propose a hard ceiling of **$25** for GPU
  inference after the target, sequence length, mutation library, provider, and exact quote are fixed; no
  resource may be created without operator approval.
- **Next step:** Identify one public, wholly unseen DMS target; preregister the target-level holdout and the
  hard-selection, softmax, static-blend, and GEMME procedures before inspecting its labels. Request operator
  approval separately if generating ESM2-650M scores would incur any spend.

### 7. Subspace-Accelerated Low-N Screening for Directed Evolution
- **What:** A lightweight, CPU-native antibody and enzyme engineering workflow that fits a Linear Fitness Subspace (LFS)
  over small PLM embedding deltas (ESM2-35M / SaProt-35M) using an initial round of 24–48 experimental measurements,
  guiding round-2 candidate acquisition without GPU fine-tuning.
- **Why now:** Commercial wet-labs typically measure 24–96 variants in round 1. Standard tools either fit brittle
  unregularized regressors that fail on unseen positions, or rely on static zero-shot rankings that cannot incorporate
  experimental assay specifics. Ma et al. (Oct 2026) proved that a 5–10 dimension subspace recovered via PLS captures
  fitness variation with sample efficiency that beats high-dimensional neural networks.
- **Evidence:** Ma et al. 2026 ([arXiv:2610.07607](https://arxiv.org/abs/2610.07607)); kbrain low-N benchmark results
  ([augmented-low-n-regression.md](findings/augmented-low-n-regression.md)).
- **Rough cost:** Zero GPU spend; pure closed-form scikit-learn PLS/Ridge inference on 8-core CPU.
- **Next step:** Execute Candidate C11 across ProteinGym `fold_contiguous_5` splits to determine whether subspace
  projection achieves a statistically positive CI over unassisted zero-shot priors on position-disjoint splits.

### 8. Independent Structure-Token Stability Replication
- **What:** A label-blind comparison of frozen SaProt-35M-AF2 and ESM2-35M scores on newly published, public
  stability mutation data, deliberately sampling non-proteolysis platforms and longer or multi-domain proteins.
- **Why now:** The parameter-matched comparison passed strongly on ProteinGym Stability, but 64 of 66 assays
  came from one cDNA-display proteolysis platform and the other two assays had a negative mean difference.
  Independent platform coverage is therefore the shortest path from a benchmark edge to an actionable model
  choice for stability campaigns.
- **Evidence:** The kbrain
  [structure-token Stability finding](findings/structure-tokens-stability-edge.md) reports a **+0.135743** mean
  per-protein Spearman improvement over ESM2-35M (95% CI **[+0.098878, +0.173060]**; 66 proteins), while
  limiting the claim to the Tsuboyama-heavy regime. Data context: Tsuboyama et al., 2023,
  [DOI:10.1038/s41586-023-06240-5](https://doi.org/10.1038/s41586-023-06240-5); model reference: Su et al.,
  2024, [bioRxiv:2023.10.02.560515](https://doi.org/10.1101/2023.10.02.560515).
- **Rough cost:** Zero cloud spend for target discovery, preregistration, and replay where public scores and an
  open experimental or AlphaFold structure exist; expected local work is one research shift plus CPU scoring.
  Any paid structure generation or GPU inference requires a separate costed proposal and operator approval.
- **Next step:** Identify one public post-ProteinGym stability paper with mutation-level labels and a distinct
  assay platform; before reading labels, freeze target inclusion, score orientation, mutant coverage, the
  protein-level endpoint, and the same bootstrap settings used here.

### 9. Distogram-Derived Energetic Scoring for High-Throughput Stability Profiling
- **What:** An open-source scoring module implementing Distogram Encoded Energetic Potentials (DEEP) over modern
  biomolecular structure foundation models (Boltz-2), extracting zero-shot stability and $\Delta\Delta G$ proxies
  from predicted residue-pair distograms without experimental stability training.
- **Why now:** Rózsa & Erdős (bioRxiv Oct 2026) demonstrated that DEEP-Boltz achieves **0.720** mean per-assay Spearman
  across 64 ProteinGym stability assays, numerically outperforming all 97 published zero-shot methods on the benchmark.
  Protein design teams currently spend days running physics engines (FoldX, Rosetta) or fine-tuning supervised regressors;
  extracting statistical potentials directly from structure prediction distograms bridges structural biology and fitness ranking.
- **Evidence:** Rózsa & Erdős, 2026 ([bioRxiv:10.64898/2026.10.15.759389](https://doi.org/10.64898/2026.10.15.759389));
  ProteinGym v1.3 stability benchmark.
- **Rough cost:** Zero cloud spend if evaluating published distograms or cached representations; local CPU scoring costs minutes.
  Any full Boltz structure generation requires a separate costed GPU proposal and operator approval.
- **Next step:** Audit the DEEP open repository; verify whether pre-computed Boltz-2 distograms exist for ProteinGym targets
  or assess feasibility of lightweight CPU extraction.

### 10. Inference-Time Uncertainty Calibration for Small Enterprise PLMs
- **What:** A lightweight CPU-native inference wrapper for small protein language models (ESM2-35M, SaProt-35M) that performs
  test-time Monte Carlo dropout ($p=0.1$) between the featurizer and transformer blocks, returning both a variance-reduced
  fitness prediction and an epistemic uncertainty estimate per mutant.
- **Why now:** Wet-lab protein engineering teams using local CPU workstations cannot host 650M–3B parameter models, yet standard
  ESM2-35M point predictions underperform by ~0.12 Spearman compared to ESM2-650M. Ravuri & Lawrence (arXiv Jun 2025) proved
  that test-time dropout boosts small PLM zero-shot Spearman correlations by up to ~22% without any fine-tuning. Adding epistemic
  uncertainty estimates enables active learning algorithms to distinguish between high-confidence candidates and exploratory designs.
- **Evidence:** Ravuri & Lawrence, 2025 ([arXiv:2506.14793](https://arxiv.org/abs/2506.14793)); ProteinGym v1.3 benchmark.
- **Rough cost:** Zero cloud spend; 1-2 engineering shifts to build the PyTorch CPU wrapper and evaluate across ProteinGym assays.
- **Next step:** Execute Candidate C12 on ProteinGym substitution assays to establish the exact CPU runtime and Spearman improvement
  delta on our 8-core CPU environment.

### 11. Forward-Validated Static Ensemble With a Viral Safeguard
- **What:** A label-blind decision rule for new DMS targets that compares frozen GEMME-only scoring, an
  unconditional 50/50 GEMME/ESM2-650M rank blend, and a predeclared taxon-aware rule that excludes ESM2-650M
  on viral targets.
- **Why now:** The MSA-depth gate beat GEMME on ProteinGym but did not beat static blending, and randomized
  depth labels also passed. Taxonomy is a plausible alternative discriminator because ESM2-650M was much
  weaker than GEMME on viral assays, but that observation has not been prospectively tested.
- **Evidence:** The kbrain [MSA-depth gated-routing finding](findings/msa-depth-gated-routing.md) reports a
  **+0.013821** protein-level gain over GEMME for the gate (95% CI **[+0.008664, +0.019153]**) versus
  **+0.016038** for static blending; the direct gate-minus-static comparison was **-0.0022** (95% CI
  **[-0.0121, +0.0066]**). Data: ProteinGym v1.3
  ([Notin et al., arXiv:2306.12204](https://arxiv.org/abs/2306.12204)); models: GEMME
  ([Laine et al., 2019](https://doi.org/10.1093/molbev/msz179)) and ESM2
  ([Lin et al., 2023](https://doi.org/10.1126/science.ade2574)).
- **Rough cost:** Zero cloud spend when an unseen public assay has frozen GEMME and ESM2-650M scores; one
  research shift for target discovery, preregistration, and evaluation. If score generation requires paid GPU
  inference, stop and submit a provider-specific quote and hard spending cap for operator approval first.
- **Next step:** With operator approval, identify one wholly unseen public DMS paper and freeze target
  inclusion, taxonomy, score orientation, coverage checks, all three rules, the protein-level endpoint, and
  bootstrap settings before inspecting labels. Do not retune an MSA-depth threshold on ProteinGym.

### 12. Dynamics-Augmented Zero-Shot Fitness Engine (GNM-PLM)
- **What:** A CPU-native protein variant scoring engine combining small sequence PLMs (ESM2-35M / 8M) and GEMME with analytical Gaussian Network Model (GNM) normal mode analysis computed from AlphaFold2 structures.
- **Why now:** TriFit (Cho, arXiv:2604.12026, Apr 2026) showed that protein conformational dynamics provides the single largest marginal accuracy boost in mutation fitness prediction (AUROC 0.897). Unlike expensive molecular dynamics simulations, GNM normal mode analysis requires only an $L \times L$ contact Laplacian decomposition that runs in milliseconds on CPU, yielding physical residue flexibility and allosteric coupling metrics without GPU clusters.
- **Evidence:** Cho, 2026 ([arXiv:2604.12026](https://arxiv.org/abs/2604.12026)); Bahar et al., 1997 (Biophys J); ProteinGym v1.3 benchmark.
- **Rough cost:** Zero cloud spend; 1-2 engineering shifts to implement the SciPy C-alpha contact graph eigensolver and benchmark against ProteinGym targets.
- **Next step:** Execute Candidate C14 across the 186 ProteinGym UniProt targets using AlphaFold2 structures to measure the bootstrap Spearman improvement over unweighted baseline priors.

### 13. In-Context Few-Shot Learning Service for Rapid Wet-Lab Screening (TabPFN + PLM)
- **What:** An automated few-shot prediction service for wet-lab protein engineers that ingests 24–96 experimental measurements and delivers zero-training Bayesian fitness predictions for uncharacterized library variants using TabPFN/TabICL coupled with frozen PLM embeddings.
- **Why now:** Wet-lab teams executing directed evolution need fast iteration in 96-well plate cycles ($N \le 96$). Conventional supervised models (neural networks, fine-tuned PLMs) severely overfit on scarce labels, while standard ridge regression requires hyperparameter tuning and fails on unseen positions. Tabular in-context learners (Guan et al., arXiv:2606.31126, Jun 2026) evaluate frozen PLM embeddings in a single transformer forward pass on CPU, matching SOTA supervised regressors without gradient updates.
- **Evidence:** Guan et al., 2026 ([arXiv:2606.31126](https://arxiv.org/abs/2606.31126)); Hollmann et al., 2023 (Nature); ProteinGym few-shot benchmark.
- **Rough cost:** Zero GPU spend; fast CPU inference (<1 second per 96-variant plate).
- **Next step:** Execute Candidate C15 to establish whether TabPFN provides a statistically significant bootstrap gain over standard ridge regression under strict position-disjoint splits (`fold_contiguous_5`).

### 14. Asymmetric Zero-Shot Ensembling & Retrieval Middleware (VRH-Protein)
- **What:** A lightweight, training-free scoring middleware that ensembles evolutionary MSA representations (GEMME) and protein language models (ESM2-35M / 650M) using calibrated asymmetric scalar weighting and structural feature routing.
- **Why now:** Commercial protein engineering teams often default to equal rank ensembling or attempt complex residue-level conservation gating. kbrain's rigorous evaluation proved that simple asymmetric ensembling (80% GEMME + 20% ESM2-35M) provides a robust, zero-cost boost over standalone GEMME without requiring auxiliary profile calculations or fragile residue-level routing.
- **Evidence:** The kbrain [position-adaptive zero-shot fusion finding](findings/position-adaptive-zero-shot-fusion.md) showed that while cross-fitted sigmoid gating arithmetically beat an equal 50/50 blend (+0.029754, 95% CI [+0.020487, +0.038899]), the position-adaptivity mechanism failed all controls: a constant gate performed identically (+0.000877, 95% CI [-0.000319, +0.002093]), shuffled confidence gave 0.479787, and a simple position-blind 80/20 scalar blend achieved 0.480458, exceeding the adaptive gate without residue features. Tan et al., 2026 ([arXiv:2609.34654](https://arxiv.org/abs/2609.34654)); ProteinGym v1.3 benchmark.
- **Rough cost:** Zero cloud GPU spend; pure analytical combination running in milliseconds on CPU. Any forward evaluation on an unseen prospective DMS paper requires operator approval.
- **Next step:** Do not deploy residue-level profile gating. Instead, evaluate whether 3D structural metrics (AlphaFold2 residue pLDDT, relative solvent accessibility, contact density) provide real causal routing signal over the 80/20 scalar baseline, or validate the 80/20 blend on an unseen forward DMS publication held out from ProteinGym.

### 15. Composable Epistasis Profiler for Combinatorial Directed Evolution Libraries
- **What:** A predictive software service that takes low-order assay data (single and double substitutions from an initial 96-well screen) and builds a composable epistatic interaction atlas ($J_{ij}$) to predict higher-order mutational fitness and flag lethal epistatic clashes before library synthesis.
- **Why now:** Synthetic biology platforms and protein design teams frequently attempt 3- to 6-site combinatorial mutagenesis libraries, but over 80% of library variants are often completely non-functional due to negative sign epistasis. Cerebra-Epistasis (Wang et al., bioRxiv Sep 2026) demonstrated that composable residue-level mutation atlases accurately capture non-additive epistatic couplings from sparse low-order measurements, solving the failure mode of additive zero-shot PLMs at mutation depth $\ge 3$.
- **Evidence:** Wang et al., 2026 ([bioRxiv:10.1101/2026.09.28.679124](https://doi.org/10.1101/2026.09.28.679124)); ProteinGym multi-mutant benchmarks.
- **Rough cost:** Minimal compute; closed-form regularized interaction matrices ($L \times L \times 20 \times 20$ sparse tensor operations) executed on standard multi-core CPU.
- **Next step:** Execute Candidate C17 on ProteinGym combinatorial assays to determine the sample size $N$ of single/double mutants needed to reliably predict higher-order combinatorial fitness.

### 16. Chronological Campaign Replay Auditor for Enterprise Directed Evolution
- **What:** A prospective audit suite for biotechs running multi-round directed evolution that grades protein engineering ML models against historical campaigns using strict temporal replay rather than misleading random cross-validation.
- **Why now:** Gao et al. (arXiv:2606.02624, TadA-Bench) demonstrated that random CV splits overestimate prospective hit rates by 3–4x. Biotechs executing 24- or 96-well multi-round campaigns waste significant library synthesis budget on variants that fail in future rounds due to interpolation illusions.
- **Evidence:** Gao et al., 2026 ([arXiv:2606.02624](https://arxiv.org/abs/2606.02624)); ProteinGym low-N split diagnostics.
- **Rough cost:** Pure CPU analytical benchmarking; zero GPU or wet-lab spend.
- **Next step:** Construct an automated temporal replay evaluator using public multi-round directed evolution trajectories.

### 17. Thermodynamic Anti-Symmetry Enforcer for Biologics Stability & De-immunization
- **What:** A lightweight, model-agnostic mathematical wrapper that enforces physical forward-reverse anti-symmetry ($\Delta\Delta G_{A \to B} = -\Delta\Delta G_{B \to A}$) on any black-box protein stability or fitness predictor.
- **Why now:** Shivram et al. (arXiv:2606.08100) proved that state-of-the-art PLMs and structure models suffer from pervasive forward-reverse asymmetry, generating high rates of false-positive stabilizing mutations in therapeutic candidate optimization.
- **Evidence:** Shivram et al., 2026 ([arXiv:2606.08100](https://arxiv.org/abs/2606.08100)); MegaScale biophysical stability benchmarks.
- **Rough cost:** Zero GPU spend; closed-form linear algebraic anti-symmetrization executed on standard CPU.
- **Next step:** Execute Candidate C18 on the ProteinGym MegaScale stability assays to quantify the exact generalization uplift over unconstrained ridge regression.

### 18. Meta-Utility Predictor Router for Low-N Directed Evolution Campaigns (AssayRouter-Protein)
- **What:** An automated meta-routing service trained across hundreds of historical deep mutational scans that observes 24–48 experimental labels from an initial screening round and selects an optimal convex ensemble of frozen predictors (ESM-2, SaProt, GEMME) based on predicted post-fit marginal utility.
- **Why now:** Commercial directed evolution platforms (Cradle, Generate:Biomedicines, Arzeda) waste wet-lab rounds testing uncalibrated zero-shot predictors. Selecting models via support-set cross-validation on 24 labels is noisy and prone to overfitting. AssayRouter (Xu et al., arXiv:2609.37285, Sep 2026) proved that cross-assay historical utility priors outperform support-set CV by 0.0409 NLL across external regression benchmarks.
- **Evidence:** Xu et al., 2026 ([arXiv:2609.37285](https://arxiv.org/abs/2609.37285)); kbrain Candidate C2 findings.
- **Rough cost:** Zero GPU compute; fast linear meta-regression inference in milliseconds on CPU.
- **Next step:** Execute Candidate C20 on ProteinGym's 217 assays under leave-one-protein-out evaluation to benchmark against unregularized 24-label model selection.

### 19. Interface-Aware Geometric Adapter Service for Biologics Affinity Maturation (CIR-Engine)
- **What:** A plug-and-play geometric residual adapter that intercepts sequence PLM scores (ESM-2, SaProt) for antibody-antigen or viral receptor complexes and injects 22 interpretable cross-chain geometric contact descriptors.
- **Why now:** Biopharma affinity maturation campaigns frequently struggle with false-positive binding predictions from 1D sequence PLMs that cannot detect cross-chain steric clashes or interface contact densities. CIR-DDG (Yu et al., arXiv:2608.27530, Aug 2026) demonstrated that adding 22 explicit geometric descriptors boosts interface mutation correlation by +0.026 to +0.081 on SARS-CoV-2 RBD DMS without retraining base predictors.
- **Evidence:** Yu et al., 2026 ([arXiv:2608.27530](https://arxiv.org/abs/2608.27530)); SKEMPI 2.0 and ProteinGym binding benchmarks.
- **Rough cost:** Zero GPU compute; PDB contact extraction and linear adapter scoring on standard CPU.
- **Next step:** Execute Candidate C21 across ProteinGym's binding assays to quantify the bootstrap gain of explicit contact density correction over raw zero-shot PLM baselines.

### 20. Multi-Mutational Distance Decay Auditor for Protein Engineering Platforms (DeePEn-Audit)
- **What:** An automated audit service for biopharma directed evolution campaigns that evaluates variant fitness predictors specifically across mutational distance strata ($K=1, 2, 3, 4+$) rather than aggregate single-mutant correlations.
- **Why now:** Biotech teams designing multi-site enzyme variants frequently find that AI models boasting high ProteinGym scores ($\rho > 0.50$) fail completely when screening 3- to 5-site libraries. Schmirler et al. (DeePEn, bioRxiv 2026) and Kolchina et al. (bioRxiv 2026) proved that zero-shot PLM performance drops precipitously at $K \ge 3$ due to additive epistasis failure. An independent auditor that stress-tests candidate models against distance decay prevents costly synthesis failures.
- **Evidence:** Schmirler et al., 2026 ([bioRxiv:10.1101/2026.06.18.660142](https://doi.org/10.1101/2026.06.18.660142)); Kolchina et al., 2026 ([bioRxiv:10.1101/2026.02.12.637890](https://doi.org/10.1101/2026.02.12.637890)).
- **Rough cost:** Zero GPU compute; analytical stratification across ProteinGym multi-mutant assays in minutes on CPU.
- **Next step:** Execute Candidate C22 to construct baseline decay curves for all leading public models.

### 21. Constant-Memory Attention-Free PLM Inference Engine for Edge & Benchtop Scoring
- **What:** A lightweight, CPU-optimized deployment package and scoring daemon using recurrent multiplicative LSTM (mLSTM) protein language models (AINN-P1 style) that eliminates $O(L^2)$ attention matrices and KV-cache memory overhead.
- **Why now:** Wet-lab benches and clinical diagnostic sequencing devices need local, real-time variant scoring on long proteins without requiring high-memory GPU servers. AINN-P1 demonstrated that 167M-parameter mLSTM models match or exceed transformer PLMs on stability prediction with linear memory scaling and constant inference state size.
- **Evidence:** Ainnocence, 2026 ([bioRxiv:10.1101/2026.03.14.643210](https://doi.org/10.1101/2026.03.14.643210)); ProteinGym v1.3 stability benchmarks.
- **Rough cost:** Zero cloud spend; CPU runtime benchmarks and ONNX/C++ compilation on standard commodity hardware.
- **Next step:** Benchmark AINN-P1 CPU throughput and memory footprint against ESM2-35M on full-length titin and viral surface proteins.

### 22. Viable-Subspace Model Auditor & Lead Optimizer (ViableRank-Audit)
- **What:** A specialized auditing tool and commercial evaluation service that stress-tests foundation models (ESM-2, SaProt, Tranception) strictly within the viable functional subspace ($y \ge y_{\text{wt}}$ or top 50% fitness) rather than full-assay bimodal distributions.
- **Why now:** Commercial biotechs commonly pick top variants from zero-shot PLMs believing a high global Spearman correlation ($\rho \approx 0.45$) guarantees top-variant enrichment. Woolley et al. (bioRxiv 2026) proved that broad benchmark correlations are inflated by obvious deleterious/unfolded variants, and that rank correlations collapse to near zero among fit variants. An independent auditor that measures viable-subspace discrimination prevents biotech clients from squandering $50k+ per library synthesis round on false-positive candidates.
- **Evidence:** Woolley et al., 2026 ([bioRxiv:10.64898/2026.06.04.730121](https://doi.org/10.64898/2026.06.04.730121)); ProteinGym v1.3 DMS distributions.
- **Rough cost:** Zero cloud spend; fast analytical evaluation on existing ProteinGym scores in minutes on CPU.
- **Next step:** Execute Candidate C24 to quantify the exact drop in Spearman correlation across all published leaderboard models.

### 23. Structural Chain-of-Thought Sanity-Check Middleware for Generative PLMs (VenusRAR API)
- **What:** A lightweight API middleware plugin for protein design platforms and generative PLMs (e.g., ESM-3, ProGen2, EvolutionaryScale) that intercepts proposed substitutions and executes automated biophysical auditing (steric clash detection, buried polar/charge penalty, pLDDT confidence gating) before variants are scheduled for wet-lab synthesis.
- **Why now:** Generative sequence models and unconstrained PLMs frequently hallucinate chemically implausible substitutions in core packing regions that appear statistically plausible to sequence-only heads. Liang et al. (arXiv:2602.00197, VenusRAR) demonstrated that an automated structural audit panel increased top-5 wet-lab hit rates by up to 367% on DMS99 and delivered 4- to 5-fold activity gains in Cas12i3.
- **Evidence:** Liang et al., 2026 ([arXiv:2602.00197](https://arxiv.org/abs/2602.00197)); GitHub `ai4protein/VenusRAR`.
- **Rough cost:** Negligible compute; fast Biopython/structural geometry calculations on standard CPU.
- **Next step:** Prototype the steric clash and SASA filter on ProteinGym benchmark assays with available AlphaFold PDBs (Candidate C25).

### 24. Low-N Zero-Shot Model Selection Engine for Directed Evolution (PRIZM-Engine)
- **What:** A lightweight decision-support SaaS / Python tool for enzyme and antibody engineering benches that takes a standard 24- or 96-well screening plate of mutant measurements, identifies the top-performing zero-shot model from a calibrated pool (GEMME, ESM2, SaProt, Tranception), and uses it to rank large prospective libraries without model fine-tuning.
- **Why now:** Wet-lab teams frequently guess which foundation model to use or try to fine-tune complex neural networks on $N \le 24$ mutants, causing severe overfitting. Harding-Larsen et al. (PRIZM, bioRxiv/Bioinformatics Advances 2026) proved that minimal calibration data ($N \approx 20$) is sufficient to pick the winning zero-shot model, yielding prospective hits (+3°C melting temp, +20% activity) in directed evolution campaigns.
- **Evidence:** Harding-Larsen et al., 2026 ([DOI:10.1093/bioadv/vbag299](https://doi.org/10.1093/bioadv/vbag299)); kbrain label-efficient routing finding.
- **Rough cost:** Zero GPU compute; instant Spearman rank correlation over precomputed candidate models in milliseconds on CPU.
- **Next step:** Execute Candidate C26 across the 217 ProteinGym assays to quantify the bootstrap improvement of N=20 model selection over a static baseline.

### 25. Sparse Causal Circuit Auditor for Biologics Hallucination & Interpretability (SAE-ProteinAudit)
- **What:** An explainability API and validation audit tool using Sparse Autoencoders (SAEs) and causal activation patching on protein language models (ESM-2, SaProt) to provide biopharma teams with structural residue attribution maps explaining why a model scored a substitution favorably before chemical synthesis.
- **Why now:** Biopharma ML teams often treat PLM variant scores as black-box logits, leading to costly wet-lab failures when models score substitutions favorably based on spurious sequence motifs. Mohanty et al. (bioRxiv 2026) showed that true functional variant predictions are mediated by sparse causal circuits that physically map to 3D spatial contacts (residues within 8 Å). An automated audit tool that visualizes and checks causal circuit integrity provides wet-lab scientists with interpretable rationale before placing oligonucleotide orders.
- **Evidence:** Mohanty et al., 2026 ([bioRxiv:10.64898/2026.08.28.747907](https://doi.org/10.64898/2026.08.28.747907)); DNAJA1 J-domain mechanistic circuit benchmark.
- **Rough cost:** Minimal CPU/GPU evaluation using open SAE checkpoints; fast visual graph outputs.
- **Next step:** Prototype Candidate C27 to measure whether 3D contact density gating replicates SAE causal circuit benefits on ProteinGym.





