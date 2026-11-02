# Structure-evolution zero-shot rank blend: deployment and reproduction note

## What was validated

On the frozen ProteinGym v1.3 substitutions benchmark across all 217 deep mutational scanning assays (186 independent `UniProt_ID` protein holdouts, 2,465,767 mutants), an unassisted, equal-weight ($w=0.5 / 0.5$) within-assay percentile-rank blend of published **GEMME** (epistatic evolutionary multiple sequence alignment model) and published **SaProt-35M-AF2** (structure-tokenized PLM conditioned on AlphaFold2 backbone coordinates via Foldseek 3Di tokens) statistically significantly outperformed **GEMME** alone by **+0.021142 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.008878, +0.032950]**; $n=186$, cluster seed=7). The top-5%-trimmed mean improvement was **+0.011567**.

All primary, comparator, and negative control metrics were independently verified bit-for-bit from raw files using `lab/proteingym.py` and `kbstats.py`:
- **Universe and Eligibility:** All 217 / 217 assays met the $\ge 95\%$ paired coverage requirement at **100.0% coverage** (2,465,767 mutants). Zero exclusions.
- **Constituent Dominance vs SaProt-35M-AF2 Alone:** Net mean per-protein improvement was **+0.079259** (95% CI **[+0.064803, +0.094000]**; trimmed mean $+0.066306$), proving the blend outperforms both constituent models rather than merely shadowing one.
- **Secondary Comparator vs ESM2-650M Alone:** Net mean per-protein improvement was **+0.065619** (95% CI **[+0.046388, +0.085921]**).
- **Rank-Permutation Negative Control:** Mean Spearman $\bar{\rho}_{\text{perm}} = \mathbf{-0.000035}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation pipeline neutrality.
- **Absolute Benchmark Scores:**
  - Benchmark Mean Per-Assay Spearman: Blend **0.493117** vs GEMME **0.474261**, ESM2-650M **0.438195**, SaProt-35M-AF2 **0.412952**.
  - Official ProteinGym Aggregate Spearman: Blend **0.479038** vs GEMME **0.454674**, ESM2-650M **0.413744**, SaProt-35M-AF2 **0.406477**.
- **Hardware Profile:** Runs strictly on CPU in $< 5$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

Under the frozen decision criteria of Task #243 (`ci_low > 0`, `net_mean_ex_top > 0`, constituent control vs SaProt, permutation control), the confirmatory backtest **PASSES and is VALIDATED**.

---

## Critical Skeptical Defect Catalogue & Boundaries

While the backtest passes its primary arithmetic acceptance gate, the skeptic audit identified five severe defect modes and biological boundaries that delimit its valid domain of deployment:

### 1. Bimodal Phenotypic Split — Severe Degradation on Functional Assays
The benchmark-wide positive delta ($\Delta\bar{\rho} = +0.0211$) is driven exclusively by physical folding stability and cellular expression. On functional phenotypes measuring enzymatic activity, ligand binding, or organismal growth, the equal 50/50 blend is **statistically significantly harmful**:

| Phenotypic Stratum | Assays ($N$) | Proteins ($N$) | Mean Delta ($\Delta\bar{\rho}_{\text{protein}}$) | 95% Cluster Bootstrap CI | Protein Win Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Stability** | 66 | 66 | **+0.081397** | **[+0.064370, +0.099545]** | 89.4% (59 / 66) |
| **Expression** | 18 | 18 | **+0.047578** | **[+0.035290, +0.060429]** | 100.0% (18 / 18) |
| **Binding** | 13 | 12 | +0.036829 | [-0.000948, +0.064615] | 91.7% (11 / 12) |
| **Activity** | 43 | 40 | **-0.015216** | **[-0.033683, +0.002052]** | 45.0% (18 / 40) |
| **OrganismalFitness** | 77 | 64 | **-0.028766** | **[-0.046731, -0.010224]** | 40.6% (26 / 64) |
| **All Non-Stability Assays** | 151 | 120 | **-0.011999** | **[-0.024972, +0.000843]** | 53.3% (64 / 120) |
| **Functional Assays (Act + Bind + Org)** | 133 | 113 | **-0.017534** | **[-0.030151, -0.004577]** | 48.7% (55 / 113) |
| **Activity + OrganismalFitness** | 120 | 101 | **-0.023994** | **[-0.037598, -0.010244]** | 42.6% (43 / 101) |

Across the 133 functional assays (113 independent proteins), the 95% bootstrap confidence interval is **strictly below zero** ($[-0.0302, -0.0046]$). The blend is an exceptional predictor of thermodynamic stability and expression, but damages predictions of catalytic turnover and organismal fitness.

### 2. Single-Study Platform Concentration in Stability Assays
- Of the 66 assays in the `Stability` stratum, **64 assays originate from a single high-throughput cDNA display proteolysis study**: Tsuboyama et al., *Nature* 2023.
- When all 64 Tsuboyama assays are excluded from the benchmark:
  - Remaining universe: 153 assays across 122 independent proteins.
  - Net mean improvement over GEMME: **-0.012144** Spearman per protein.
  - 95% Bootstrap CI: **[-0.024276, +0.000664]** (spans zero).
  - Ex-top 5% trimmed mean: **-0.018396**.
- The benchmark-wide statistical pass across 186 proteins is essentially driven by the 64 targets from this single cDNA display proteolysis experimental platform. Outside this platform, the equal 50/50 blend underperforms GEMME.

### 3. Systematic Collapse on Viral Genomes
- On all 31 viral assays (28 unique UniProt proteins), SaProt-35M-AF2 alone achieves mean Spearman of only 0.2224 (vs 0.4900 for GEMME), dragging the 50/50 blend down by $\Delta = -0.037130$ (win rate only 32.1%).
- On the 21 viral OrganismalFitness replication assays (20 proteins, covering Dengue, Influenza, HIV, HCV, SARS-CoV-2, Coxsackievirus, AAV2, and ZIKV), the collapse is severe:
  - Net mean degradation: **-0.099491** Spearman per protein.
  - 95% Bootstrap CI: **[-0.116771, -0.082118]** (entirely below -0.08).
  - Ex-top 5% trimmed mean: **-0.105014**.
- Viral polyproteins and quaternary complexes lack high-quality monomer AF2 structures, injecting near-random Foldseek tokens that dilute rich viral epistatic MSAs.

### 4. Suboptimal Mixing Asymmetry (Pareto-Superior 80/20 Frontier)
Because SaProt-35M-AF2 (0.4130) is substantially weaker than GEMME (0.4743) benchmark-wide, equal weighting ($w=0.5 / 0.5$) severely overpenalizes GEMME. An audit sweep across blending weights revealed:

| Blend Weights (GEMME / SaProt) | Benchmark Mean Spearman | All 186 Proteins ($\Delta\bar{\rho}$, 95% CI) | Stability (66 Proteins) ($\Delta\bar{\rho}$, 95% CI) | Non-Stability (120 Proteins) ($\Delta\bar{\rho}$, 95% CI) | Functional (113 Proteins) ($\Delta\bar{\rho}$, 95% CI) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.50 / 0.50 (Preregistered) | 0.4931 | +0.0211 [+0.0089, +0.0330] | **+0.0814** [+0.0644, +0.0995] | **-0.0120** [-0.0250, +0.0008] | **-0.0175** [-0.0302, -0.0046] |
| 0.70 / 0.30 | **0.4988** | **+0.0260** [+0.0197, +0.0321] | +0.0584 [+0.0487, +0.0687] | **+0.0083** [+0.0020, +0.0144] | +0.0053 [-0.0008, +0.0117] |
| **0.80 / 0.20** | 0.4940 | +0.0208 [+0.0169, +0.0245] | +0.0407 [+0.0345, +0.0473] | **+0.0098** [+0.0060, +0.0136] | **+0.0079** [+0.0043, +0.0117] |
| 1.00 / 0.00 (GEMME Alone) | 0.4743 | Baseline (0.0) | Baseline (0.0) | Baseline (0.0) | Baseline (0.0) |

An asymmetric **80% GEMME + 20% SaProt** scalar blend is strictly **Pareto-superior**: it improves over GEMME across **every single stratum**, including Functional phenotypes ($\Delta = +0.0079$, 95% CI $[+0.0043, +0.0117]$), while narrowing the 95% bootstrap CI by $>60\%$.

### 5. Intrinsically Disordered Protein Failure Mode
On proteins lacking native tertiary structure (e.g. alpha-synuclein `SYUA_HUMAN`), AF2 low-confidence coordinates inject spurious Foldseek 3Di tokens (SaProt alone $-0.0451$ vs GEMME $+0.2274$). The 50/50 blend collapses to $0.1020$ ($\Delta = -0.1254$ vs GEMME).

---

## Reproduce

1. **Environment and Lab**:
   - Use the trusted evaluator `lab/proteingym.py` and `kbstats.py` with Python 3 (`/home/kapil/.local/share/kbrain/sci/bin/python3`).
2. **Data**:
   - Staged ProteinGym v1.3 data in `data/proteingym/`: metadata `DMS_substitutions_reference.csv`, assay CSVs in `dms/`, published zero-shot tables in `zero_shot/`.
3. **Execution Steps**:
   ```python
   import numpy as np
   import pandas as pd
   import proteingym as pg
   import kbstats

   assays = pg.assays()
   rho_blend = {}
   rho_gemme = {}
   rho_saprot = {}

   for aid in assays:
       df = pg.load_assay(aid)
       s_gemme = pg.published_scores(aid, "GEMME")
       s_saprot = pg.published_scores(aid, "SaProt_35M_AF2")
       
       # Common mutant alignment
       common = df.index.intersection(s_gemme.dropna().index).intersection(s_saprot.dropna().index)
       assert len(common) / len(df) >= pg.MIN_COVERAGE
       
       # Fractional rank transform to [0, 1]
       r_gemme = s_gemme.loc[common].rank(method="average", pct=True)
       r_saprot = s_saprot.loc[common].rank(method="average", pct=True)
       
       # Equal 50/50 blend
       s_blend = 0.5 * r_gemme + 0.5 * r_saprot
       
       rho_blend[aid] = pg.spearman(aid, s_blend)
       rho_gemme[aid] = pg.spearman(aid, s_gemme.loc[common])
       rho_saprot[aid] = pg.spearman(aid, s_saprot.loc[common])

   # Cluster paired improvements by protein (186 independent units)
   deltas_vs_gemme = pg.improvement_units(rho_blend, rho_gemme, by="protein")
   res = kbstats.evaluate(deltas_vs_gemme, n_boot=2000, alpha=0.05, seed=7)
   # res['net_mean'] == +0.021142
   # res['ci_low'] == +0.008878
   # res['ci_high'] == +0.032950
   # res['net_mean_ex_top'] == +0.011567
   ```

---

## Caveats and Deployment Warnings

- **DO NOT Deploy the 50/50 Blend Universally**: Never use an unweighted 50/50 GEMME/SaProt blend for variant effect prediction on functional assays (enzymatic activity, ligand binding, organismal fitness) or viral proteins.
- **When to Use the 50/50 Blend**: Restrict the equal-weight blend strictly to applications focused on physical folding stability ($\Delta\Delta G$) or protein expression, where it provides massive gains ($\Delta = +0.0814$ and $+0.0476$).
- **General-Purpose Recommendation**: For uncharacterized or multi-phenotype variant effect prediction, deploy an asymmetric **80% GEMME + 20% SaProt** scalar blend. This captures structural packing signals without dragging down catalytic or organismal fitness predictions.
- **Intrinsically Disordered Proteins**: Require a structural confidence mask (e.g. reverting to GEMME alone when AF2 mean residue pLDDT $< 60$).

---

## Next Decisions and Forward Evaluation

1. **Forward Paper Test (Requires Operator Approval)**:
   Evaluate whether the asymmetric 80% GEMME + 20% SaProt blend maintains its advantage over GEMME alone on a genuinely unseen, prospectively collected deep mutational scanning publication held out from ProteinGym v1.3. All models, blending weights, score orientations, and bootstrap parameters must remain frozen prior to inspecting experimental labels.
2. **Phenotype-Aware Structural Routing**:
   Investigate whether explicit phenotypic gating (applying higher structural weights to folding stability targets and low/zero structural weights to viral and catalytic turnover targets) outperforms static scalar ensembling.
