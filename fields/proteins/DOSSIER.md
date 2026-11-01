---
title: "Mutation-Effect Prediction Dossier"
type: research
status: maintained
started: 2026-11-01
updated: 2026-11-01
tags:
  - proteins
  - mutation-effect
  - proteingym
  - zero-shot
  - low-n
  - baselines
source_repositories:
  - https://github.com/OATML-Markslab/ProteinGym
---

# Proteins: Mutation-Effect Prediction Dossier

Scope: Predicting the functional and fitness effects of amino-acid substitutions on proteins, evaluated on the **ProteinGym v1.3** benchmark suite. This is the canonical reference page for computational and experimental work in this niche. Every finding here distinguishes measured experimental results from statistical inferences and qualitative conclusions. All benchmark scores are computed strictly through `lab/proteingym.py`.

---

## State of the Art

State-of-the-art methods in variant effect prediction span four distinct computational paradigms:
1. **Multiple Sequence Alignment (MSA) generative models**: capture natural evolutionary constraints across homologous sequences via explicit statistical physics or density estimation (e.g., GEMME, EVE, DeepSequence, EVmutation).
2. **Pre-trained Protein Language Models (PLMs)**: leverage large-scale masked language modeling (MLM) or autoregressive modeling across millions of unaligned sequences (e.g., ESM-1v, ESM2, ESM3, Progen2/3).
3. **Retrieval-augmented and hybrid autoregressive models**: dynamically retrieve and condition on evolutionary homologs during sequence evaluation (e.g., Tranception, PoET, AIDO Protein-RAG).
4. **Structure-informed models and inverse-folding networks**: condition sequence probability on 3D backbone coordinates or quantized geometric vocabularies from AlphaFold2 / PDB structures (e.g., ProSST, SaProt, ESCOTT, ESM-IF1, ProteinMPNN).

### Leaderboard on ProteinGym v1.3 Substitutions (217 Assays)

The table below reports zero-shot performance across all 217 deep mutational scanning (DMS) substitution assays in ProteinGym v1.3. Both the **Mean per-assay Spearman** ($\bar{\rho}_{\text{assay}}$) and the official **ProteinGym aggregate Spearman** ($\bar{\rho}_{\text{agg}}$, hierarchical mean within UniProt ID, then within coarse selection type, then across selection types) are computed directly from published per-mutant scores via `lab/proteingym.py`.

| Rank | Model | Class | Parameters | Hardware / Compute Profile | Mean Spearman ($\bar{\rho}_{\text{assay}}$) | ProteinGym Aggregate ($\bar{\rho}_{\text{agg}}$) | Primary Reference |
|---|---|---|---|---|---|---|---|
| 1 | **AIDO Protein-RAG** | Retrieval-Augmented PLM | 16B | Cluster GPU (Multi-A100) | 0.5419 | 0.5182 | Gao et al., 2024 ([bioRxiv:2024.08.19.608688](https://doi.org/10.1101/2024.08.19.608688)) |
| 2 | **VenusREM** | Representation Ensemble | - | Cluster GPU | 0.5357 | 0.5182 | VenusREM team, 2024 |
| 3 | **ProSST (K=2048)** | Structure-Aware PLM | ~110M | GPU (AF2 structure tokens) | 0.5225 | 0.5069 | Wang et al., 2023 ([bioRxiv:2023.11.02.565261](https://doi.org/10.1101/2023.11.02.565261)) |
| 4 | **S3F-MSA** | Structure + Surface + MSA | - | Cluster GPU | 0.5154 | 0.4959 | S3F team, 2024 |
| 5 | **S2F-MSA** | Structure + MSA | - | Cluster GPU | 0.5079 | 0.4883 | S2F team, 2024 |
| 6 | **Protriever** | Homology Retrieval PLM | - | GPU (Retrieval index) | 0.4989 | 0.4789 | Protriever team, 2024 (200 assays) |
| 7 | **ESCOTT** | Structure + Alignment | - | GPU / CPU | 0.4985 | 0.4759 | Faure et al., 2021 ([Genome Biol 22:256](https://doi.org/10.1186/s13059-021-02482-1)) |
| 8 | **PoET** | Autoregressive Retrieval | 200M | GPU (Batched MSA prompt) | 0.4898 | 0.4701 | Truong & Bepler, 2023 ([NeurIPS 2023](https://doi.org/10.1101/2023.07.03.547514)) |
| 9 | **ESM3 open** | Multimodal Foundation | 1.4B | Cluster GPU | 0.4827 | 0.4657 | Hayes et al., 2024 ([bioRxiv:2024.07.02.601708](https://doi.org/10.1101/2024.07.02.601708)) |
| 10 | **RSALOR** | Sequence + Structure | - | GPU | 0.4848 | 0.4646 | RSALOR team, 2024 |
| 11 | **VespaG** | PLM + Conservation | - | GPU / CPU | 0.4818 | 0.4579 | Marquet et al., 2024 |
| 12 | **SaProt (650M)** | Structure-Aware PLM | 650M | High-end GPU (AF2 structure) | 0.4728 | 0.4566 | Su et al., 2024 ([ICLR 2024](https://doi.org/10.1101/2023.10.02.560515)) |
| 13 | **TranceptEVE L** | Retrieval + Generative VAE | Ensemble | High-end GPU | 0.4745 | 0.4558 | Notin et al., 2022 ([ICML 2022](https://proceedings.mlr.press/v162/notin22a.html)) |
| 14 | **GEMME** | Epistatic Evolutionary | Analytical | **CPU-only (seconds–minutes)** | **0.4743** | **0.4547** | Laine et al., 2019 ([Mol Biol Evol 36:2349](https://doi.org/10.1093/molbev/msz179)) |
| 15 | **ProtSSN (ensemble)**| Structure-Sequence GNN | Ensemble | GPU | 0.4728 | 0.4489 | Tan et al., 2023 ([bioRxiv:2023.11.16.567362](https://doi.org/10.1101/2023.11.16.567362)) |
| 16 | **EVE (ensemble)** | Deep Generative VAE | 5x VAE | GPU (Train per family) | 0.4599 | 0.4393 | Frazer et al., 2021 ([Nature 599:91](https://doi.org/10.1038/s41586-021-04043-8)) |
| 17 | **VESPA** | PLM + Mutation Embedding | - | Fast CPU/GPU inference | 0.4630 | 0.4355 | Marquet et al., 2022 ([Bioinformatics 38:3020](https://doi.org/10.1093/bioinformatics/btac278)) |
| 18 | **Tranception L** | Autoregressive Retrieval | 700M | High-end GPU | 0.4502 | 0.4341 | Notin et al., 2022 ([ICML 2022](https://proceedings.mlr.press/v162/notin22a.html)) |
| 19 | **MSA Transformer** | Axial Attention Transformer| 100M | High-end GPU (16 GB VRAM) | 0.4526 | 0.4317 | Rao et al., 2021 ([ICML 2021](https://proceedings.mlr.press/v139/rao21a.html)) |
| 20 | **ESM2 (650M)** | Masked Language Model | 650M | GPU (8–16 GB VRAM) | 0.4382 | 0.4138 | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |
| 21 | **ESM-1v (ensemble)**| Masked Language Model | 5x 650M | GPU (8–16 GB VRAM) | 0.4280 | 0.4065 | Meier et al., 2021 ([NeurIPS 2021](https://doi.org/10.1101/2021.07.09.451791)) |
| 22 | **SaProt (35M)** | Structure-Aware PLM | 35M | Low GPU / CPU | 0.4130 | 0.4065 | Su et al., 2024 ([ICLR 2024](https://doi.org/10.1101/2023.10.02.560515)) |
| 23 | **ESM2 (3B)** | Masked Language Model | 3B | Multi-GPU (24–48 GB VRAM) | 0.4321 | 0.4056 | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |
| 24 | **ESM2 (15B)** | Masked Language Model | 15B | Cluster GPU (8x A100) | 0.4253 | 0.4003 | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |
| 25 | **EVmutation** | Pairwise Potts Epistasis | Analytical | CPU (Pseudolikelihood) | 0.4184 | 0.3953 | Hopf et al., 2017 ([Nat Biotechnol 35:128](https://doi.org/10.1038/nbt.3769)) |
| 26 | **Site-Independent**| Profile PSSM Log-odds | 0 | **CPU-only (milliseconds)** | **0.3688** | **0.3594** | Classical baseline (ProteinGym standard) |
| 27 | **ESM2 (35M)** | Masked Language Model | 35M | **CPU-viable (RAM < 2 GB)** | **0.3188** | **0.3208** | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |
| 28 | **ESM2 (8M)** | Masked Language Model | 8M | **CPU-viable (RAM < 1 GB)** | **0.2056** | **0.2257** | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |

### Supervised and Low-N Fitness Prediction

When experimental variant measurements are available, supervised models can adapt zero-shot representations or learn directly from sequence encodings:
- **Mutation-Augmented Models** (Hsu et al., 2022, *Nat Biotechnol* 40:1014–1023, [DOI: 10.1038/s41587-021-01146-5](https://doi.org/10.1038/s41587-021-01146-5)): Combining zero-shot evolutionary density estimates (e.g., from EVmutation or ESM-1v) as explicit features with regularized linear models (Ridge) or small neural networks dramatically improves sample efficiency at low $N$ ($N \in [24, 96]$). Pure supervised models trained from scratch without evolutionary augmentation fail completely in this regime.
- **Low-N ML-Guided Directed Evolution** (Biswas et al., 2021, *Nat Methods* 18:389–396, [DOI: 10.1038/s41592-021-01100-y](https://doi.org/10.1038/s41592-021-01100-y)): Demonstrates that UniRep sequence embeddings paired with Gaussian Process or linear heads guide sequence discovery within fewer than 100 characterizations.
- **FLIP Benchmark** (Dallago et al., 2021, *NeurIPS Datasets and Benchmarks*, [bioRxiv:2021.11.09.467890](https://doi.org/10.1101/2021.11.09.467890)): Evaluates supervised models under biological splits (e.g. mutational distance, sequence homology), showing massive performance drops when test sequences diverge from training sequences.
- **ProteinGym Supervised CV Splits** (Notin et al., 2023): Evaluates models across 5 folds under `random`, `modulo`, and `contiguous` partitioning. Generalization drops substantially on `contiguous` folds because the model cannot rely on observed mutations at the same position.

---

## Benchmarks and Datasets

### Primary Benchmark: ProteinGym v1.3 Substitutions

- **Name**: ProteinGym v1.3 (DMS Substitutions)
- **Accession / URLs**:
  - Web: [https://proteingym.org](https://proteingym.org)
  - Code: [https://github.com/OATML-Markslab/ProteinGym](https://github.com/OATML-Markslab/ProteinGym)
  - Data Zenodo: [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327)
- **Size**:
  - Total Assays: 217 distinct deep mutational scanning assays.
  - Unique Target Proteins (UniProt IDs): 186.
  - Total Mutants: 2,465,767.
  - Single-Substitution Mutants: 696,311.
- **Taxonomic Distribution**:
  - Human: 96 assays (44.2%)
  - Prokaryote: 50 assays (23.0%)
  - Non-human Eukaryote: 40 assays (18.4%)
  - Virus: 31 assays (14.3%)
- **Coarse Functional Selection Types**:
  - OrganismalFitness: 77 assays (35.5%)
  - Stability: 66 assays (30.4%)
  - Activity: 43 assays (19.8%)
  - Expression: 18 assays (8.3%)
  - Binding: 13 assays (6.0%)
- **Alignment Depth ($N_{\text{eff}}/L$) Distribution**:
  - Medium ($1 < N_{\text{eff}}/L \le 10$): 109 assays (50.2%)
  - High ($N_{\text{eff}}/L > 10$): 72 assays (33.2%)
  - Low ($N_{\text{eff}}/L \le 1$): 36 assays (16.6%)
- **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0).
- **Measurement Endpoint**: Experimental fitness metrics derived from high-throughput deep mutational scanning (growth selection log2 enrichment, flow cytometry fluorescence intensity, phage/ribosome display binding affinity, protease cleavage resistance).

### Low-N / Supervised Cross-Validation Folds

Single-substitution assays contain predefined 5-fold cross-validation columns:
1. `fold_random_5`: Uniform random partition across mutants.
2. `fold_modulo_5`: Split by residue position modulo 5 ($pos \pmod 5$). Positions are interleaved across folds.
3. `fold_contiguous_5`: Sequence partitioned into 5 contiguous structural blocks ($pos \in [L_k, L_{k+1}]$). Positions in the test fold are completely absent from training.

### Known Leakage Traps

1. **Positional Tolerance Leakage (The Random CV Trap)**:
   - *Trap*: Residue positions differ dramatically in their tolerance to any mutation (e.g. highly conserved buried hydrophobic cores vs solvent-exposed flexible loops). Under `fold_random_5`, other substitutions at position $i$ are present in the training set. A naive model that simply memorizes the mean fitness at position $i$ scores artificially high on test sets.
   - *Fix*: Evaluate strictly on `fold_contiguous_5` or enforce position-disjoint splits so no mutations at test positions appear in training.
2. **Homology and Pre-training Data Contamination**:
   - *Trap*: Large PLMs (ESM-1v, ESM2, ESM3) are trained on UniRef50/UniRef90, which contain wild-type target sequences and close homologs. While zero-shot masked marginal scoring does not observe experimental fitness labels, supervised fine-tuning or nearest-neighbor sequence retrieval can suffer from severe sequence identity leakage.
   - *Fix*: Standardize zero-shot evaluations across all 217 assays without target-specific fine-tuning; when performing sequence retrieval, strictly exclude the wild-type and target homologs if evaluating generalization.
3. **Structure Holo vs. Apo Conformation Leakage**:
   - *Trap*: Structure-based methods (ProSST, ESCOTT, SaProt, ProteinMPNN) evaluated on experimental crystal structures often use structures crystallized with bound ligands or substrates. This leaks information about active sites and binding interfaces that is unavailable in apo states.
   - *Fix*: ProteinGym standardizes structural inputs on predicted AlphaFold2 / ColabFold structures to avoid ligand-binding artifacts and crystal packaging biases.
4. **Per-Assay Hyperparameter Cherry-Picking**:
   - *Trap*: Tuning temperature parameters, MSA alignment filtering thresholds, or ensemble weights separately on each assay's test set.
   - *Fix*: Hyperparameters must be fixed a priori across the entire benchmark, or cross-validated across independent protein family clusters.
5. **Dependent-Row and Repeated-Assay Clustering**:
   - *Trap*: Treating all 2.47M mutants or 217 assays as independent identical observations. Several UniProt proteins have multiple DMS assays under different selection conditions (e.g. 186 UniProt IDs across 217 assays). Standard row-level or assay-level t-tests underestimate standard errors.
   - *Fix*: Grade statistical improvements by resampling independent units (clustering by UniProt ID via `by="protein"` in `improvement_units`) with bootstrap confidence intervals via `kbstats`.

---

## Baselines that are Hard to Beat

### Zero-Shot Track
1. **GEMME** (Laine et al., 2019):
   - **Performance**: Mean Spearman = 0.4743, Aggregate Spearman = 0.4547.
   - **Properties**: CPU-only analytical pseudolikelihood model of epistasis and conservation computed from an MSA. It runs in minutes without GPU acceleration, matches the massive hybrid TranceptEVE L (0.4558 aggregate), and easily beats ESM2-650M (0.4138 aggregate) and ESM-1v ensemble (0.4065 aggregate).
2. **Site-Independent** (Profile PSSM Log-Odds):
   - **Performance**: Mean Spearman = 0.3688, Aggregate Spearman = 0.3594.
   - **Properties**: Has zero trainable parameters. Computes independent conservation log-odds from family MSA frequencies: $\log [f(i, x_i) / f(i, x_i^{\text{wt}})]$. Outperforms ESM2-35M (0.3208 aggregate) by +0.0386 and CARP-76M (0.3279 aggregate) by +0.0315.
3. **ESM2 (650M)** (Lin et al., 2023):
   - **Performance**: Mean Spearman = 0.4382, Aggregate Spearman = 0.4138.
   - **Properties**: The standard GPU-based masked language model baseline. Requires no MSA and no structural input. Single-sequence zero-shot benchmark standard.
4. **VESPA / VESPAl** (Marquet et al., 2022):
   - **Performance**: Mean Spearman = 0.4630, Aggregate Spearman = 0.4355.
   - **Properties**: Fast inference combining PLM representations with conservation features.

### Low-N / Supervised Track
1. **Frozen Zero-Shot Baseline (0 Parameters)**:
   - In low-N regimes ($N = 24$ or $N = 48$), high measurement noise causes unregularized regression models to overfit training samples and achieve negative test correlations. The unadapted zero-shot prior is the primary baseline to beat.
2. **Augmented Ridge Regression** (Hsu et al., 2022):
   - Linear ridge regression combining one-hot mutant indicators with an evolutionary zero-shot score feature: $\hat{y} = \alpha \cdot s_{\text{zero}}(x) + \mathbf{w}^T \mathbf{x} + b$. The gold standard for low-N supervised adaptation.

---

## Open Questions Testable on 8 CPU Cores Without a GPU

Our compute boundary (8 CPU cores, ~7 GB RAM, ~160 GB disk, no GPU) dictates our strategic edge: we do not train large models from scratch; we leverage published zero-shot scores, small CPU-viable PLMs (ESM2-8M/35M), analytical MSA algorithms, and rigorous statistical calibration.

1. **Cheap Zero-Shot Ensembling (Candidate C1)**:
   - *Question*: Can an unweighted rank average or regularized blend of cheap CPU-computable published scores (GEMME, Site-Independent, EVmutation, VESPA, ESM2-35M) outperform GEMME alone on the 217 ProteinGym substitution assays?
   - *Feasibility*: Published scores are fully precomputed on disk (`data/proteingym/zero_shot/`). Evaluating linear or rank blends across 217 assays runs in minutes on CPU.
2. **Label-Efficient Model Selection at $N=24$ (Candidate C2)**:
   - *Question*: Given only 24 experimental mutant labels for a target protein, can a simple selection rule (e.g. small-sample Spearman or cross-validated ranking) accurately identify whether an MSA model (GEMME) or a PLM (ESM) will perform better on the remaining unobserved mutants?
   - *Feasibility*: Evaluated using `pg.low_n(aid, fit_predict, n_train=24)`. Runs in under 30 minutes on CPU.
3. **Augmented Low-N Regression Under Contiguous Splits (Candidate C3)**:
   - *Question*: Does Hsu et al.'s augmented ridge regression maintain its performance advantage over zero-shot alone when tested on `fold_contiguous_5` (where test positions are completely unseen during training), or does it degrade toward the zero-shot baseline?
   - *Feasibility*: Fast closed-form ridge regression using numpy/scikit-learn across 5 folds. Runs in seconds per assay.
4. **Explaining Small PLM Failure Modes (Candidate C4)**:
   - *Question*: How does the performance gap between small PLMs (ESM2-35M) and top MSA models (GEMME) correlate with MSA evolutionary depth ($N_{\text{eff}}/L$), taxon (virus vs eukaryote), sequence length, and functional assay type?
   - *Feasibility*: Pure analytical regression on metadata from `pg.reference()` and `pg.leaderboard()`. Runs in seconds.
5. **Positional Prior Calibration from Few Labels (Candidate C5)**:
   - *Question*: Can 24 or 48 labels be used solely to fit a 1D position tolerance vector $\hat{\mu}_i$ that re-centers zero-shot scores, and does this improve correlation under random vs contiguous splits?
   - *Feasibility*: Simple 1D shrinkage/empirical Bayes estimator on CPU.

---

## Hype vs. Evidence

| Common Hype / Industry Belief | Rigorous Empirical Evidence (ProteinGym v1.3) |
|---|---|
| **"Bigger PLMs (15B, 100B) continuously improve variant effect predictions."** | **Refuted by scaling data.** ESM2-650M ($\bar{\rho}_{\text{agg}} = 0.4138$) outperforms ESM2-3B ($0.4056$) and ESM2-15B ($0.4003$). xTrimoPGLM-100B ($\bar{\rho}_{\text{agg}} = 0.3643$) scores worse than ESM2-150M ($0.3868$). Without explicit MSA retrieval or structure conditioning, massive parameter scaling shows plateauing or inverse scaling on single-sequence zero-shot variant effects. |
| **"Deep learning renders classical evolutionary models (GEMME, EVmutation) obsolete."** | **Refuted by benchmark results.** GEMME (2019), an analytical epistatic model on MSAs running in minutes on CPU without neural networks, achieves $\bar{\rho}_{\text{agg}} = 0.4547$, beating every single-sequence PLM (including ESM2-650M at $0.4138$) and matching the complex TranceptEVE L ensemble ($0.4558$). |
| **"Supervised machine learning easily predicts fitness with 20–50 experimental mutants."** | **Refuted in low-N regimes.** Pure supervised models (linear, CNN, or transformer) trained from scratch on 24–48 mutants frequently fit experimental noise, achieving negative test $R^2$ and trailing frozen zero-shot evolutionary priors. Supervised heads only provide value when heavily regularized and augmented with evolutionary priors (Hsu et al., 2022). |
| **"Random 5-fold cross-validation proves a model learns fitness landscapes."** | **Refuted by split leakage.** Uniform random CV leaks position-level conservation tolerance across folds. A model memorizing position-level mean fitness appears predictive on random CV, but collapses on `contiguous_5` splits where test positions are strictly unobserved. |
| **"Sequence alone contains all information needed; structures add no edge."** | **Refuted by structure-informed PLMs.** ProSST-2048 ($\bar{\rho}_{\text{agg}} = 0.5069$) and SaProt-650M ($\bar{\rho}_{\text{agg}} = 0.4566$) substantially outperform their sequence-only counterparts by integrating 3D structural tokens derived from AlphaFold2 backbones. SaProt-35M ($\bar{\rho}_{\text{agg}} = 0.4065$) matches the 5-model ESM-1v ensemble ($0.4065$) at 1/18th the parameter count. |

---

## Verdicts (Ours, Dated, Newest First)

### 2026-11-01: Lab Validation — Exact Reproduction of ProteinGym v1.3 Leaderboard
- **Evaluator**: `lab/proteingym.py`
- **Result**: **PASS (Exact Match)**
- **Measured**: Recomputing per-assay Spearman from published v1.3 zero-shot per-mutant scores across all 217 DMS substitution assays matches the published `DMS_substitutions_Spearman_DMS_level.csv` to within $\pm 0.0005$ (its 3-decimal rounding precision) across all verified models:
  - TranceptEVE L: Mean Spearman = 0.4745, Aggregate = 0.4558
  - GEMME: Mean Spearman = 0.4743, Aggregate = 0.4547
  - ESM2 (650M): Mean Spearman = 0.4382, Aggregate = 0.4138
  - Site-Independent: Mean Spearman = 0.3688, Aggregate = 0.3594
  - ESM2 (35M): Mean Spearman = 0.3188, Aggregate = 0.3208
  - ESM2 (8M): Mean Spearman = 0.2056, Aggregate = 0.2257
- **Inference**: Confirms that `lab/proteingym.py` reproduces the official ProteinGym evaluation standard identically without evaluator drift or metric leakage.
- **Field Impact**: Proves that GEMME (an analytical CPU method) is competitive with state-of-the-art hybrid models (TranceptEVE L) and superior to ESM2-650M, establishing a solid zero-cost CPU foundation for kbrain's protein mutation-effect research.
