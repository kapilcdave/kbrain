# Low-N & Supervised Fitness Prediction

_A comprehensive guide to supervised and few-shot protein fitness prediction, split leakage rigor, and empirical crossover dynamics._

Last updated: 2026-11-01 (Scout shift). Grounded in ProteinGym v1.3 benchmark protocols and kbrain empirical findings.

---

## 1. Executive Summary & Why Low-N Matters

While zero-shot foundation models (ESM-2, GEMME, VenusREM2) predict broad fitness landscapes without experimental labels, real-world protein engineering always operates in **directed evolution cycles**:
- A wet-lab team screens an initial library of **$N \in \{24, 48, 96, 192\}$** variants in a 96-well plate (ELISA, FACS, deep sequencing, or cell survival).
- The goal is **not** to retrain a 650M-parameter neural network from scratch, but to use these scarce measurements to accurately rank uncharacterized mutants for Round 2 acquisition.
- This creates the **low-N supervised track**: predicting the remainder of a target's mutational landscape from minimal labeled data.

### The Central Dilemma
1. **At $N < 20$:** Empirical models overfit or fail to generalize; frozen zero-shot evolutionary priors dominate.
2. **At $N \approx 50–100$:** Direct wet-lab assay feedback begins to outcompete frozen foundation models ([Ding et al., bioRxiv Oct 2026](https://doi.org/10.64898/2026.10.13.758966)).
3. **The Crossover Zone ($N \in [24, 96]$):** The critical operational battleground where **augmented models** (combining zero-shot priors with empirical regression) determine whether protein engineers find improved variants or waste screening rounds.

---

## 2. Paradigms of Low-N Fitness Prediction

```
+-----------------------------------------------------------------------------------------+
|                                LOW-N ARCHITECTURAL TAXONOMY                             |
+-----------------------------------------------------------------------------------------+
| 1. Pure Zero-Shot Prior (N=0)                                                           |
|    y_pred = Prior(x)  [e.g., GEMME, ESM-2, SaProt]                                      |
|    - Fast, zero assay labels required; capped by alignment/model blindspots.            |
+-----------------------------------------------------------------------------------------+
| 2. Pure Empirical Regression                                                            |
|    y_pred = f(OneHot(x))  [e.g., Ridge Regression, Gaussian Processes, CNNs]             |
|    - Learns target assay noise and non-natural selection; fails at unseen positions.    |
+-----------------------------------------------------------------------------------------+
| 3. Zero-Shot Augmented Ridge (Hsu et al., Nat Biotechnol 2022)                           |
|    y_pred = w0 * Prior(x) + w_pos * OneHot(x)                                           |
|    - Blends evolutionary conservatism with local assay calibration; runs in seconds.    |
+-----------------------------------------------------------------------------------------+
| 4. Linear Fitness Subspace / SGES (Ma et al., arXiv Oct 2026)                           |
|    y_pred = w * Proj_LFS(z_mut - z_wt) + Prior(x)                                       |
|    - Recovers a compact 5-10D assay-specific direction from PLM embedding deltas.      |
+-----------------------------------------------------------------------------------------+
| 5. Tabular In-Context Learners (Guan et al., arXiv Jun 2026)                            |
|    y_pred = TabPFN(D_train=(X_train, y_train), x_query=X_test)                          |
|    - Maps frozen PLM embeddings + few labels to predictions in 1 forward pass on CPU.    |
+-----------------------------------------------------------------------------------------+
| 6. Label-Efficient Model Selection / Routing (kbrain Finding 2026)                      |
|    y_pred = Prior_k*(x) where k* = argmax_k Corr(Prior_k(D_train), y_train)             |
|    - Routes between evolutionary (GEMME) and sequence (ESM2) priors using N=24 labels.  |
+-----------------------------------------------------------------------------------------+
```

### Paradigm 1: Pure Empirical Models (One-Hot Features)
- Encodes mutants as sparse binary indicator vectors of length $L \times 20$.
- **Strengths:** Captures linear site-specific fitness preferences directly from experimental data without PLM hallucination.
- **Fatal Weakness:** In single-substitution libraries under position-disjoint splits, any mutation occurring at a position not represented in the training set has a feature vector of all zeros. The model can only predict the global intercept.

### Paradigm 2: Zero-Shot Augmented Regression (Hsu et al. Precedent)
- First introduced systematically by [Hsu et al. (Nature Biotechnology 2022)](https://doi.org/10.1038/s41587-021-01146-5).
- Appends the scalar zero-shot log-odds score $s_{\text{zero}}(x)$ as an explicit feature column alongside sequence one-hot indicators:
  $$y = w_0 s_{\text{zero}}(x) + \sum_{i, a} w_{i, a} \mathbb{I}[x_i = a] + b$$
- Solved via closed-form $L_2$-regularized Ridge regression.
- **Hardware requirement:** Fractions of a second on an 8-core CPU.

### Paradigm 3: Linear Fitness Subspace & Embedding Deltas (Ma et al. 2026)
- [Ma et al. (arXiv:2610.07607)](https://arxiv.org/abs/2610.07607) identified that mutation-induced representation shifts in PLMs ($\Delta z = z_{\text{mut}} - z_{\text{wt}} \in \mathbb{R}^D$) are heavily constrained by protein geometry.
- Rather than running high-dimensional non-linear regression (which overfits when $N \ll D$), Partial Least Squares (PLS) or principal subspace projection isolates a 5–10 dimensional **Linear Fitness Subspace (LFS)**.
- Unlike one-hot features, $\Delta z$ retains continuous structural and chemical semantics across all positions, enabling generalization to positions unseen in the $N$ training points.

### Paradigm 4: Tabular In-Context Learning (TabPFN / TabICL, Guan et al. 2026)
- [Guan et al. (arXiv:2606.31126)](https://arxiv.org/abs/2606.31126) demonstrated that tabular foundation models pretrained on synthetic causal graphs (TabPFN, TabICL) can be repurposed as zero-training, few-shot regressors for protein fitness.
- By pairing frozen PLM embeddings (e.g. ESM Cambrian) as input columns $X$ with measured assay fitness $y$, the tabular foundation model performs in-context Bayesian regression in a single transformer forward pass.
- Eliminates hyperparameter tuning, gradient descent, and cross-validation overfitting on small datasets ($N \le 96$), matching or exceeding task-specific Gaussian processes and supervised regressors on ProteinGym and catalytic activity benchmarks while running instantaneously on CPU.

### Paradigm 5: Label-Efficient Model Routing (kbrain 2026)
- Instead of using $N=24$ measurements to fit model weights, use them to perform **hypothesis selection**: which foundation model's energy landscape best correlates with this specific assay?
- Demonstrated by kbrain's [label-efficient model selection finding](findings/label-efficient-model-selection.md): dynamically switching between GEMME and ESM2-650M yields **+0.01645** held-out Spearman gain over GEMME (95% CI [+0.00776, +0.02608]).

---

## 3. Split Leakage Traps & Rigorous Cross-Validation

The low-N protein literature is rife with reported gains that vanish in actual wet-lab application. ProteinGym v1.3 provides three cross-validation fold structures that reveal distinct generalization mechanisms:

| Split Scheme in ProteinGym | Mechanism | What It Tests | Leakage Risk / Reality Check |
|---|---|---|---|
| `fold_random_5` | Mutants randomly partitioned into 5 folds | Interpolation across variants | **High Leakage:** In single-mutant assays, test variants share positions with training variants. An algorithm can memorize position-level tolerance while claiming sequence understanding. |
| `fold_modulo_5` | Partitioned by position index modulo 5 | Regular spatial spacing | **Moderate Leakage:** Uniformly samples every structural region of the protein; test positions are strictly distinct, but closely flank training positions in 3D space. |
| `fold_contiguous_5` | Sequence divided into 5 continuous blocks | Unseen domain / structural region | **Strict Generalization:** Entire sequence segments and structural motifs are completely held out. Simulates de novo regional engineering (e.g., redesigning an unmutated CDR loop). |

### The kbrain Empirical Lesson: Random vs Contiguous Divergence
In kbrain's [augmented low-N finding](findings/augmented-low-n-regression.md):
- On `fold_random_5` at $N=48$, augmented ridge regression produced a statistically significant gain (+0.00994 Spearman; 95% CI [+0.00451, +0.01570]).
- **The Stratification Attack:** When stratified by mutational complexity, the gain was driven almost entirely by **multiple-mutant assays** (+0.03362), while the single-substitution-only stratum was statistically **null** (+0.00071; 95% CI [-0.00393, +0.00474]).
- On single substitutions, random-split gains often merely reflect position-variance absorption rather than true mutational effect learning. Under `fold_contiguous_5`, one-hot models cannot even evaluate unseen positions.

### Independent Confirmation in the Literature (2026 Preprints)
The kbrain skepticism regarding split leakage has received independent peer confirmation across 2026 preprints:
- **Site-Mean Dominance ([Vieira, Lin, & Wilke, bioRxiv Mar 2026](https://doi.org/10.64898/2026.03.08.710389)):** Systematic benchmarking established that a trivial baseline model predicting only the *site mean fitness* matches or exceeds complex supervised PLMs on many assays under random splits. The apparent supervised "edge" of PLMs drops dramatically under site-stratified splitting, proving that random splits reward memorizing site tolerance rather than learning biochemical substitution rules.
- **Modality-Specific OOD Extrapolation ([Vithayapalert, Piriyajitakonkij, & Grisoni, bioRxiv Oct 2026](https://doi.org/10.64898/2026.10.06.756934)):** On FLIP2 and ProteinGym out-of-distribution splits, structural priors (AlphaFold2 coordinates/3Di tokens) confer generalization across unseen protein backbones, but **co-evolutionary/MSA trunk representations** are strictly necessary to extrapolate fitness predictions to unobserved mutation positions. In the absence of an MSA, PLMs fail to generalize to position-disjoint folds.

---

## 4. The Empirical Crossover Frontier: Foundation Models vs Wet-Lab Data

How many measurements does a protein engineer actually need before foundation models become obsolete?

Recent decision-benchmarking literature ([Ding et al., bioRxiv Oct 2026](https://doi.org/10.64898/2026.10.13.758966)) mapped the exact empirical trade-off across 217 ProteinGym assays:

1. **Top-Candidate Discovery (Hit Rate Optimization):**
   - At $N \le 24$: Foundation model zero-shot rankings provide the highest discovery yield.
   - At $N \approx 48–96$: Active acquisition using empirical Gaussian processes or regularized ridge matches and begins exceeding zero-shot priors.
   - At $N \ge 100$: Wet-lab iterative measurements completely dominate zero-shot models. Zero-shot ranking accuracy explains $<20\%$ of subsequent discovery variance.
2. **Global Landscape Reconstruction (Spearman Rank Correlation):**
   - Global rank correlation across thousands of mutants requires $\sim 500$ experimental measurements to outcompete top zero-shot models (GEMME, VenusREM2).
   - Foundation models preserve a strong global prior over deleterious/neutral regimes, but local fine-tuning near the wild-type requires assay-specific supervision.

---

## 5. Recommended Best Practices for Low-N Research on CPU

1. **Always report held-out Spearman clustered by Protein (UniProt ID), not raw pooled rows.** Single proteins with large assays (e.g. 100k mutants) easily bias unclustered metrics.
2. **Always report results on both `fold_random_5` and `fold_contiguous_5`.** If a method's advantage drops to zero on contiguous splits, it is memorizing positions, not learning substitutions.
3. **Always compare against frozen zero-shot priors alone as the baseline.** Any supervised method claiming low-N utility must demonstrate a 95% CI strictly above zero over the unassisted zero-shot score on the exact same test mutants.
4. **Use Closed-Form Linear Models on CPU:** Ridge regression and PLS regression over one-hot indicators, zero-shot priors, and small PLM embeddings require zero GPU compute, cost seconds per assay, and match or outperform heavily parameterized neural networks in the $N \le 96$ regime.

---

## 6. Key References

- **Hsu et al., Nat Biotechnol 2022:** *Learning protein fitness landscapes with mutation-augmented neural networks.* [DOI:10.1038/s41587-021-01146-5](https://doi.org/10.1038/s41587-021-01146-5)
- **Ding et al., bioRxiv 2026:** *Decision benchmarking reveals when protein foundation models add experimental value.* [DOI:10.64898/2026.10.13.758966](https://doi.org/10.64898/2026.10.13.758966)
- **Ma et al., arXiv 2026:** *Linear Fitness Subspace in Protein Language Models Enables Sample-Efficient Directed Evolution.* [arXiv:2610.07607](https://arxiv.org/abs/2610.07607)
- **Notin et al., NeurIPS 2023:** *ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design.* [arXiv:2306.12204](https://arxiv.org/abs/2306.12204)
- **kbrain Lab Findings:** [Augmented low-N regression](findings/augmented-low-n-regression.md) & [Label-efficient model selection](findings/label-efficient-model-selection.md).
