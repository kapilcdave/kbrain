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


