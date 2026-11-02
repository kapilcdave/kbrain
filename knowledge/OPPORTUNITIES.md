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





