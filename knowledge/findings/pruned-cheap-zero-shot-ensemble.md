# Pruned CPU zero-shot ensemble outperforms GEMME benchmark-wide, but collapses on viral fitness

_2026-11-01. Validated experiment (Tasks #259, #260, #266, and #269 / #278); deployed in dry mode by Task #275._

## Claim

On the frozen ProteinGym v1.3 substitution benchmark across all 217 assays (186 independent UniProt target proteins, 2,465,767 mutants), an unassisted, equal-weight ($w=0.25$ each) within-assay percentile-rank ensemble of four cheap zero-shot models excluding Site-Independent profile log-odds (**GEMME**, **EVmutation**, **VESPA**, and **ESM2-35M**) statistically significantly outperforms **GEMME** alone and every constituent model alone. Pruning `Site-Independent` profile log-odds systematically eliminates the negative drag observed in naive 5-model ensembling. Furthermore, unlike structure-token blends, the pruned ensemble retains genuine positive improvements across functional phenotypes and non-stability assays.

However, the skeptic audit conclusively demonstrated two major operational boundaries:
1. **Severe Viral Organismal Fitness Collapse:** ESM2-35M exhibits near-zero predictive correlation on viral replication ($\bar{\rho} = 0.0233$), injecting 25% pure noise into GEMME's rich epistatic predictions and degrading 95% of viral organismal fitness targets ($\Delta = -0.0389$). Do not deploy this 4-model ensemble on viral targets; drop ESM2-35M on viral genomes.
2. **Burned Holdout Backtest:** The 4-model combination was identified post-hoc from Task #172/177 on the exact same ProteinGym v1.3 benchmark. Evaluating on ProteinGym confirms the arithmetic (+0.017584) but remains a retrospective verification on burned data; authentic out-of-sample confirmation requires an unseen forward publication.

## Measured result

All 217 assays and 186 independent UniProt protein holdouts passed the preregistered $\ge 95\%$ coverage check at 100.0% paired coverage (2,465,767 mutants). Zero assays were excluded.

Benchmark-wide metrics:
- **Mean Per-Assay Spearman:** Pruned Ensemble **0.4943** vs Naive 5-model **0.4838**, GEMME **0.4743**, VESPA **0.4631**, ESM2-650M **0.4382**, EVmutation **0.4184**, and ESM2-35M **0.3188**.
- **Official ProteinGym Aggregate Spearman:** Pruned Ensemble **0.4748** vs Naive 5-model **0.4668**, GEMME **0.4547**, VESPA **0.4355**, ESM2-650M **0.4137**, EVmutation **0.3952**, and ESM2-35M **0.3208**.
- **Primary endpoint vs GEMME alone:** Net mean per-protein improvement was **+0.017584 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.009415, +0.025719]**; top-5%-trimmed mean **+0.011067**; $n=186$ independent proteins; seed 7). Both `ci_low > 0` and `net_mean_ex_top > 0` passed.
- **Control vs Naive 5-Model Ensemble:** Net mean per-protein improvement over the naive 5-model ensemble (which included Site-Independent) was **+0.010988** (95% CI **[+0.007662, +0.014288]**), proving that pruning `Site-Independent` profile log-odds systematically eliminates negative drag.
- **Constituent Dominance Tests:** The ensemble statistically dominates every constituent member alone:
  - vs EVmutation alone: **+0.079559** (95% CI **[+0.068430, +0.091152]**)
  - vs VESPA alone: **+0.035599** (95% CI **[+0.027377, +0.044078]**)
  - vs ESM2-35M alone: **+0.168308** (95% CI **[+0.142520, +0.194295]**)
- **Secondary comparator vs ESM2-650M alone:** Net mean per-protein improvement was **+0.062061** (95% CI **[+0.040934, +0.083180]**).
- **Rank-Permutation Negative Control:** Mean Spearman $\bar{\rho}_{\text{perm}} = \mathbf{+0.001111}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation pipeline neutrality.
- **Target Win Rate:** 119 wins (64.0%) vs 67 losses (36.0%) across 186 independent target proteins.
- **Hardware Profile:** Runs strictly on CPU in $< 3$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

The skeptic audit identified five critical boundaries and trade-offs:

1. **Severe Collapse on Viral Organismal Fitness (ESM2-35M Noise Injection):**
   Across all 31 viral assays (28 proteins), the pruned ensemble degrades GEMME:
   - Net mean delta: **-0.00949** (95% CI **[-0.03177, +0.01887]**), win rate only **32.1%** (9 / 28 proteins).
   - On **viral OrganismalFitness** (21 assays, 20 proteins measuring viral replication in Dengue, Influenza, HIV, HCV, SARS-CoV-2, Coxsackievirus, AAV2, and ZIKV), the collapse is severe and statistically significant:
     $$\Delta\bar{\rho}_{\text{protein}} = \mathbf{-0.03893} \quad (95\%\text{ CI } [-0.05330, -0.02543], \text{ win rate } 5.0\%)$$
     19 of 20 viral organismal targets are actively degraded.
   - *Mechanistic Root Cause*: ESM2-35M has near-zero correlation on viral organismal fitness (mean Spearman **0.0233** vs **0.4774** for GEMME). Assigning a 25% equal weight injects 25% pure noise into GEMME's rich epistatic predictions.

2. **Residual Negative Drag from ESM2-35M Benchmark-Wide:**
   While pruning `Site-Independent` eliminated the largest source of drag, retaining `ESM2-35M` (standalone benchmark mean 0.3188, trailing GEMME by -0.1555) remains suboptimal:
   - **Pruned 4-model (with ESM2-35M):** Mean Spearman **0.4943**, $\Delta\text{ vs GEMME} = \mathbf{+0.01758}$ (CI $[+0.0094, +0.0257]$).
   - **3-model (GEMME + EVmutation + VESPA, dropping ESM2-35M):** Mean Spearman **0.4984**, $\Delta\text{ vs GEMME} = \mathbf{+0.01992}$ (CI $[+0.0133, +0.0262]$).
   - **2-model (GEMME + VESPA 50/50):** Mean Spearman **0.4999**, $\Delta\text{ vs GEMME} = \mathbf{+0.02182}$ (CI $[+0.0154, +0.0283]$).
   Dropping ESM2-35M improves overall benchmark correlation and turns the viral delta from **-0.0095** to **+0.0233** (CI $[+0.0061, +0.0420]$).

3. **Suboptimal Equal Weighting Frontier:**
   Equal 25% weighting assigns identical influence to ESM2-35M ($0.3188$) as to top models GEMME ($0.4743$) and VESPA ($0.4631$). An asymmetric scalar weighting (40% GEMME + 30% VESPA + 20% EVmutation + 10% ESM2-35M) achieves benchmark mean Spearman **0.5039** and paired delta **+0.02664** (CI $[+0.02071, +0.03232]$), strictly dominating the uniform ensemble.

4. **Genuine Functional and Non-Stability Robustness:**
   Unlike Candidate C10 (GEMME + SaProt-35M), which collapsed on non-Tsuboyama assays ($-0.0121$) and functional assays ($-0.0175$), the pruned 4-model ensemble retains a statistically significant positive edge across:
   - **153 non-Tsuboyama assays:** $\Delta = \mathbf{+0.01243}$ (95% CI $[+0.00361, +0.02114]$, win rate 59.8%).
   - **133 functional assays (Activity, Binding, OrganismalFitness):** $\Delta = \mathbf{+0.01180}$ (95% CI $[+0.00208, +0.02126]$, win rate 58.4%).
   The advantage is genuine across cellular functional phenotypes.

5. **Post-Hoc Re-Evaluation on the Same Benchmark (Circular Holdout):**
   The hypothesis tested here was derived from post-hoc leave-one-out ablations in Task #172/177 on the exact same 217 ProteinGym v1.3 assays (+0.017584 matching down to the 16th decimal place). Per `METHODOLOGY.md`, this is an arithmetic verification of that ablation on a burned holdout. An authentic out-of-sample confirmation requires an unseen forward publication.

## Inference and conclusion

Combining multiple complementary zero-shot representations—epistatic evolutionary couplings (GEMME, EVmutation), sequence-conservation ensembles (VESPA), and small masked language models (ESM2-35M)—provides meaningful variance reduction and outperforms individual constituents on general cellular targets. Systematically removing single-site marginal profile log-odds (`Site-Independent`) is essential, as unregularized frequency profiles act as severe negative drag.

However, model ensembling without domain conditioning introduces serious failure modes. Small protein language models (ESM2-35M) fail to capture viral replication landscapes, turning an otherwise strong ensemble into a destructive noise injector on viral organismal fitness.

Keep the result in dry mode.
- **Deploy for General Cellular Variant Effect Prediction:** For general zero-shot fitness prediction across eukaryotic, human, and prokaryotic proteins, deploy the **pruned 4-model ensemble (GEMME + EVmutation + VESPA + ESM2-35M)**. It runs in minutes on CPU without GPU hardware, requires zero parameter training, and delivers a robust $+0.0176$ Spearman improvement over GEMME alone (+0.0118 across functional phenotypes).
- **Strict Operational Prohibition on Viral Targets:** **Do NOT deploy this 4-model ensemble on viral proteins.** ESM2-35M lacks signal on viral replication landscapes ($\rho = 0.0233$), actively degrading GEMME on 95% of viral organismal fitness targets ($\Delta = -0.0389$). For viral proteins, drop ESM2-35M (deploy GEMME + EVmutation + VESPA or GEMME alone).
- **Pareto-Superior Configurations:** For enhanced performance, prefer:
  - **3-model ensemble (GEMME + EVmutation + VESPA):** mean Spearman 0.4984, $+0.0199$ over GEMME, and cures viral drag ($+0.0233$).
  - **Asymmetric weighting (40% GEMME + 30% VESPA + 20% EVmutation + 10% ESM2-35M):** mean Spearman 0.5039, $+0.0266$ over GEMME.
- **Forward Paper Test Mandate:** Prospective evaluation on an unseen forward DMS publication held out from ProteinGym v1.3 requires operator approval, with all model weights, score orientations, and taxon routing rules frozen before inspecting labels.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, published zero-shot scores, and reference metadata; 217 assays representing 186 independent UniProt target proteins. Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). ProteinGym benchmark reference: Notin et al.,
  [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** GEMME is described by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); EVmutation by Marks et al., 2011 / Hopf et al., 2017,
  [DOI:10.1038/nbt.3769](https://doi.org/10.1038/nbt.3769); VESPA by Marquet et al., 2021,
  [DOI:10.1093/bioinformatics/btab547](https://doi.org/10.1093/bioinformatics/btab547); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574).
- **Procedure:** Load published zero-shot scores for GEMME, EVmutation, VESPA, ESM2-35M, and Site-Independent across all 217 assays via `lab/proteingym.py`. Verify $\ge 95\%$ common finite mutant coverage. Convert mutant scores within each assay to fractional percentile ranks in $[0, 1]$ using average tie-breaking. Blend ranks equally: $s_{\text{pruned}} = 0.25 \cdot r_{\text{GEMME}} + 0.25 \cdot r_{\text{EVmutation}} + 0.25 \cdot r_{\text{VESPA}} + 0.25 \cdot r_{\text{ESM2-35M}}$. Score with `pg.spearman_by_assay`, cluster paired improvements by `UniProt_ID` with `pg.improvement_units(..., by="protein")`, and evaluate 2,000 bootstrap resamples with alpha 0.05 and seed 7 using `kbstats.evaluate`.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction steps, stratified breakdowns, and deployment guidelines in the [deployment brief](../../fields/proteins/deploy-pruned-cheap-zero-shot-ensemble.md). Task #259 holds the frozen preregistration, Task #260 is the confirmatory run, Task #266 is the skeptic audit, Task #269 / #278 records the field verdict, and Task #275 is the deployment.

## Caveats

- Published frozen benchmark scores were compared; no model was newly trained or parameterized.
- The 4-model combination was identified post-hoc from Task #172/177 on the exact same ProteinGym v1.3 benchmark; re-scoring confirms the arithmetic (+0.0176) but is a burned-holdout backtest.
- Equal 25% weighting causes severe degradation on viral organismal fitness targets ($-0.0389$ vs GEMME; win rate 5.0%), where ESM2-35M acts as uncorrelated noise.
- Retaining ESM2-35M is suboptimal benchmark-wide; dropping ESM2-35M (GEMME + EVmutation + VESPA) or using asymmetric weighting (40/30/20/10) achieves superior Spearman correlation and cures viral collapse.
- Retrospective benchmark results on ProteinGym v1.3 must not be deployed prospectively without an operator-approved forward test on unseen targets.
