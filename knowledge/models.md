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

### 9. Inference-Only Dropout for Training-Free Zero-Shot Boosting
- **Paper:** *Protein Language Model Zero-Shot Fitness Predictions are Improved by Inference-only Dropout*
- **Authors:** Aditya Ravuri, Neil D. Lawrence (arXiv, Jun 2025)
- **Citations / Links:** [arXiv:2506.14793](https://arxiv.org/abs/2506.14793)
- **Claims:** Injecting a simple stochastic dropout layer ($p \approx 0.1$) solely at inference time between the PLM featurizer/embedding layer and its transformer blocks, then averaging log-probabilities across multiple stochastic forward passes (Monte Carlo dropout), consistently boosts zero-shot mutational effect prediction accuracy on ProteinGym. Crucially, this requires **no retraining or fine-tuning**, functioning effectively even on models (such as standard ESM-2 checkpoints) originally trained with zero dropout.
- **Benchmark & Baselines:** ProteinGym DMS substitution subsets evaluated across ESM-2 model scales (8M, 35M, 150M, 650M) against deterministic single forward-pass zero-shot scoring.
- **Result:** Median Spearman rank correlation coefficient (SRCC) increases across protein families, with relative improvements reaching **up to ~22% SRCC on small models** (8M and 35M parameter regimes). An optimal dropout rate of $p = 0.1$ is remarkably robust across architectures.
- **Open Code / Weights / Data:** Preprint open; implementation is standard PyTorch CPU compatible (`torch.nn.functional.dropout`).
- **Hype vs. Evidence:** **HIGHLY ACTIONABLE FOR KBRAIN.** Demonstrates that test-time uncertainty marginalization lifts small, CPU-runnable PLMs toward larger GPU counterparts at the cost of only $K$ forward passes (minutes on CPU).

### 10. Distogram Encoded Energetic Potentials (DEEP-Boltz)
- **Paper:** *DEEP: Extracting Latent Energetic Landscapes from Protein Structure Predictors*
- **Authors:** Zsófia Rózsa, Gábor Erdős (bioRxiv, Oct 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.10.15.759389](https://doi.org/10.64898/2026.10.15.759389)
- **Claims:** Modern biomolecular structure predictors learn latent energetic representations in their pairwise distance distribution heads (distograms). The DEEP framework extracts effective statistical potentials directly from these distograms using the model's terminal distance state as an internal reference, requiring **zero training on experimental stability data**.
- **Benchmark & Baselines:** Evaluated on 64 biophysical stability DMS assays from ProteinGym (134k+ variants) against all 97 published zero-shot methods on the leaderboard, plus 180,000+ Rosetta decoy conformations.
- **Result:** Applied to Boltz-2 (**DEEP-Boltz**), achieves a mean per-assay Spearman correlation of **0.720**, numerically outperforming every published zero-shot baseline on the ProteinGym stability track and matching top supervised predictors. Intriguingly, applying DEEP to AlphaFold2 yields strong decoy discrimination but significantly weaker mutation sensitivity, indicating Boltz-2 possesses uniquely sequence-sensitive internal energetic representations.
- **Open Code / Weights / Data:** Preprint and computational tool open on GitHub / bioRxiv.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED / FRONTIER RESULT.** Establishes that next-generation biomolecular structure foundation models (Boltz-2) encode thermodynamic stability landscapes within their distograms without explicit energy supervision.

### 11. Generalization Across Distribution Shifts via Structural & Co-evolutionary Priors
- **Paper:** *Generalizing Protein Fitness Prediction Across Distribution Shifts via Structural and Co-evolutionary Priors*
- **Authors:** Nopsinth Vithayapalert, Maytus Piriyajitakonkij, Francesca Grisoni (bioRxiv, Oct 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.10.06.756934](https://doi.org/10.64898/2026.10.06.756934)
- **Claims:** Protein fitness predictors frequently collapse when directed evolution forces out-of-distribution (OOD) extrapolation to unseen positions or distinct protein backbones. By pairing structure-aware PLMs with pooled representations from an AlphaFold-style trunk (integrating MSA co-evolution and sequence), models attain robust OOD generalization.
- **Benchmark & Baselines:** FLIP2 benchmark suite and ProteinGym OOD splits across mutational distance, position-holdout, and backbone-holdout shifts against ESM-2, ProSST, and SaProt baselines.
- **Result:** Dissects exact prior contributions: **structural priors** drive generalization across unseen protein backbones, whereas **co-evolutionary trunk representations (MSAs)** are specifically required to enable generalization to unmutated structural positions.
- **Open Code / Weights / Data:** Fully open preprint and benchmarking code.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Replaces vague claims about "general intelligence" in PLMs with mechanistic clarity: structure gives fold invariance, while evolutionary MSAs give positional extrapolative power.

### 12. Intrinsic Dataset Features and the Site-Mean Leakage Trap
- **Paper:** *Intrinsic dataset features drive mutational effect prediction by protein language models*
- **Authors:** Luiz C. Vieira, Sophia Lin, Claus O. Wilke (bioRxiv, Mar 2026)
- **Citations / Links:** [bioRxiv:10.64898/2026.03.08.710389](https://doi.org/10.64898/2026.03.08.710389)
- **Claims:** High reported supervised and transfer-learning accuracies on DMS benchmarks are heavily confounded by dataset-level site effects. A naive baseline that predicts only the **empirical site mean fitness** matches or exceeds complex supervised PLMs on numerous assays. Furthermore, random cross-validation splits in benchmarks like ProteinGym induce severe data leakage: models memorize position-specific tolerance rather than learning general mutational biophysics.
- **Benchmark & Baselines:** Systematic evaluation across ProteinGym viral and cellular DMS datasets under random vs site-stratified splits against site-mean-only baselines and ESM architectures.
- **Result:** Supervised PLM performance plunges under site-stratified splitting. Quantifies the Relative Variability of Site Means (RVSM) and Fraction of Highly Variable Sites (FHVS) as the primary determinants of apparent model success. Shows PLMs systematically underperform on viral targets due to divergent evolutionary pressures.
- **Open Code / Weights / Data:** Fully open preprint, code, and processed datasets.
- **Hype vs. Evidence:** **CRITICAL VALIDATION FOR KBRAIN RIGOR.** Directly mirrors and generalizes kbrain's empirical skeptic finding on random vs contiguous low-N splits: random CV permits one-hot regressors to fit site means, creating an illusion of mutational learning that evaporates on position-disjoint splits.

### 13. TriFit: Trimodal Fusion with Protein Dynamics
- **Paper:** *TriFit: Trimodal Fusion with Protein Dynamics for Mutation Fitness Prediction*
- **Authors:** Seungik Cho (arXiv, Apr 2026)
- **Citations / Links:** [arXiv:2604.12026](https://arxiv.org/abs/2604.12026)
- **Claims:** Protein language models and static structures ignore conformational dynamics (residue flexibility, allosteric coupling, normal mode vibrations). TriFit integrates sequence (ESM-2 650M masked marginals), structure (AlphaFold2 C-alpha coordinates), and dynamics (Gaussian Network Model / GNM B-factors, mode shapes, and cross-correlations) via a 4-expert Mixture-of-Experts (MoE) fusion module.
- **Benchmark & Baselines:** ProteinGym v1.3 substitution benchmark (217 DMS assays, 696k SAVs) against supervised baselines Kermut, ProteinNPT, and zero-shot ESM3.
- **Result:** Achieves AUROC 0.897 +/- 0.0002, outperforming Kermut (0.864) and ProteinNPT (0.844). Crucially, ablation confirms that **dynamics contributes the largest marginal gain** over pairwise modality combinations, and outputs exhibit near-perfect calibration (ECE = 0.044) without post-hoc scaling.
- **Open Code / Weights / Data:** Preprint open; GNM normal mode analysis is analytical and computable on CPU in milliseconds via contact matrix decomposition.
- **Hype vs. Evidence:** **HIGHLY RELEVANT TO KBRAIN CPU EDGE.** Proves that conformational dynamics provide orthogonal signal to sequence PLMs; because Gaussian Network Models require only an AlphaFold2 C-alpha contact matrix and an analytical eigensolver (numpy/scipy on CPU), dynamics features can be extracted locally without GPUs.

### 14. Reverse Distillation: Matryoshka Representation Scaling for PLMs
- **Paper:** *Reverse Distillation: Consistently Scaling Protein Language Model Representations*
- **Authors:** Darius Catrina, Christian Bepler, Samuel Sledzieski, Rohit Singh (arXiv, Mar 2026)
- **Citations / Links:** [arXiv:2603.07710](https://arxiv.org/abs/2603.07710); Code: [github.com/rohitsinghlab/plm_reverse_distillation](https://github.com/rohitsinghlab/plm_reverse_distillation)
- **Claims:** Resolves the well-documented PLM scaling ceiling (where ESM-2 650M beats 3B and 15B on ProteinGym) by decomposing large PLM representations into orthogonal Matryoshka-style subspaces guided by smaller models. Constrained smaller models (e.g., 35M/150M) isolate core, broadly-shared biophysical features, while larger models supply orthogonal capacity without catastrophic interference.
- **Benchmark & Baselines:** ProteinGym zero-shot substitution benchmark across ESM-2 scales (8M to 15B) vs standard ESM-2 embeddings.
- **Result:** Reverse-distilled ESM-2 variants consistently outperform baseline models at identical embedding dimensions, restoring monotonic scaling: the reverse-distilled 15B model achieves the strongest overall performance on the benchmark.
- **Open Code / Weights / Data:** Code and trained checkpoints publicly available.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Provides a rigorous theoretical and empirical explanation for why small PLMs (which we run on CPU) capture the essential primary manifold of fitness, and provides a blueprint for nested feature extraction.

### 15. Proust: Compute-Efficient Causal PLMs for Zero-Shot Fitness
- **Paper:** *No Generation without Representation: Efficient Causal Protein Language Models Enable Zero-Shot Fitness Estimation*
- **Authors:** Furkan Eris (arXiv, Feb 2026)
- **Citations / Links:** [arXiv:2602.01845](https://arxiv.org/abs/2602.01845); Code: [github.com/Furkan9015/proust-inference](https://github.com/Furkan9015/proust-inference)
- **Claims:** Bridges the traditional divide between masked language models (MLMs, optimal for fitness scoring) and causal autoregressive models (optimal for generative design). Introduces Proust (309M parameters), integrating modern LLM architecture: grouped-query attention (GQA) with shared K/V projections, cross-layer value residuals, and depthwise causal convolutions.
- **Benchmark & Baselines:** ProteinGym substitutions and indels against ESM-2, ProGen2, and EVEREST viral fitness.
- **Result:** Trained on 33B tokens in only 40 B200 GPU-hours, Proust attains Spearman rho = 0.390 on ProteinGym substitutions (approaching models requiring 50-200x more pretraining compute) and establishes a new state-of-the-art on ProteinGym indels, while retaining native autoregressive sequence generation capabilities.
- **Open Code / Weights / Data:** Inference code and weights fully open source.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Confirms that modern causal architectural efficiency translates directly to variant scoring and indel fitness estimation.

### 16. VenusREM2 & VenusREM-Harness: Model-Agnostic Retrieval Logits Fusion
- **Paper:** *A General Harness for Protein Foundation Model Fitness Prediction* (and *From high-throughput evaluation to wet-lab studies: advancing mutation effect prediction with a retrieval-enhanced model*, Bioinformatics/ISMB)
- **Authors:** Yang Tan, Qijia Tian, Gangyu Sun, Bozitao Zhong, Mingchen Li, Yuanxi Yu, Nanqing Dong, Liang Hong (arXiv, Sep 2026)
- **Citations / Links:** [arXiv:2609.34654](https://arxiv.org/abs/2609.34654); GitHub: [github.com/MatBiomed/remharness](https://github.com/MatBiomed/remharness)
- **Claims:** Protein foundation models (PFMs) miss fine-grained evolutionary conservation and family-specific epistatic constraints when scored in isolation. VenusREM-Harness (`vrh`) introduces a training-free, plug-and-play harness that boosts *any* frozen foundation model (ESM-2, SaProt, ProSST, ProteinMPNN) by retrieving homologous sequence alignments (MSAs) and performing adaptive uncertainty-weighted logit fusion, amino acid background correction, and structure-conditioned shrinkage without parameter fine-tuning.
- **Benchmark & Baselines:** Evaluated across the 217 ProteinGym v1.3 DMS substitution benchmark assays against all 97 published single-model baselines.
- **Result:** VenusREM2 achieves an average per-assay Spearman correlation of **0.556**, setting the current SOTA record on the ProteinGym substitution leaderboard (surpassing un-augmented ESM-2 650M at 0.446, GEMME at 0.470, and AIDO.Protein-RAG at 0.518).
- **Open Code / Weights / Data:** Fully open-source Python harness (`vrh`) and weights on GitHub.
- **Hype vs. Evidence:** **LEADERBOARD FRONTIER / HIGH RELEVANCE.** Demonstrates that post-hoc retrieval logit fusion beats end-to-end retraining. Directly inspires CPU-native score combination methods at kbrain (blending our published GEMME/Site-Independent and ESM2/SaProt scores).

### 17. Cerebra-Epistasis: Composable Epistasis-Aware Mutation Atlas
- **Paper:** *From single-sequence structure prediction to protein fitness landscape through a composable, epistasis-aware mutation atlas*
- **Authors:** Weizhe Wang, Zimu Yu, Endi Yang, Ziyu Shi, Shize Yu, Jian Hu, Yunxin Xu, Haipeng Gong (bioRxiv, Sep 2026)
- **Citations / Links:** [bioRxiv:10.1101/2026.09.28.679124](https://doi.org/10.1101/2026.09.28.679124); GitHub: `Cerebra-Epistasis`
- **Claims:** Current zero-shot PLMs assume additive log-odds combinations across mutated sites ($\sum \Delta \log P$), severely degrading when evaluating higher-order multi-mutants dominated by non-additive epistasis (sign and reciprocal sign epistasis). Cerebra-Epistasis extracts single-sequence structural representations once (`Cerebra-Seq`), builds a composable mutation atlas of residue-level perturbations, and feeds them into an explicit epistatic interaction module that maps combinatorial landscapes from low-order (single/double) mutant calibration data.
- **Benchmark & Baselines:** Combinatorial Deep Mutational Scanning datasets (GB1 4-site combinatorial, beta-lactamase, fluorescent proteins, ProteinGym multi-mutants) compared against additive ESM-2, ProteinNPT, and standard epistatic regression.
- **Result:** Drastically outperforms additive zero-shot baselines at mutation depth $\ge 3$, capturing synergistic mutational jumps and avoiding dead-end lethal combinations that additive models falsely predict as beneficial.
- **Open Code / Weights / Data:** Code and preprint publicly available on GitHub and bioRxiv.
- **Hype vs. Evidence:** **CONFIRMED & CRITICAL RIGOR ALIGNMENT.** Corroborates kbrain's empirical skeptic finding that supervised augmented ridge gains are concentrated in multi-mutants; demonstrates that explicit modeling of pairwise interaction terms ($J_{ij}$) is the essential bridge from single-mutant screening to combinatorial engineering.

### 18. EvoIF: Evolutionary Profiles via Inverse Reinforcement Learning
- **Paper:** *Evolutionary Profiles for Protein Fitness Prediction*
- **Authors:** Jigang Fan, Xiaoran Jiao, Shengdong Lin, Zhanming Liang, Weian Mao, Chenchen Jing, Hao Cheng, Chunhua Shen, et al. (arXiv, Oct 2025 / 2026)
- **Citations / Links:** [arXiv:2510.07286](https://arxiv.org/abs/2510.07286)
- **Claims:** Formulates zero-shot fitness prediction through an Inverse Reinforcement Learning (IRL) framework, mathematically showing that Masked Language Modeling on extant natural sequences is equivalent to Maximum Entropy IRL where natural sequences represent expert trajectories. Proposes EvoIF, a compact model that integrates within-family evolutionary profiles (retrieved sequence homologs) with cross-family inverse-folding structural constraints (inverse folding logits).
- **Benchmark & Baselines:** ProteinGym substitution benchmarks vs massive PLMs (ESM-2 3B/15B, ProtBert, ESM-IF1).
- **Result:** Matches or outperforms multi-billion parameter PLMs on zero-shot fitness prediction while using an order-of-magnitude fewer parameters and dramatically lower pre-training data, maintaining robust calibration across deep mutational variants.
- **Open Code / Weights / Data:** Code and model architectures open on GitHub / arXiv.
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Solidifies the theoretical foundation connecting evolutionary density estimation with fitness estimation, showing that compact dual-profile models rival massive monolithic PLMs.

### 19. AIDO.Protein-RAG & ProSST: Quantized Structure and Retrieval Frontiers
- **Papers:** *AIDO.Protein-RAG: Retrieval Augmented Protein Language Models for Structure and Fitness Prediction* (GenBio AI, MBZUAI, CMU, 2025/2026) & *Protein Language Modeling with Quantized Structure and Disentangled Attention (ProSST)* (Li et al., NeurIPS 2024 / bioRxiv)
- **Citations / Links:** [bioRxiv:10.1101/2024.11.14.623617](https://doi.org/10.1101/2024.11.14.623617); [arXiv:2404.09260](https://arxiv.org/abs/2404.09260)
- **Claims:** ProSST converts local 3D backbone coordinates into discrete structural tokens via vector quantization, enabling disentangled sequence-structure self-attention. AIDO.Protein-RAG scales this paradigm to a 16B Mixture-of-Experts (MoE) backbone with ultra-fast hierarchical MSA retrieval, infusing co-evolutionary context even when homologous alignments are sparse.
- **Benchmark & Baselines:** ProteinGym v1.3 substitution benchmark (217 assays) vs ESM-2 650M/3B and MSA-Transformer.
- **Result:** AIDO.Protein-RAG reaches ~0.518 average Spearman on ProteinGym, tied with top leaderboard models. ProSST demonstrates that quantized 3D geometric tokens yield significant gains on biophysical stability assays compared to pure 1D sequence models.
- **Open Code / Weights / Data:** Checkpoints and code open on Hugging Face (`genbio-ai/AIDO.Protein-RAG`, `Li-Lab-Tsinghua/ProSST`).
- **Hype vs. Evidence:** **EVIDENCE CONFIRMED.** Proves that discrete structural quantization and RAG indexing are the dominant architectural paradigms driving current frontier protein models.

### 20. Constraint-Aware Anti-Symmetric Optimization for Thermodynamic Stability (SPURS-AntiSym)
- **Paper:** *Constraint-Aware Optimization for Robust Protein Stability Prediction*
- **Authors:** A Shivram, Aneesh S. Chivukula, Manik Gupta, Sourav Chowdhury (arXiv, Jun 2026)
- **Citations / Links:** [arXiv:2606.08100](https://arxiv.org/abs/2606.08100)
- **Claims:** Modern multimodal $\Delta\Delta G$ predictors (integrating sequence PLMs with inverse-folding representations like ESM + ESM-IF1 / SPURS) suffer from three severe pathologies: out-of-distribution (OOD) performance collapse, pervasive forward-reverse asymmetry ($\Delta\Delta G(A \to B) \neq -\Delta\Delta G(B \to A)$), and systematic under-prediction of rare stabilizing mutations. Rather than adding model parameters, this work introduces optimization-level interventions: Balanced MSE, a Siamese anti-symmetric regularizer, and an OOD-margin consistency loss on per-position feature representations.
- **Benchmark & Baselines:** Evaluated across 11 biophysical stability benchmarks (MegaScale, S669, S461, Ssym, Myoglobin, p53) against SPURS, ThermoMPNN, and ESM baselines.
- **Result:** Improves Spearman correlation on S669 from 0.486 to 0.540 ($\sigma = 0.002$) and on S461 from 0.653 to 0.711 with zero architectural modifications to the backbone. Diagnostic testing on Ssym shows anti-symmetric regularization acts as an implicit regularizer that prevents spurious overconfidence on destabilizing variants.
- **Open Code / Weights / Data:** Benchmark scripts and optimization pipelines released on GitHub / arXiv.
- **Hype vs. Evidence:** **CRITICAL RIGOR CONFIRMATION.** Confirms that thermodynamic consistency violations degrade empirical stability predictors, proving that enforcing anti-symmetry during inference or low-N regression directly improves generalization.

### 21. Mutation Perturbation Fields & Direct-Distal Attention (RipplePLM)
- **Paper:** *RipplePLM: Structural and Property Decoupling for Protein Mutation Effect Generation*
- **Authors:** Liuzhenghao Lv, Yuyang Liu, Yuyang Gao, Li Yuan (arXiv, Oct 2026)
- **Citations / Links:** [arXiv:2610.01891](https://arxiv.org/abs/2610.01891); GitHub: [Lyu6PosHao/RipplePLM](https://github.com/Lyu6PosHao/RipplePLM)
- **Claims:** Standard PLMs smear mutational perturbations across the entire sequence representation, conflating direct physical contact disruptions with indirect distal allosteric shifts. RipplePLM builds a residue-level Mutation Perturbation Field from PLM embeddings and uses Direct-Distal Cross-Attention (DDCA) to partition features into two explicit structural pathways: the mutation site's immediate contact shell (<6 Å) and its multi-hop distal neighborhood, coupled with a Property Latent Chain (PLChain) injecting explicit biophysical constraints.
- **Benchmark & Baselines:** Evaluated on MutaDescribe structural splits and low-N fitness regression benchmarks against mutation-specific PLMs and general LLMs.
- **Result:** Increases structural-split ROUGE-L from 22.23 to 35.65 and shows consistent improvements in low-N fitness regression by preventing distant, non-interacting residues from corrupting the mutation representation.
- **Open Code / Weights / Data:** Open source on GitHub: `Lyu6PosHao/RipplePLM`.
- **Hype vs. Evidence:** **SOLID EVIDENCE / VALUABLE ARCHITECTURAL LESSON.** Confirms that separating local direct contacts from global distal background is essential for sample-efficient low-N regression.

### 22. Orthogonal Projection of PLM Embeddings for Interpretable Fitness Prediction
- **Paper:** *Interpreting Protein Language Model Embeddings via Orthogonal Projection for Protein Fitness Prediction*
- **Authors:** Paulo Yanez Sarmiento, Pia Francesca Rissom, Manuel Pfeuffer, Marco Simnacher (arXiv, Aug 2026)
- **Citations / Links:** [arXiv:2608.25548](https://arxiv.org/abs/2608.25548)
- **Claims:** It is actively debated whether PLMs learn genuine higher-order 3D structural packing and evolutionary context, or simply memorize trivial tabular physicochemical properties (charge, hydropathy, volume). This work uses orthogonal subspace projection to mathematically excise the linear and non-linear effects of standard physicochemical descriptors (AAindex) from PLM embedding vectors before downstream regression.
- **Benchmark & Baselines:** Evaluated on deep mutational scanning fitness prediction datasets, measuring the degradation of regression performance after projecting out interpretable chemical features.
- **Result:** Demonstrates that standard tabular biochemical descriptors explain a substantial fraction of PLM fitness variance, but a robust non-reducible residual variance remains that correlates with spatial contact topology.
- **Open Code / Weights / Data:** Python implementation open on arXiv / GitHub.
- **Hype vs. Evidence:** **VALUABLE AUDITING TOOL FOR KBRAIN.** Provides an exact mathematical framework to audit whether our low-N regressors and zero-shot scores are discovering genuine contextual biology or merely re-indexing amino-acid lookup tables.

### 23. Explicit Cross-Chain Geometry Residual Correction for Interface Mutants (CIR-DDG)
- **Paper:** *CIR-DDG: backbone-agnostic residual correction of antibody-antigen affinity changes with explicit cross-chain geometry*
- **Authors:** Weilun Yu, Zhiheng Zou, Yonggui Huang, Honggang Qi, Geguang Pu (arXiv, Aug 2026)
- **Citations / Links:** [arXiv:2608.27530](https://arxiv.org/abs/2608.27530); GitHub: [ecnuabmlab/CIR-ddG](https://github.com/ecnuabmlab/CIR-ddG)
- **Claims:** Heterogeneous protein complex predictors (PLM-based or equivariant GNNs) routinely drop critical interface geometry in their scalar outputs, failing to preserve explicit cross-chain contact density and site-partner context. CIR-DDG introduces a lightweight residual adapter combining a fixed base model prediction with 22 interpretable geometric descriptors (cross-chain distance, contact coordination number, partner residue context).
- **Benchmark & Baselines:** SKEMPI 2.0 (343 complexes, 5-fold CV) across six diverse backbones, and independent zero-shot transfer on the SARS-CoV-2 RBD-ACE2 deep mutational scan (3,669 substitutions).
- **Result:** Improves interface mutation Spearman correlation across all six backbones on SKEMPI by +0.0346 to +0.1296 (RMSE drops by 0.0074–0.0408 kcal/mol). Transferred zero-shot without retraining to the SARS-CoV-2 RBD-ACE2 DMS benchmark, boosting absolute interface Spearman correlation by +0.026 to +0.081 across all backbones.
- **Open Code / Weights / Data:** Open source at GitHub: `ecnuabmlab/CIR-ddG`.
- **Hype vs. Evidence:** **CRITICAL PRACTICAL LESSON FOR CPU ARCHITECTURES.** Proves that simple, CPU-computable geometric contact features can provide an orthogonal, training-free additive correction to black-box PLM predictions on protein-protein interfaces.

### 24. Order-Resolved Epistatic Information Tracking & Reproducibility in PLMs (ORBIT-FMIB)
- **Paper:** *ORBIT-FMIB: Tracking Order-Resolved Epistatic Information Through ESM-2*
- **Authors:** Maryam Rahimimovassagh, Ivan Garibay, Niloofar Yousefi (arXiv, Sept 2026)
- **Citations / Links:** [arXiv:2610.00672](https://arxiv.org/abs/2610.00672)
- **Claims:** Formulates a diagnostic framework combining Walsh-based interaction decomposition with subset-conditioned neural dependence estimation to track whether ESM-2 retains higher-order epistatic interaction information as strongly as first- and second-order information across its representation hierarchy.
- **Benchmark & Baselines:** Evaluated on synthetic fitness landscapes with known epistatic structures and the dense four-site GB1 combinatorial deep mutational scan across ESM-2 layer depths.
- **Result:** Provides an exemplary negative/reproducibility result. While an initial production run suggested ESM-2 selectively loses higher-order epistasis ($\Delta_{\mathrm{HO-LO}} = -0.107$), a rigorous matched replication across seeds and critic pairings substantially reduced the contrast to $\Delta_{\mathrm{HO-LO}} = -0.017$, with sign instability ($-0.011$ to $+0.015$). Concludes there is currently no robust evidence that ESM-2 representation hierarchy selectively degrades higher-order epistatic information.
- **Open Code / Weights / Data:** Diagnostic framework and replication code open on arXiv / GitHub.
- **Hype vs. Evidence:** **EXEMPLARY RIGOR BENCHMARK.** A vital methodological warning for kbrain: probing combinatorial epistasis with neural critics without matched replication easily mistakes critic evaluation artifacts for fundamental PLM representation limitations.

### 25. Transferable Historical Utility Priors for Low-N Predictor Routing (AssayRouter)
- **Paper:** *AssayRouter: Historical Utility Priors for Frozen Molecular Predictor Routing*
- **Authors:** Dong Xu, Zhangfan Yang, Jiantao Wu, Shipeng Zhang, Zexuan Zhu (arXiv, Sept 2026)
- **Citations / Links:** [arXiv:2609.37285](https://arxiv.org/abs/2609.37285)
- **Claims:** Laboratories facing a new target assay with only 16–64 labels cannot reliably pick the best predictor using support-set correlation or cross-validation alone due to high noise and selection variance. AssayRouter treats completed historical assays as pseudo-targets, labeling each candidate model by its post-fit held-out utility (the reduction in discovery loss when added to the local predictor). A shared meta-regressor learns to predict candidate utility solely from model behavior on the support set, outputting a convex blend of top predictors.
- **Benchmark & Baselines:** Evaluated across 24 external regression assays across six frozen interface families against support-set CV (`Support-CV@4`).
- **Result:** Lowers strict four-call negative log-likelihood (NLL) by 0.0409 over standard support-set cross-validation and generalizes across leave-one-interface-out predictor families.
- **Open Code / Weights / Data:** Method and training pipelines open on arXiv.
- **Hype vs. Evidence:** **DIRECTLY ACTIONABLE FOR KBRAIN LOW-N REGIMES.** Directly solves the empirical instability observed in our Candidate C2 (24-label routing): by substituting noisy support-set argmax selection with historical utility priors learned across completed ProteinGym assays, 24-label routing can become robust and monotonic.

### 26. Global Mutation Perturbation Regimes & Protein Fragility Maps (RegimeFormer & RegimeAtlas)
- **Paper:** *RegimeFormer: A Large Protein Model of Global Perturbation Regimes*
- **Authors:** Siyuan Ma, Yi Chai, Yi Wu, Qixin Zhang, Yajing Yuan (arXiv, Aug 2026)
- **Citations / Links:** [arXiv:2608.26586](https://arxiv.org/abs/2608.26586)
- **Claims:** Sequence PLMs predict local mutational shifts but lack an explicit global representation of how whole protein scaffolds respond to perturbation. RegimeFormer harmonizes 202M non-redundant sequences across the tree of life (with a 1M protein high-resolution inference layer over 407M residues) into RegimeAtlas, identifying universal protein perturbation regimes that organize residue fragility, structural adaptability, and uncertainty.
- **Benchmark & Baselines:** Evaluated on experimental DMS benchmarks, structural confidence metrics, and evolutionary constraint tasks against standard zero-shot PLMs.
- **Result:** Conditioning variant predictions on global perturbation regimes produces substantial improvements in substitution effect prediction, with the largest relative gains emerging under unseen-protein, unseen-family, and low-homology evaluation regimes.
- **Open Code / Weights / Data:** Pre-computed residue perturbation atlas and inference code available via RegimeAtlas.
- **Hype vs. Evidence:** **SOLID FOUNDATION CONCEPT.** Demonstrates that global protein fragility/plasticity is an orthogonal macro-property that regularizes local point mutation predictions.
