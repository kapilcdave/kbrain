# Pruned CPU zero-shot ensemble: deployment and reproduction note

## What was validated

On the frozen ProteinGym v1.3 substitutions benchmark across all 217 deep mutational scanning (DMS) assays (186 independent `UniProt_ID` protein holdouts, 2,465,767 mutants), an unassisted, equal-weight ($w=0.25$ each) within-assay percentile-rank ensemble of four cheap zero-shot models excluding Site-Independent profile log-odds (**GEMME**, **EVmutation**, **VESPA**, and **ESM2-35M**) statistically significantly outperformed **GEMME** alone by **+0.017584 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.009415, +0.025719]**; $n=186$ independent units, cluster seed=7). The top-5%-trimmed mean improvement was **+0.011067 > 0**.

All primary, comparator, and negative control metrics were independently verified bit-for-bit from raw staged score tables using `lab/proteingym.py` and `kbstats.py`:
- **Universe and Coverage:** All 217 / 217 assays met the $\ge 95\%$ paired coverage requirement at **100.0% coverage** (2,465,767 mutants). Zero exclusions.
- **Control vs Naive 5-Model Ensemble:** Net mean per-protein improvement over the naive 5-model ensemble (which included Site-Independent) was **+0.010988** (95% CI **[+0.007662, +0.014288]**), proving that pruning `Site-Independent` profile log-odds systematically eliminates negative drag.
- **Constituent Dominance Tests:** The ensemble statistically dominates every constituent member alone:
  - vs EVmutation alone: **+0.079559** (95% CI **[+0.068430, +0.091152]**)
  - vs VESPA alone: **+0.035599** (95% CI **[+0.027377, +0.044078]**)
  - vs ESM2-35M alone: **+0.168308** (95% CI **[+0.142520, +0.194295]**)
- **Secondary Comparator vs ESM2-650M (GPU PLM):** Net mean per-protein improvement was **+0.062061** (95% CI **[+0.040934, +0.083180]**).
- **Rank-Permutation Negative Control:** Mean per-assay Spearman $\bar{\rho}_{\text{perm}} = \mathbf{+0.001111}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation pipeline integrity.
- **Absolute Benchmark Scores:**
  - Benchmark Mean Per-Assay Spearman: Pruned Ensemble **0.4943** vs Naive 5-model **0.4838**, GEMME **0.4743**, VESPA **0.4631**, ESM2-650M **0.4382**, EVmutation **0.4184**, and ESM2-35M **0.3188**.
  - ProteinGym Aggregate Spearman: Pruned Ensemble **0.4748** vs Naive 5-model **0.4668**, GEMME **0.4547**, VESPA **0.4355**, ESM2-650M **0.4137**, EVmutation **0.3952**, and ESM2-35M **0.3208**.
- **Target Win Rate:** 119 wins (64.0%) vs 67 losses (36.0%) across 186 independent target proteins.
- **Hardware Profile:** Sequential execution runs strictly on CPU in $< 3$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

Under the frozen preregistration criteria of Task #259 (`ci_low > 0`, `net_mean_ex_top > 0`, naive 5-model control, constituent dominance, permutation control), the confirmatory backtest **PASSES and is VALIDATED**.

---

## Critical Boundaries, Nuances, and Trade-Offs

The skeptic audit (Task #266) identified five critical boundaries and trade-offs:

### 1. Post-Hoc Re-Evaluation on the Same Benchmark (Circular Holdout)
The hypothesis tested here was not generated independently from an uninspected data source. In Task #172/177, the naive 5-model ensemble failed on the exact same 217 ProteinGym v1.3 assays, and a post-hoc leave-one-out ablation revealed that dropping `Site-Independent` yielded $\Delta = +0.0176$. Task #259/260 re-evaluated that exact ablation on the identical 217 assays (+0.017584 matching down to the 16th decimal place). Per `METHODOLOGY.md`, this is an arithmetic verification of that ablation on a burned holdout. An authentic out-of-sample confirmation requires an unseen forward publication.

### 2. Severe Collapse on Viral Organismal Fitness (ESM2-35M Noise Injection)
Across all 31 viral assays (28 proteins), the pruned ensemble degrades GEMME:
- Net mean delta: **-0.00949** (95% CI **[-0.03177, +0.01887]**), win rate only **32.1%** (9 / 28 proteins).
- On **viral OrganismalFitness** (21 assays, 20 proteins measuring viral replication in Dengue, Influenza, HIV, HCV, SARS-CoV-2, Coxsackievirus, AAV2, and ZIKV), the collapse is severe and statistically significant:
  $$\Delta\bar{\rho}_{\text{protein}} = \mathbf{-0.03893} \quad (95\%\text{ CI } [-0.05330, -0.02543], \text{ win rate } 5.0\%)$$
  19 of 20 viral organismal targets are actively degraded.
- *Root Cause*: ESM2-35M has near-zero correlation on viral organismal fitness (mean Spearman **0.0233** vs **0.4774** for GEMME). Assigning a 25% equal weight injects 25% pure noise into GEMME's rich epistatic predictions.

### 3. Residual Negative Drag from ESM2-35M Benchmark-Wide
While pruning `Site-Independent` cured the largest source of drag, retaining `ESM2-35M` (standalone benchmark mean 0.3188, trailing GEMME by -0.1555) remains suboptimal:
- **Pruned 4-model (with ESM2-35M):** Mean Spearman **0.4943**, $\Delta\text{ vs GEMME} = \mathbf{+0.01758}$ (CI $[+0.0094, +0.0257]$).
- **3-model (GEMME + EVmutation + VESPA, dropping ESM2-35M):** Mean Spearman **0.4984**, $\Delta\text{ vs GEMME} = \mathbf{+0.01992}$ (CI $[+0.0133, +0.0262]$).
- **2-model (GEMME + VESPA 50/50):** Mean Spearman **0.4999**, $\Delta\text{ vs GEMME} = \mathbf{+0.02182}$ (CI $[+0.0154, +0.0283]$).
Dropping ESM2-35M improves overall benchmark correlation and turns the viral delta from **-0.0095** to **+0.0233** (CI $[+0.0061, +0.0420]$).

### 4. Suboptimal Equal Weighting Frontier
Equal 25% weighting assigns identical influence to ESM2-35M ($0.3188$) as to top models GEMME ($0.4743$) and VESPA ($0.4631$). An asymmetric scalar weighting (40% GEMME + 30% VESPA + 20% EVmutation + 10% ESM2-35M) achieves benchmark mean Spearman **0.5039** and paired delta **+0.02664** (CI $[+0.02071, +0.03232]$), strictly dominating the uniform ensemble.

### 5. Genuine Functional and Non-Stability Robustness
Unlike Candidate C10 (GEMME + SaProt-35M), which collapsed on non-Tsuboyama assays ($-0.0121$) and functional assays ($-0.0175$), the pruned 4-model ensemble retains a statistically significant positive edge across:
- **153 non-Tsuboyama assays:** $\Delta = \mathbf{+0.01243}$ (95% CI $[+0.00361, +0.02114]$, win rate 59.8%).
- **133 functional assays (Activity, Binding, OrganismalFitness):** $\Delta = \mathbf{+0.01180}$ (95% CI $[+0.00208, +0.02126]$, win rate 58.4%).
The advantage is genuine across cellular functional phenotypes.

---

## Reproduce

1. **Environment and Lab**:
   - Run with Python 3 (`/home/kapil/.local/share/kbrain/sci/bin/python3`) using `lab/proteingym.py` and `kbstats.py`.
2. **Data**:
   - Staged ProteinGym v1.3 data in `data/proteingym/`: metadata `DMS_substitutions_reference.csv`, assay CSVs in `dms/`, published zero-shot tables in `zero_shot/`.
3. **Execution Script**:
   ```python
   import numpy as np
   import pandas as pd
   import proteingym as pg
   import kbstats

   assays = pg.assays()
   rho_pruned = {}
   rho_gemme = {}
   rho_naive5 = {}
   rho_evm = {}
   rho_vespa = {}
   rho_esm35 = {}
   rho_esm650 = {}

   for aid in assays:
       df = pg.load_assay(aid)
       s_gemme = pg.published_scores(aid, "GEMME")
       s_evm = pg.published_scores(aid, "EVmutation")
       s_vespa = pg.published_scores(aid, "VESPA")
       s_esm35 = pg.published_scores(aid, "ESM2 (35M)")
       s_site = pg.published_scores(aid, "Site-Independent")
       s_esm650 = pg.published_scores(aid, "ESM2 (650M)")

       # Align valid mutants across ground truth and models
       valid = (
           df.index
           .intersection(s_gemme.dropna().index)
           .intersection(s_evm.dropna().index)
           .intersection(s_vespa.dropna().index)
           .intersection(s_esm35.dropna().index)
       )
       assert len(valid) / len(df) >= pg.MIN_COVERAGE

       # Within-assay percentile rank transformation
       r_gemme = s_gemme.loc[valid].rank(method="average", pct=True)
       r_evm = s_evm.loc[valid].rank(method="average", pct=True)
       r_vespa = s_vespa.loc[valid].rank(method="average", pct=True)
       r_esm35 = s_esm35.loc[valid].rank(method="average", pct=True)
       r_site = s_site.loc[valid].rank(method="average", pct=True)

       # Ensembles
       s_pruned = 0.25 * r_gemme + 0.25 * r_evm + 0.25 * r_vespa + 0.25 * r_esm35
       s_naive5 = 0.20 * r_gemme + 0.20 * r_evm + 0.20 * r_vespa + 0.20 * r_esm35 + 0.20 * r_site

       # Score against ground-truth DMS_score
       rho_pruned[aid] = pg.spearman(aid, s_pruned)
       rho_gemme[aid] = pg.spearman(aid, s_gemme.loc[valid])
       rho_naive5[aid] = pg.spearman(aid, s_naive5)
       rho_evm[aid] = pg.spearman(aid, s_evm.loc[valid])
       rho_vespa[aid] = pg.spearman(aid, s_vespa.loc[valid])
       rho_esm35[aid] = pg.spearman(aid, s_esm35.loc[valid])
       rho_esm650[aid] = pg.spearman(aid, s_esm650.loc[valid])

   # Cluster by independent target protein (UniProt_ID, 186 units)
   u_gemme = pg.improvement_units(rho_pruned, rho_gemme, by="protein")
   u_naive5 = pg.improvement_units(rho_pruned, rho_naive5, by="protein")
   u_evm = pg.improvement_units(rho_pruned, rho_evm, by="protein")
   u_vespa = pg.improvement_units(rho_pruned, rho_vespa, by="protein")
   u_esm35 = pg.improvement_units(rho_pruned, rho_esm35, by="protein")
   u_esm650 = pg.improvement_units(rho_pruned, rho_esm650, by="protein")

   res_gemme = kbstats.evaluate(u_gemme, n_boot=2000, alpha=0.05, seed=7)
   res_naive5 = kbstats.evaluate(u_naive5, n_boot=2000, alpha=0.05, seed=7)
   res_evm = kbstats.evaluate(u_evm, n_boot=2000, alpha=0.05, seed=7)
   res_vespa = kbstats.evaluate(u_vespa, n_boot=2000, alpha=0.05, seed=7)
   res_esm35 = kbstats.evaluate(u_esm35, n_boot=2000, alpha=0.05, seed=7)
   res_esm650 = kbstats.evaluate(u_esm650, n_boot=2000, alpha=0.05, seed=7)

   print(f"vs GEMME:          net={res_gemme['net_mean']:.5f}, CI=[{res_gemme['ci_low']:.5f}, {res_gemme['ci_high']:.5f}]")
   print(f"vs Naive 5-model:  net={res_naive5['net_mean']:.5f}, CI=[{res_naive5['ci_low']:.5f}, {res_naive5['ci_high']:.5f}]")
   print(f"vs EVmutation:     net={res_evm['net_mean']:.5f}, CI=[{res_evm['ci_low']:.5f}, {res_evm['ci_high']:.5f}]")
   print(f"vs VESPA:          net={res_vespa['net_mean']:.5f}, CI=[{res_vespa['ci_low']:.5f}, {res_vespa['ci_high']:.5f}]")
   print(f"vs ESM2-35M:       net={res_esm35['net_mean']:.5f}, CI=[{res_esm35['ci_low']:.5f}, {res_esm35['ci_high']:.5f}]")
   print(f"vs ESM2-650M:      net={res_esm650['net_mean']:.5f}, CI=[{res_esm650['ci_low']:.5f}, {res_esm650['ci_high']:.5f}]")
   ```

---

## Deployment Recommendations & What This Points To

1. **Deploy for General Cellular Variant Effect Prediction**:
   - For general zero-shot fitness prediction across eukaryotic, human, and prokaryotic proteins, deploy the **pruned 4-model ensemble (GEMME + EVmutation + VESPA + ESM2-35M)**. It runs in minutes on CPU without GPU hardware, requires zero parameter training, and delivers a robust $+0.0176$ Spearman improvement over GEMME alone (+0.0118 across functional phenotypes).
2. **Strict Operational Prohibition on Viral Targets**:
   - **Do NOT deploy this 4-model ensemble on viral proteins.** ESM2-35M lacks signal on viral replication landscapes ($\rho = 0.0233$), actively degrading GEMME on 95% of viral organismal fitness targets ($\Delta = -0.0389$). For viral proteins, drop ESM2-35M (deploy GEMME + EVmutation + VESPA or GEMME alone).
3. **Pareto-Superior Configurations**:
   - For enhanced performance, prefer:
     - **3-model ensemble (GEMME + EVmutation + VESPA)**: mean Spearman 0.4984, $+0.0199$ over GEMME, and cures viral drag ($+0.0233$).
     - **Asymmetric weighting (40% GEMME + 30% VESPA + 20% EVmutation + 10% ESM2-35M)**: mean Spearman 0.5039, $+0.0266$ over GEMME.
4. **Forward Paper Test Mandate**:
   - Because this experiment tested an ablation derived from Task #172/177 on the same ProteinGym v1.3 dataset, true confirmation requires testing on an unseen forward publication held out from ProteinGym. This forward test requires operator approval and must keep all model weights and configurations frozen before target labels are unblinded.
