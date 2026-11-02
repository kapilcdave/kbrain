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




