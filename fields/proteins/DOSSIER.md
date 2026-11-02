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
| 1 | **VenusREM2** | Retrieval-Enhanced Harness | - | GPU + Structure/MSA Harness | - | **0.5560** | Tan et al., 2026 ([arXiv:2609.34654](https://arxiv.org/abs/2609.34654)) |
| 2 | **AIDO Protein-RAG** | Retrieval-Augmented PLM | 16B | Cluster GPU (Multi-A100) | 0.5419 | 0.5182 | Gao et al., 2024 ([bioRxiv:2024.08.19.608688](https://doi.org/10.1101/2024.08.19.608688)) |
| 3 | **VenusREM** | Representation Ensemble | - | Cluster GPU | 0.5357 | 0.5182 | VenusREM team, 2024 |
| 4 | **ProSST (K=2048)** | Structure-Aware PLM | ~110M | GPU (AF2 structure tokens) | 0.5225 | 0.5069 | Wang et al., 2023 ([bioRxiv:2023.11.02.565261](https://doi.org/10.1101/2023.11.02.565261)) |
| 5 | **S3F-MSA** | Structure + Surface + MSA | - | Cluster GPU | 0.5154 | 0.4959 | S3F team, 2024 |
| 6 | **S2F-MSA** | Structure + MSA | - | Cluster GPU | 0.5079 | 0.4883 | S2F team, 2024 |
| 7 | **Protriever** | Homology Retrieval PLM | - | GPU (Retrieval index) | 0.4989 | 0.4789 | Protriever team, 2024 (200 assays) |
| 8 | **ESCOTT** | Structure + Alignment | - | GPU / CPU | 0.4985 | 0.4759 | Faure et al., 2021 ([Genome Biol 22:256](https://doi.org/10.1186/s13059-021-02482-1)) |
| 9 | **PoET** | Autoregressive Retrieval | 200M | GPU (Batched MSA prompt) | 0.4898 | 0.4701 | Truong & Bepler, 2023 ([NeurIPS 2023](https://doi.org/10.1101/2023.07.03.547514)) |
| 10 | **ESM3 open** | Multimodal Foundation | 1.4B | Cluster GPU | 0.4827 | 0.4657 | Hayes et al., 2024 ([bioRxiv:2024.07.02.601708](https://doi.org/10.1101/2024.07.02.601708)) |
| 11 | **RSALOR** | Sequence + Structure | - | GPU | 0.4848 | 0.4646 | RSALOR team, 2024 |
| 12 | **VespaG** | PLM + Conservation | - | GPU / CPU | 0.4818 | 0.4579 | Marquet et al., 2024 |
| 13 | **SaProt (650M)** | Structure-Aware PLM | 650M | High-end GPU (AF2 structure) | 0.4728 | 0.4566 | Su et al., 2024 ([ICLR 2024](https://doi.org/10.1101/2023.10.02.560515)) |
| 14 | **TranceptEVE L** | Retrieval + Generative VAE | Ensemble | High-end GPU | 0.4745 | 0.4558 | Notin et al., 2022 ([ICML 2022](https://proceedings.mlr.press/v162/notin22a.html)) |
| 15 | **GEMME** | Epistatic Evolutionary | Analytical | **CPU-only (seconds–minutes)** | **0.4743** | **0.4547** | Laine et al., 2019 ([Mol Biol Evol 36:2349](https://doi.org/10.1093/molbev/msz179)) |
| 16 | **ProtSSN (ensemble)**| Structure-Sequence GNN | Ensemble | GPU | 0.4728 | 0.4489 | Tan et al., 2023 ([bioRxiv:2023.11.16.567362](https://doi.org/10.1101/2023.11.16.567362)) |
| 17 | **EVE (ensemble)** | Deep Generative VAE | 5x VAE | GPU (Train per family) | 0.4599 | 0.4393 | Frazer et al., 2021 ([Nature 599:91](https://doi.org/10.1038/s41586-021-04043-8)) |
| 18 | **VESPA** | PLM + Mutation Embedding | - | Fast CPU/GPU inference | 0.4630 | 0.4355 | Marquet et al., 2022 ([Bioinformatics 38:3020](https://doi.org/10.1093/bioinformatics/btac278)) |
| 19 | **Tranception L** | Autoregressive Retrieval | 700M | High-end GPU | 0.4502 | 0.4341 | Notin et al., 2022 ([ICML 2022](https://proceedings.mlr.press/v162/notin22a.html)) |
| 20 | **MSA Transformer** | Axial Attention Transformer| 100M | High-end GPU (16 GB VRAM) | 0.4526 | 0.4317 | Rao et al., 2021 ([ICML 2021](https://proceedings.mlr.press/v139/rao21a.html)) |
| 21 | **ESM2 (650M)** | Masked Language Model | 650M | GPU (8–16 GB VRAM) | 0.4382 | 0.4138 | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |
| 22 | **ESM-1v (ensemble)**| Masked Language Model | 5x 650M | GPU (8–16 GB VRAM) | 0.4280 | 0.4065 | Meier et al., 2021 ([NeurIPS 2021](https://doi.org/10.1101/2021.07.09.451791)) |
| 23 | **SaProt (35M)** | Structure-Aware PLM | 35M | Low GPU / CPU | 0.4130 | 0.4065 | Su et al., 2024 ([ICLR 2024](https://doi.org/10.1101/2023.10.02.560515)) |
| 24 | **ESM2 (3B)** | Masked Language Model | 3B | Multi-GPU (24–48 GB VRAM) | 0.4321 | 0.4056 | Lin et al., 2023 ([Science 379:1069](https://doi.org/10.1126/science.ade2574)) |
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

1. **Pruned Cheap Zero-Shot Ensembling (Candidate C1b, Follow-up to C1)**:
   - *Status / Finding*: Naive 5-model unweighted rank ensembling (C1) was tested and **rejected** (Task #172/177: net mean $+0.0066$, 95% CI $[-0.0014, +0.0140]$ vs GEMME). Site-Independent profile PSSMs acted as negative drag.
   - *Open Question*: Does a pruned 4-model ensemble excluding Site-Independent (GEMME + EVmutation + VESPA + ESM2-35M, which showed $+0.0176$, CI $[+0.0094, +0.0257]$ in post-hoc ablation) statistically significantly outperform GEMME across independent protein units under a fresh preregistered test?
   - *Feasibility*: Published scores are fully precomputed on disk (`data/proteingym/zero_shot/`). Evaluating linear or rank blends across 217 assays runs in minutes on CPU.
2. **Label-Efficient Model Selection at $N=24$ (Candidate C2)**:
   - *Status / Finding*: **Validated against frozen GEMME under the preregistered random low-N protocol (Task #194).** Training-only hard selection between GEMME and ESM2-650M using 24 labels improved held-out Spearman by $+0.01645$ per UniProt target (95% CI $[+0.00776,+0.02608]$; $n=186$) over GEMME. The label-shuffle control was negative ($-0.02840$, CI $[-0.04343,-0.01435]$).
   - *Qualification*: The static 50/50 rank blend also passed ($+0.01583$, CI $[+0.00512,+0.02695]$), so this study establishes a useful low-N improvement over GEMME, not that hard selection is superior to a label-free blend. The prespecified softmax weighting was larger ($+0.03183$, CI $[+0.02348,+0.04090]$), but remains secondary to the frozen hard-selection endpoint.
   - *Next question*: With a held-out future DMS paper or a prospectively supplied initial 24-label batch, does the frozen softmax rule retain its advantage over both GEMME and static blending? This external/prospective validation requires operator approval and must keep the entire target assay unseen while freezing all rules.
3. **Augmented Low-N Regression Under Contiguous Splits (Candidate C3)**:
   - *Status*: **Random-split endpoint validated, but not deployable to position-unseen mutation design (Task #191).** Across all proteins the preregistered random-split endpoint passed: mean per-protein $\Delta\rho=+0.00994$, 95% bootstrap CI $[+0.00451,+0.01570]$, $n=186$. This aggregate is driven by 33 multi-mutant-dominated proteins ($+0.05271$, CI $[+0.03402,+0.07464]$); the 153 single-mutant-dominated proteins are null ($+0.00071$, CI $[-0.00393,+0.00474]$).
   - *Question*: Does a model that cannot reuse positional information from training retain an advantage over GEMME on `fold_contiguous_5`, where all test positions are unseen?
   - *Current status*: **Parked (Task #201; no endpoint evaluated).** The frozen `contiguous-low-n-augmentation` preregistration cannot be run in the supplied environment: its authoritative staged `proteingym.py` evaluator cannot import because the only available Python 3.14.8 runtime lacks pandas, scipy, and scikit-learn (numpy 2.5.4 is present). No result, eligibility count, control, or numerical conclusion was produced.
   - *Required next test*: Restore an evaluator-compatible local runtime with pandas, scipy, and scikit-learn, then rerun the unchanged frozen preregistration using `lab/proteingym.py`; emit paired per-assay predictions and protein-clustered `kbstats.evaluate` fields (`net_mean`, `ci_low`, `ci_high`, `n_units`). Do not substitute a custom evaluator or treat the random-split result as evidence for this position-disjoint question.
   - *Feasibility once unblocked*: Fast ridge regression across five folds; expected to run in seconds per assay on the stated CPU budget.
4. **Explaining Small PLM Failure Modes (Candidate C4)**:
   - *Question*: How does the performance gap between small PLMs (ESM2-35M) and top MSA models (GEMME) correlate with MSA evolutionary depth ($N_{\text{eff}}/L$), taxon (virus vs eukaryote), sequence length, and functional assay type?
   - *Feasibility*: Pure analytical regression on metadata from `pg.reference()` and `pg.leaderboard()`. Runs in seconds.
5. **Positional Prior Calibration from Few Labels (Candidate C5)**:
   - *Question*: Can 24 or 48 labels be used solely to fit a 1D position tolerance vector $\hat{\mu}_i$ that re-centers zero-shot scores, and does this improve correlation under random vs contiguous splits?
   - *Feasibility*: Simple 1D shrinkage/empirical Bayes estimator on CPU.
6. **Structure-Token Edge Beyond Stability (Candidate C6)**:
   - *Question*: On the frozen non-Stability ProteinGym subset (Activity, Binding, Expression, and OrganismalFitness), do published SaProt-35M structure-token scores improve per-protein DMS Spearman over published ESM2-35M sequence-only scores when both are paired on identical mutants?
   - *Current status*: **Parked (Task #207; no endpoint evaluated).** The supplied Python 3.14.8 runtime cannot import the mandated staged `proteingym.py` evaluator because pandas, scipy, and scikit-learn are unavailable. The staged ProteinGym v1.3 data are present and validated, but no score vector, correlation, coverage result, confidence interval, or model comparison was produced.
   - *Required next test*: Restore an evaluator-compatible local runtime containing pandas, scipy, and scikit-learn, then run the unchanged frozen `structure-tokens-nonstability-edge` preregistration using `lab/proteingym.py` and its protein-clustered `kbstats.evaluate` endpoint. Do not substitute an evaluator, expand the frozen subset, or infer this comparison from aggregate leaderboard scores.
   - *Feasibility once unblocked*: $0; published scores are staged locally and the paired evaluation should finish within one CPU hour.

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

### 2026-11-01: structure-tokens-nonstability-edge — PARKED (Evaluator Runtime Blocked)
- **Hypothesis / frozen protocol**: The frozen zero-shot comparison asks whether published SaProt-35M structure-token scores rank DMS substitutions better than published ESM2-35M sequence-only scores on the 151 predeclared non-Stability ProteinGym v1.3 assays (120 UniProt IDs), with paired-mutant scoring and a protein-clustered endpoint. The frozen preregistration is `inputs/structure-tokens-nonstability-edge.md` (Task #204).
- **Measured result**: **No numerical result.** The staged ProteinGym v1.3 dataset is present and validated, but the only supplied Python runtime is 3.14.8 and cannot import the trusted staged `proteingym.py` evaluator: `pandas`, `scipy`, and `scikit-learn` are unavailable. Consequently no score files were evaluated and no coverage exclusion, per-assay Spearman, protein-level difference, bootstrap confidence interval, control, or pass/fail endpoint exists.
- **Verdict**: **PARKED / BLOCKED BY RUNTIME.** This is neither support for nor rejection of a non-Stability structure-token advantage; aggregate leaderboard values and the separate Stability question cannot answer the frozen paired comparison.
- **Resumption condition**: Provide a local evaluator-compatible runtime containing pandas, scipy, and scikit-learn; rerun the unchanged frozen protocol through `lab/proteingym.py` and report the prespecified paired coverage, model means, and protein-clustered `kbstats.evaluate` fields. Do not replace the evaluator, alter the model pair or phenotype subset, or tune after restoration.

### 2026-11-01: contiguous-low-n-augmentation — PARKED (Evaluator Runtime Blocked)
- **Hypothesis / frozen protocol**: The preregistered N=96 GEMME-augmented ridge with position-free amino-acid-pair indicators would improve held-out Spearman over frozen GEMME on ProteinGym v1.3 `fold_contiguous_5`, assessed as a protein-clustered paired endpoint. The frozen preregistration is `inputs/contiguous-low-n-augmentation.md`.
- **Measured result**: **No numerical result.** The mandated staged `proteingym.py` evaluator could not import in the only available Python 3.14.8 environment because pandas, scipy, and scikit-learn were unavailable (numpy 2.5.4 was available). Consequently no data were loaded or scored, and no eligibility, prediction, baseline, control, confidence interval, or pass/fail decision exists.
- **Verdict**: **PARKED / BLOCKED BY RUNTIME.** This is an infrastructure limitation, not a negative result or evidence for/against transferable low-N calibration under position-disjoint splits.
- **Resumption condition**: Provide a local evaluator-compatible runtime containing pandas, scipy, and scikit-learn; rerun the unchanged frozen preregistration through `lab/proteingym.py`. Do not replace the evaluator, alter the split, or tune the frozen method after the runtime is restored.

### 2026-11-01: label-efficient-model-selection — VALIDATED (Random Low-N Protocol)
- **Hypothesis**: With 24 labelled mutants, training-only agreement with experimental fitness can select between GEMME and ESM2-650M well enough to improve held-out fitness prediction over frozen GEMME.
- **Preregistration / evaluator**: `inputs/label-efficient-model-selection.md`; all splitting and scoring used `lab/proteingym.py` `pg.low_n` with five fixed random splits (seeds 0–4), $N_{train}=24$, and protein-clustered `pg.improvement_units(..., by="protein")` followed by 2,000-bootstrap `kbstats.evaluate` (seed 7).
- **Measured primary result**: **PASS.** Adaptive hard selection achieved raw mean held-out assay Spearman $0.49203$ versus $0.47412$ for GEMME, and a decision-statistic mean per-protein improvement of **$+0.01645$** (95% CI **$[+0.00776,+0.02608]$**; top-5%-trimmed mean $+0.00697$; $n=186$ protein units). All 217 assays evaluated with zero failures. This passes the frozen gates `ci_low > 0` and positive trimmed mean.
- **Controls**: ESM2-650M alone was worse than GEMME ($-0.04475$, CI $[-0.06871,-0.01921]$). Shuffling the 24 training labels made hard selection harmful ($-0.02840$, CI $[-0.04343,-0.01435]$), supporting that the gain uses label-model association rather than selection noise. The label-free static 50/50 rank blend also passed ($+0.01583$, CI $[+0.00512,+0.02695]$); the prespecified secondary softmax rule achieved $+0.03183$, CI $[+0.02348,+0.04090]$.
- **Inference**: Twenty-four labels contain actionable information about agreement between a frozen evolutionary model and a frozen PLM under random held-out-mutant sampling. The primary endpoint supports improving on GEMME with this protocol; it does **not** establish that hard selection is better than the static blend, since their confidence intervals overlap and no direct frozen comparison was the endpoint.
- **Field impact / limitation**: This is a cheap ($0; about two CPU minutes), reproducible benchmark procedure, not a prospective protein-engineering deployment claim. Its random mutant split can retain other substitutions at a test position in training; a future assay-level/prospective test must freeze the softmax, hard-selection, and static comparators before any target labels are seen. The required external test needs operator approval.

### 2026-11-01: augmented-low-n-regression — VALIDATED RANDOM-SPLIT ENDPOINT; NOT VALIDATED FOR SINGLE-SUBSTITUTION DESIGN
- **Hypothesis**: At 48 labelled mutants and five fixed random low-N replicates, a GEMME-augmented ridge model improves held-out Spearman over frozen GEMME, graded by target protein.
- **Preregistration**: `inputs/augmented-low-n-regression.md`; evaluator: `lab/proteingym.py`, with protein-clustered `kbstats.evaluate`.
- **Measured primary result**: **PASS.** GEMME-augmented ridge achieved mean per-protein held-out Spearman improvement $+0.00994$ over frozen GEMME (95% bootstrap CI $[+0.00451,+0.01570]$; $n=186$ proteins). The preregistered criterion was `ci_low > 0`.
- **Why this passes narrowly**: The saved per-protein results exactly reproduce the reported `kbstats` endpoint, and `pg.low_n` excluded `DMS_score` from each test frame. Splits and seeds were fixed; repeated assays were clustered by UniProt ID.
- **Critical limitation (measured diagnostic)**: The apparent improvement is concentrated in 33 multi-mutant-dominated proteins: $+0.05271$, CI $[+0.03402,+0.07464]$. Among 153 single-mutant-dominated proteins—the relevant regime for amino-acid substitution prediction—it is $+0.00071$, CI $[-0.00393,+0.00474]$. Removing the top 10 proteins changes the all-protein CI lower bound to $-0.00043$. In a representative short multi-mutant protein (PHOT_CHLRE, length 118), 98.9% of test examples overlap a training example at at least one position.
- **Inference**: Random low-N splits permit the one-hot mutation features to learn positional mean fitness and reuse it on test variants at the same positions. Thus the aggregate endpoint is a valid random-split result, but is not evidence that evolutionary-score calibration generalizes to novel positions or ordinary single-substitution design.
- **Controls / reporting defects**: The $\alpha=10^9$ control made all coefficients, including the GEMME coefficient, zero; it is a constant-prediction control rather than a GEMME-equivalence control. The pure-supervised mean ($0.294$) was calculable for only 69/217 assays and is not representative. Neither defect changes the primary paired endpoint.
- **Field impact**: Retain this as a qualified benchmark fact only. Do not use augmented ridge for position-unseen or single-substitution protein engineering until a preregistered contiguous, single-substitution evaluation passes.

### 2026-11-01: cheap-zero-shot-ensemble — REJECTED (Null Result vs GEMME)
- **Hypothesis**: An unweighted 5-model rank-average ensemble of cheap CPU-runnable zero-shot models (GEMME, EVmutation, Site-Independent, VESPA, ESM2-35M) statistically significantly outperforms the best individual member (GEMME) across 217 ProteinGym v1.3 DMS substitution assays evaluated by independent protein target (186 UniProt proteins).
- **Preregistration**: `inputs/cheap-zero-shot-ensemble.md` (Task #172 / #177).
- **Evaluator**: `lab/proteingym.py` + `kbstats.py` (2,000 cluster bootstrap resamples, $B=2,000$, $\alpha=0.05$, seed=7).
- **Result**: **REJECTED (Null Result / Falsified)**
- **Measured**:
  - Independent Protein Units ($N = 186$): Net mean per-protein Spearman improvement $\Delta \bar{\rho} = +0.0066$, 95% cluster bootstrap CI $[-0.0014, +0.0140]$. Net mean excluding top unit: $+0.0007$.
  - Rejection Criterion: $\text{ci\_low} = -0.0014 \le 0.0000$, failing the preregistered threshold for acceptance.
  - Secondary Per-Assay Units ($N = 217$): Net mean $\Delta \bar{\rho} = +0.0095$, 95% CI $[+0.0021, +0.0166]$. (Naive assay-level evaluation gave false positive significance due to repeated assays per protein).
  - Absolute Benchmark Metrics: 5-model ensemble achieved mean Spearman $\bar{\rho} = 0.4838$ and aggregate $\bar{\rho}_{\text{agg}} = 0.4668$ (vs GEMME: $\bar{\rho} = 0.4743$, $\bar{\rho}_{\text{agg}} = 0.4547$).
  - Permutation Control: Shuffled score ranks yielded $\Delta = -0.4798$, 95% CI $[-0.5024, -0.4574]$ ($\bar{\rho} \approx 0.0$).
  - Leave-One-Out Ablations ($N = 186$ proteins):
    - Dropping `Site-Independent`: $\Delta = +0.0176$, 95% CI $[+0.0094, +0.0257]$ (**strictly positive**).
    - Dropping `EVmutation`: $\Delta = +0.0064$, 95% CI $[-0.0020, +0.0144]$ (spans zero).
    - Dropping `ESM2 (35M)`: $\Delta = +0.0053$, 95% CI $[-0.0017, +0.0117]$ (spans zero).
    - Dropping `GEMME`: $\Delta = -0.0132$, 95% CI $[-0.0236, -0.0034]$ (strictly negative).
    - Dropping `VESPA`: $\Delta = -0.0146$, 95% CI $[-0.0237, -0.0061]$ (strictly negative).
- **Inference**:
  - Equal-weight rank averaging across diverse cheap models fails to reliably improve upon the best individual member (GEMME). Low-fidelity first-order conservation models (`Site-Independent` PSSM log-odds, standalone $\bar{\rho}=0.3688$) inject uncorrelated noise that dilutes high-order epistatic signal.
  - Clustering by independent biological target (`UniProt_ID`) is essential to avoid false edges: naive assay-level analysis produces a false-positive edge ($+0.0095$, CI $[+0.0021, +0.0166]$), whereas protein-level clustering correctly reveals the CI crossing zero ($[-0.0014, +0.0140]$).
- **Field Impact**:
  - Unweighted ensembles should not blindly include simple profile PSSMs when combining epistatic MSA models and PLMs.
  - Motivates a targeted pruned ensemble hypothesis (GEMME + EVmutation + VESPA + ESM2-35M), which showed $+0.0176$ per-protein gain in post-hoc ablation and warrants formal preregistration.

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
