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
- **Evidence:** Hsu et al., 2022 (Nat Biotechnol); ProteinGym CV benchmarks; kbrain finding on cheap-zero-shot ensembles.
- **Rough cost:** Zero cloud spend; purely analytical evaluation using `pg.low_n` and `lab/proteingym.py`.
- **Next step:** Preregister Candidate C2 / C3 to benchmark low-N ridge regression and model selection across all 217 assays.



