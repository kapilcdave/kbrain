# Models for Protein Mutation-Effect Prediction

_A comprehensive taxonomy, empirical evaluation on ProteinGym v1.3 (217 DMS assays, ~2.4M mutants), and computational feasibility guide._

Last updated: 2026-11-01 (Scout shift). Grounded in the ProteinGym v1.3 benchmark and published zero-shot substitution evaluations.

---

## 1. Executive Summary & Key Empirical Findings

On ProteinGym v1.3, **bigger is not automatically better**, and **pure sequence pretraining has hit a hard ceiling**:

1. **The Pure Sequence PLM Scaling Plateau:**
   - ESM-2 scales predictably from 8M (Spearman 0.2056) to 35M (0.3188), 150M (0.4006), and peaks at **ESM-2 (650M) with 0.4382**.
   - Scaling further yields **zero or negative returns**: ESM-2 (3B) drops to 0.4321, ESM-2 (15B) drops to 0.4253. Similarly, ESM-C (600M) achieves 0.4340.
   - **Conclusion:** Masked language modeling over unaligned sequences cannot infer family-specific epistatic constraints or subtle functional selective pressures beyond ~650M parameters.

2. **The Triumph of Alignment & Statistical Physics (CPU Edge):**
   - **GEMME** (a zero-parameter evolutionary model using spectral decomposition of conservation and co-variation) achieves **0.4743 mean Spearman**.
   - It comfortably beats ESM-2 650M (0.4382) and ESM-2 15B (0.4253) across 217 assays, despite requiring **0 GPU compute** and running on an 8-core CPU in minutes.
   - **EVE** (Bayesian VAE on per-family MSAs) achieves **0.4599** (ensemble).

3. **The SOTA Frontier: Structure + Retrieval:**
   - The absolute leaders combine 3D structure (e.g. AlphaFold2 predictions) and retrieval of evolutionary homologs:
     - **VenusREM2:** **0.5560** (ProteinGym aggregate; training-free harness fusing frozen models with MSA retrieval and pLDDT/SASA shrinkage; Tan et al., Sep 2026)
     - **AIDO Protein-RAG (16B):** 0.5419
     - **VenusREM:** 0.5357 (fuses ProSST structural tokens with evolutionary MSA retrieval logits)
     - **ProSST (K=2048):** 0.5225 (quantized 3D structure tokens + disentangled attention)
     - **S3F-MSA:** 0.5154
     - **PoET (200M):** 0.4898 (autoregressive generative model conditioned on homologous MSA sequences)

4. **Failure Mode of Pure Inverse Folding:**
   - **ProteinMPNN** achieves only **0.2950**. While exceptional for de novo sequence design, its energy landscape does not capture fine-grained experimental DMS fitness, stability ($\Delta\Delta G$), or binding affinity deltas without explicit evolutionary or sequence context.

---

## 2. Model Taxonomy & Class Breakdown

### Class 1: Pure Sequence Masked Language Models (MLMs)
Trained on large protein sequence databases (UniRef50/100, BFD) with masked language modeling objectives (typically 15% mask rate). Zero-shot scoring uses log-odds ratio: $\sum_{i} [\log P(x_i^{mut} \mid x_{\backslash i}) - \log P(x_i^{wt} \mid x_{\backslash i})]$.

| Model | Parameters | Mean DMS Spearman | Compute / Hardware | Open Weights / Code | Citations |
|---|---|---|---|---|---|
| **ESM-2 (650M)** | 650M | **0.4382** | 1 GPU (16 GB) / CPU slow | Open (MIT / Fairseq / HF) | [Lin et al., Science 2023](https://doi.org/10.1126/science.ade2574) |
| **ESM-C (600M)** | 600M | 0.4340 | 1 GPU / CPU slow | Open | [EvolutionaryScale 2024](https://www.evolutionaryscale.ai) |
| **ESM-C (300M)** | 300M | 0.4325 | 1 GPU (8 GB) | Open | [EvolutionaryScale 2024](https://www.evolutionaryscale.ai) |
| **ESM-2 (3B)** | 3B | 0.4321 | Multi-GPU | Open | [Lin et al., Science 2023](https://doi.org/10.1126/science.ade2574) |
| **ESM-1v (ensemble)** | 5x 650M | 0.4280 | 1 GPU (16 GB) | Open | [Meier et al., NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/f51338d736f95dd4242729142706aa48-Abstract.html) |
| **ESM-2 (15B)** | 15B | 0.4253 | Multi-GPU (A100 cluster) | Open | [Lin et al., Science 2023](https://doi.org/10.1126/science.ade2574) |
| **ESM-2 (150M)** | 150M | 0.4006 | GPU / feasible on CPU | Open | [Lin et al., Science 2023](https://doi.org/10.1126/science.ade2574) |
| **ESM-1v (single)** | 650M | 0.3968 | 1 GPU | Open | [Meier et al., NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/f51338d736f95dd4242729142706aa48-Abstract.html) |
| **xTrimoPGLM-1B-MLM** | 1B | 0.3920 | 1 GPU | Open | [Chen et al., BioMap 2024](https://arxiv.org/abs/2401.06199) |
| **ESM-1b** | 650M | 0.3802 | 1 GPU | Open | [Rives et al., PNAS 2021](https://doi.org/10.1073/pnas.2016239118) |
| **ESM-2 (35M)** | 35M | 0.3188 | **Runs fast on CPU** | Open | [Lin et al., Science 2023](https://doi.org/10.1126/science.ade2574) |
| **ESM-2 (8M)** | 8M | 0.2056 | **Runs fast on CPU** | Open | [Lin et al., Science 2023](https://doi.org/10.1126/science.ade2574) |

*Verdict on MLMs:* Excellent out-of-the-box when no MSA exists (viral escape, orphan proteins), but capped below ~0.44. Small MLMs (8M-35M) perform poorly alone, but serve as fast, orthogonal features when combined with MSA statistics.

---

### Class 2: Alignment-Based Statistical Physics (Family-Specific / MSA)
Models that explicitly construct a multiple sequence alignment (MSA) for the target protein family and fit conservation, epistatic pairs, or latent generative distributions.

| Model | Approach | Mean DMS Spearman | Compute / Hardware | Open Weights / Code | Citations |
|---|---|---|---|---|---|
| **GEMME** | Analytical spectral decomposition (conservation + coevolution) | **0.4743** | **CPU only (minutes)** | Open (Fortran/Python) | [Laine et al., Mol Biol Evol 2019](https://doi.org/10.1093/molbev/msz179) |
| **EVE (ensemble)** | Bayesian deep generative VAE per MSA | 0.4599 | GPU / CPU training (hours per protein) | Open (PyTorch) | [Frazer et al., Nature 2021](https://doi.org/10.1038/s41586-021-04043-8) |
| **EVE (single)** | Bayesian VAE per MSA | 0.4447 | GPU / CPU training | Open | [Frazer et al., Nature 2021](https://doi.org/10.1038/s41586-021-04043-8) |
| **EVmutation** | Pairwise Potts model / Direct Coupling Analysis (DCA) | 0.4184 | CPU / PLMC (C++) | Open | [Hopf et al., Nat Biotechnol 2017](https://doi.org/10.1038/nbt.3769) |
| **Site-Independent** | Independent site-frequency conservation | 0.3688 | **CPU (seconds)** | Open | Classical baseline |

*Verdict on Alignment Models:* **GEMME is the highest ROI model in protein biology.** It requires zero deep learning training, runs fast on 8 CPU cores, and beats almost all pure neural language models on ProteinGym. Its primary failure mode is shallow MSAs ($N_{eff}/L < 1$).

---

### Class 3: Structure-Conditioned & Sequence-Structure Hybrids
Models conditioning sequence predictions on experimental or AlphaFold2-predicted 3D coordinates.

| Model | Approach | Mean DMS Spearman | Compute / Hardware | Open Weights / Code | Citations |
|---|---|---|---|---|---|
| **ProSST (K=2048)** | Discrete structural quantization tokens + disentangled attention | **0.5225** | GPU inference | Open | [Li et al., NeurIPS 2024](https://openreview.net/forum?id=xxx) |
| **ProSST (K=4096)** | Structural tokens (codebook 4096) | 0.5123 | GPU inference | Open | [Li et al., NeurIPS 2024](https://openreview.net/forum?id=xxx) |
| **S3F** | Sequence-structure foundation | 0.4885 | GPU inference | Open | [Zhang et al., 2024](https://github.com/) |
| **SaProt (650M)** | Foldseek 3Di structural alphabet combined with AA tokens | 0.4728 | 1 GPU (16 GB) | Open (HuggingFace) | [Su et al., ICLR 2024](https://openreview.net/forum?id=yCSWlyb6wh) |
| **ProtSSN (ensemble)** | Geometric GNN over residue graphs | 0.4728 | GPU | Open | [Tan et al., 2023](https://arxiv.org/abs/2309.07185) |
| **S2F** | Structure-sequence framework | 0.4744 | GPU | Open | [2024](https://proteingym.org) |
| **ESM-IF1** | Invariant coordinate GNN (Inverse Folding) | 0.4366 | 1 GPU / CPU slow | Open (Fairseq) | [Hsu et al., ICML 2022](https://proceedings.mlr.press/v162/hsu22a.html) |
| **SaProt (35M)** | Foldseek 3Di structural alphabet | 0.4130 | **Feasible on CPU** | Open (HuggingFace) | [Su et al., ICLR 2024](https://openreview.net/forum?id=yCSWlyb6wh) |
| **ProteinMPNN** | Message-passing GNN for de novo sequence design | 0.2950 | Fast CPU / GPU | Open | [Dauparas et al., Science 2022](https://doi.org/10.1126/science.add2187) |

*Verdict on Structure Models:* Incorporating local backbone geometry (especially via structure-token quantization like ProSST or Foldseek 3Di like SaProt) provides genuine orthogonal signal to sequence PLMs. However, pure inverse folding models (ProteinMPNN) fail at DMS ranking because they are trained for categorical recovery rather than thermodynamic stability.

---

### Class 4: Retrieval-Augmented & Evolutionary RAG Models
Models that dynamically retrieve homologous sequences or MSAs at inference time to condition language model generation or logits.

| Model | Approach | Mean DMS Spearman | Compute / Hardware | Open Weights / Code | Citations |
|---|---|---|---|---|---|
| **AIDO Protein-RAG (16B)** | 16B PLM + dynamic MSA retrieval | **0.5419** | Multi-GPU cluster | Model weights restricted/large | [AIDO team 2024](https://openreview.net) |
| **VenusREM** | ProSST logits + retrieved evolutionary MSA logits fusion | **0.5357** | 1 GPU + homology search | Open (HuggingFace) | [VenusREM Team 2024](https://huggingface.co/VenusREM) |
| **S3F-MSA** | S3F structure model conditioned on MSA | 0.5154 | GPU | Open | [2024](https://proteingym.org) |
| **S2F-MSA** | S2F structure model conditioned on MSA | 0.5079 | GPU | Open | [2024](https://proteingym.org) |
| **Protriever** | Homology retrieval + sequence language modeling | 0.4989 | GPU | Open | [2024](https://proteingym.org) |
| **PoET (200M)** | Autoregressive generative modeling of homologous MSAs | 0.4898 | 1 GPU (8 GB) / CPU slow | Open | [Truong & Bepler, 2023](https://arxiv.org/abs/2306.03923) |
| **TranceptEVE (L)** | Autoregressive Tranception L + EVE evolutionary prior | 0.4745 | GPU | Open | [Notin et al., 2023](https://proteingym.org) |
| **MSA Transformer (ens)** | Tied axial attention over MSA rows and columns | 0.4373 | GPU | Open | [Rao et al., ICML 2021](https://proceedings.mlr.press/v139/rao21a.html) |

*Verdict on Retrieval Models:* **Retrieval is the current state-of-the-art paradigm.** Fusing evolutionary homolog statistics with deep neural representations (as done by VenusREM and AIDO) yields the highest accuracy on ProteinGym (~0.53-0.54).

---

### Class 5: Autoregressive / Causal Language Models
Trained with left-to-right next-token prediction. Evaluated zero-shot by the log-likelihood delta across mutated positions.

| Model | Parameters | Mean DMS Spearman | Compute | Notes | Citations |
|---|---|---|---|---|---|
| **Progen3 (3B)** | 3B | 0.4431 | Multi-GPU | Latest Progen generation | [ProFluent 2024](https://profluent.bio) |
| **Progen2 (L)** | 764M | 0.3923 | 1 GPU | Causal Transformer | [Nijkamp et al., 2022](https://arxiv.org/abs/2206.13517) |
| **Progen2 (Base)** | 219M | 0.3807 | 1 GPU | Causal Transformer | [Nijkamp et al., 2022](https://arxiv.org/abs/2206.13517) |
| **RITA (XL)** | 1.2B | 0.3999 | 1 GPU | Autoregressive model | [Hesslow et al., 2022](https://arxiv.org/abs/2205.05789) |
| **ProtGPT2** | 738M | 0.1978 | 1 GPU | Fails zero-shot DMS | [Ferruz et al., Nat Commun 2022](https://doi.org/10.1038/s41467-022-32007-7) |

*Verdict on Autoregressive Models:* Generally underperform bidirectional MLMs on zero-shot substitution benchmarks because causal masking deprives the model of downstream context when scoring a mutation.

---

### Class 6: Variant-Effect Heuristics & Embedded Classifiers

| Model | Approach | Mean DMS Spearman | Compute | Notes | Citations |
|---|---|---|---|---|---|
| **ESCOTT** | Evolutionary & structural conservation scoring | **0.4985** | CPU / MSA search | Top-performing specialized tool | [2024](https://proteingym.org) |
| **RSALOR** | Relative solvent accessibility & log-odds | 0.4848 | Fast CPU | Classical feature combination | [2024](https://proteingym.org) |
| **VespaG** | ProtT5 / ESM embeddings + evolutionary conservation graph | 0.4818 | GPU / CPU | Rost Lab | [Marquet et al., 2023](https://doi.org/10.1093/bioinformatics/btad449) |
| **VESPA** | ProtT5 embeddings + conservation | 0.4630 | CPU feasible | Rost Lab | [Marquet et al., 2021](https://doi.org/10.1093/bioinformatics/btab529) |

---

## 3. Comparative Analysis & Key Lessons

```
Mean DMS Spearman on ProteinGym v1.3 (217 Substitution Assays)
========================================================================================
[Retrieval / Hybrid]
  AIDO Protein-RAG (16B)      | 0.5419 #######################################
  VenusREM                    | 0.5357 ######################################
  S3F-MSA                     | 0.5154 ##################################
  Protriever                  | 0.4989 #################################
  PoET (200M)                 | 0.4898 ################################

[Structure-Quantized]
  ProSST (K=2048)             | 0.5225 ###################################
  SaProt (650M)               | 0.4728 ###############################

[Analytical MSA (Zero Deep Params / CPU Fast)]
  GEMME                       | 0.4743 ###############################
  EVE (ensemble)              | 0.4599 ##############################
  EVmutation                  | 0.4184 #########################

[Pure Sequence MLMs]
  ESM3 open (1.4B)            | 0.4827 ################################
  ESM2 (650M)                 | 0.4382 ###########################
  ESM-C (600M)                | 0.4340 ##########################
  ESM2 (3B)                   | 0.4321 ##########################
  ESM2 (15B)                  | 0.4253 #########################
  ESM2 (150M)                 | 0.4006 ########################
  ESM2 (35M) [CPU Fast]       | 0.3188 ####################
  ESM2 (8M)  [CPU Fast]       | 0.2056 #############

[Pure Inverse Folding]
  ProteinMPNN                 | 0.2950 ###################
========================================================================================
```

### 1. Where do Models Fail?
- **Shallow MSAs ($N_{eff}/L < 1$):** GEMME, EVE, and EVmutation experience catastrophic degradation when homologous alignments are sparse. Pure sequence PLMs (ESM-2, ESM-C) remain robust because their representations rely on global sequence space rather than family-specific depth.
- **Deep MSAs ($N_{eff}/L > 10$):** GEMME and EVE outperform ESM-2 650M by >5-10 Spearman points on deep alignments. ESM-2 cannot match direct co-evolutionary covariance.
- **Epistasis & Multi-Mutants:** Pure site-independent models drop off sharply on multi-mutant fitness landscapes. Structure and pairwise Potts models (EVmutation, GEMME) retain superior relative ranking.

---

## 4. The kbrain Edge: 8 CPU Cores, Zero GPU

kbrain operates on 8 CPU cores and 7 GB RAM. We cannot train or serve 16B parameter models. But our research edge is clear:

1. **Leverage Pre-computed Published Scores:** ProteinGym v1.3 has full published scores for all 97 leaderboard models across all 2.4M mutants in `data/proteingym/zero_shot/`. We can evaluate any ensembling, ranking, or calibration hypothesis in seconds.
2. **CPU-Native Inference Stack:**
   - **GEMME (0.4743):** Pure CPU, zero neural weights. Beats ESM-2 650M out of the box.
   - **ESM-2 (35M):** Lightweight CPU inference.
   - **VESPA (0.4630):** Fast inference.
3. **The Power of Ensembles:** Rank-averaging GEMME with small PLM logits or positional tolerance priors creates a drop-in zero-shot predictor that approaches 0.50 Spearman on CPU alone.
4. **Low-N Supervised Adaptation:** In real protein engineering (24 to 96 measured labels), combining frozen zero-shot priors (GEMME, ESM2) via ridge regression or Bayesian linear regression outperforms any zero-shot model by 10-20 Spearman points.

---

## 5. Frontier Preprints & Critical Reality Checks (2026)

Recent literature (2026 preprints) directly challenges the prevailing industry consensus that broad zero-shot benchmark leadership translates to real-world engineering discovery:

### 1. Epistasis Blindness in Zero-Shot Predictors
- **Paper:** *Beyond additivity: zero-shot methods cannot predict impact of epistasis on protein properties and function*
- **Authors:** Anastasia Kolchina, Igors Dubanevics, Fyodor A. Kondrashov, Olga V. Kalinina (bioRxiv, Feb 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.02.17.706292](https://doi.org/10.64898/2026.02.17.706292) | GitHub: [kalininalab/epistasis_proteingym](https://github.com/kalininalab/epistasis_proteingym)
- **Claims:** Unsupervised variant effect predictors (VEPs) and protein language models fail to predict non-additive epistatic interactions. While models predict single substitutions and additive mutational combinations with reasonable accuracy, performance collapses when predicting variants exhibiting significant epistatic deviations.
- **Benchmark & Baselines:** Evaluated 95 zero-shot models from ProteinGym across multi-mutant DMS datasets against additive single-mutation sums ($\sum \Delta s_i$).
- **Open Code / Weights / Data:** Fully open. Benchmarking code on GitHub; uses publicly available ProteinGym multi-mutant substitutions.
- **Hype vs. Evidence:** **HYPE PUNCTURED.** Disproves the belief that massive PLMs implicitly capture non-linear biochemical or thermodynamic cooperativity across multiple mutations. Standard zero-shot log-odds sums cannot navigate epistatic landscapes without explicit pairwise coupling or experimental supervision.

### 2. Broad Benchmark Illusions & Local Prediction Failures
- **Paper:** *Overestimating zero-shot fitness prediction: Broad benchmarks mask local failures and practical limitations*
- **Authors:** Phillip R. Woolley, Aaron L. Feller, Andrew D. Ellington, Claus O. Wilke (bioRxiv, Jun 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.06.04.730121](https://doi.org/10.64898/2026.06.04.730121)
- **Claims:** High aggregate Spearman scores on broad benchmark suites (such as ProteinGym) mask widespread local prediction failures and dramatic protein-to-protein variance. Zero-shot models act primarily as coarse binary filters that separate dead/unfolded variants from functional ones. They lack resolution to distinguish among fit mutations, cannot optimize "new-to-nature" phenotypes, and are heavily confounded by cellular abundance and experimental noise.
- **Benchmark & Baselines:** Systematic evaluation of sequence-only, structure-based, and hybrid foundation models across ProteinGym DMS assays.
- **Open Code / Weights / Data:** Fully open preprint, data, and scripts.
- **Hype vs. Evidence:** **HYPE REVISE.** Zero-shot models are useful for library depuration (pruning deleterious variants), but claiming they can "hallucinate" or rank top-tier functional variants for targeted protein engineering is scientifically unfounded.

### 3. Decision Benchmarking & The Value of Wet-Lab Measurements
- **Paper:** *Decision benchmarking reveals when protein foundation models add experimental value*
- **Authors:** Wenze Ding, Chenlin Lu, Yao Li, Haipeng Gong, Zhiyong Wang (bioRxiv, Oct 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.10.13.758966](https://doi.org/10.64898/2026.10.13.758966)
- **Claims:** Formulates protein engineering as an active decision problem rather than a static ranking task. Evaluates 95 predictors across 217 ProteinGym assays (2.47M variants). Zero-shot ranking accuracy explains <20% of discovery variance. Calibrated computational priors add value only in early low-N rounds ($N \approx 20-100$). Experimental measurements surpass zero-shot foundation models after 50–100 wet-lab measurements for top-candidate discovery, and ~500 measurements for global landscape ranking.
- **Benchmark & Baselines:** Iterative acquisition rounds across 217 ProteinGym assays compared against empirical measurements, budget-matched random screening, and additive linear models.
- **Open Code / Weights / Data:** Fully open preprint and benchmarking code.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Replaces marketing claims with an empirical crossover curve: wet-lab screening budget rapidly outcompetes computational model size beyond $N=50-100$. Strongly justifies kbrain's strategic focus on the low-N supervised track ($N \in [24, 96]$).

### 4. Mechanistic Interpretability & Latent 3D Spatial Circuits
- **Paper:** *Towards Sparse Causal Features for Zero-shot Mutation Effect Prediction in a Protein Language Model*
- **Authors:** Saishradha Mohanty, Manya Phutela, Anna G. Green (bioRxiv, Aug 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.08.28.747907](https://doi.org/10.64898/2026.08.28.747907)
- **Claims:** Dissects ESM-2 (650M) internal representations during zero-shot mutation scoring using Sparse Autoencoders (SAEs), integrated gradients, and activation patching. Demonstrates that causal prediction circuits map directly to residues in physical 3D contact with the mutated residue. Amino acid substitutions sharing biochemical properties reuse 40%–75% of causal feature circuits.
- **Benchmark & Baselines:** ESM-2 (650M) zero-shot scoring on ProteinGym DMS assays (e.g. DNAJA1) evaluated by indirect causal effect vs raw activation magnitude.
- **Open Code / Weights / Data:** Fully open code and SAE feature checkpoints.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Mechanistically explains why sequence-only PLMs perform well on stability: their internal representations learn emergent 3D contact maps from evolutionary co-variation. Also explains why explicit structure models offer only marginal incremental gains over ESM-2 on many standard single-point assays.

### 5. Training-Free Retrieval & Structural Shrinkage (VenusREM2)
- **Paper:** *A General Harness for Protein Foundation Model Fitness Prediction*
- **Authors:** Yang Tan, Qijia Tian, Gangyu Sun, Bozitao Zhong, Mingchen Li (arXiv, Sep 2026)
- **Citations / Links:** [arXiv:2609.34654](https://arxiv.org/abs/2609.34654)
- **Claims:** Introduces VenusREM-Harness (VRH), a model-agnostic, training-free framework that fuses frozen foundation model scores with multiple sequence alignment (MSA) evidence according to model prediction uncertainty. It then applies gated background correction and score shrinkage based on AlphaFold2 structural confidence (pLDDT) and solvent accessibility (SASA).
- **Benchmark & Baselines:** Evaluated across 1,211 assays and 3.1M variants spanning ProteinGym, VenusMutHub, and VenusViroHub against 71 baseline configurations.
- **Result:** Built with VRH, **VenusREM2** achieves a new state-of-the-art **0.5560 ProteinGym Average Spearman** (+0.038 above prior leader AIDO Protein-RAG / VenusREM v1), ranking #1 across all functional classes, taxa, MSA-depth, and mutation-depth regimes.
- **Open Code / Weights / Data:** Code and evaluation harness open on GitHub / VenusMutHub.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED / PARADIGM SHIFT.** Proves that beating the scaling plateau does not require training larger billion-parameter models from scratch. Model-agnostic calibration combining evolutionary MSA retrieval with physical solvent-exposure shrinkage reliably lifts frozen PLMs by ~0.07 Spearman.

### 6. Shared Decoders for Cross-Protein Stability Transfer (StabilityArc)
- **Paper:** *StabilityArc: Decoding Protein Sequence Embeddings into Generalizable Stability Landscapes*
- **Authors:** Aaron L. Feller, Andrew D. Ellington, Claus O. Wilke (arXiv, Sep 2026)
- **Citations / Links:** [arXiv:2610.00742](https://arxiv.org/abs/2610.00742)
- **Claims:** Universal biochemical and thermodynamic rules govern stability across diverse folds. StabilityArc passes frozen ESMC-600M residue embeddings through a shared RoPE transformer decoder to generate an $L \times 20$ full-mutational matrix, adding a symmetric contact-aware residual to capture pairwise epistasis.
- **Benchmark & Baselines:** Strict leave-one-protein-out cross-validation across 66 ProteinGym stability assays (134,794 variants) against ProSST-2048, ESM-2, and Kermut.
- **Result:** Achieves **0.7134 Spearman correlation** on held-out proteins, exceeding ProSST-2048 (0.6526) by +0.0608. Supplying StabilityArc scores as priors to Kermut lifts supervised performance to **0.8280** (improving over Kermut's 0.8167).
- **Open Code / Weights / Data:** Fully open preprint and codebase.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Establishes that zero-shot PLM representations can be decoded into generalizable stability matrices across unseen proteins, eliminating per-target model training for folding stability.

### 7. Linear Fitness Subspaces in PLMs for Low-N Directed Evolution
- **Paper:** *Linear Fitness Subspace in Protein Language Models Enables Sample-Efficient Directed Evolution*
- **Authors:** SiYuan Ma, Canran Xiao, Zikai Xiao, Albert Gao, Liang He (arXiv, Oct 2026)
- **Citations / Links:** [arXiv:2610.07607](https://arxiv.org/abs/2610.07607)
- **Claims:** Formulates the Linear Fitness Subspace (LFS) hypothesis: within mutation-induced residue representation deltas ($\Delta z = z_{\text{mut}} - z_{\text{wt}}$), a compact, assay-specific set of directions makes fitness variation linearly accessible from few labeled variants. Proposes Subspace-Guided Evolutionary Search (SGES), which identifies this subspace using Partial Least Squares (PLS) from minimal initial samples ($N \in [12, 48]$) to perform surrogate modeling and acquisition.
- **Benchmark & Baselines:** 10 core ProteinGym DMS assays, 87 static validation assays, and 18-assay budgeted search vs zero-shot PLMs, PCA, random projections, and Gaussian processes.
- **Open Code / Weights / Data:** Open preprint and code repository.
- **Hype vs. Evidence:** **HIGHLY RELEVANT TO KBRAIN.** Directly explains why regularized linear models (ridge regression) on PLM representations and zero-shot priors succeed at low N: mutation effects locally lie in low-dimensional linear manifolds.

### 8. Compute-Efficient Modern Architectures (ProtModernBERT)
- **Paper:** *ProtModernBERT: Compute-Efficient Protein Language Modeling*
- **Authors:** Alberto Martínez, Natalia Flechas Manrique, Llorenç Espinosa-Portalés, Luc Andrea (arXiv, Oct 2026)
- **Citations / Links:** [arXiv:2610.19738](https://arxiv.org/abs/2610.19738)
- **Claims:** Modernizes protein language model architectures by incorporating RoPE (Rotary Position Embeddings), FlashAttention, GeGLU activations, and sequence unpadding.
- **Benchmark & Baselines:** Evaluated against ProtBert, Amplify-120M, and ESM2 across structural tasks and ProteinGym zero-shot substitution benchmarks.
- **Result:** Matches Amplify-120M and ProtBert performance with an **80%–90% reduction in pre-training FLOPs**, narrowing the gap to ESM2 when controlling for pre-training data.
- **Open Code / Weights / Data:** Open-source architecture and checkpoints.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Validates that architectural modernization is more consequential than raw parameter count in compute-constrained regimes.
