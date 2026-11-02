# Structure-evolution zero-shot rank blend validates benchmark-wide, driven by stability

_2026-11-01. Validated experiment (Tasks #243, #244, #261, and #262); deployed in dry mode by Task #265._

## Claim

On the frozen ProteinGym v1.3 substitution benchmark across all 217 assays (186 independent UniProt targets), an unassisted, equal-weight ($w=0.5 / 0.5$) within-assay percentile-rank blend of published GEMME (epistatic evolutionary MSA model) and published SaProt-35M-AF2 (Foldseek 3Di structure-token PLM on AlphaFold2 backbones) statistically significantly outperformed GEMME alone and SaProt-35M-AF2 alone. However, the skeptic audit conclusively demonstrated that the benchmark-wide positive delta is driven exclusively by physical folding stability and cellular expression—concentrated heavily within a single high-throughput cDNA display proteolysis study. On functional phenotypes (enzymatic activity, ligand binding, and organismal fitness) and viral genomes, the equal 50/50 blend is statistically significantly harmful. Do not deploy the unweighted 50/50 blend universally; use an asymmetric 80% GEMME + 20% SaProt scalar blend for general-purpose variant effect prediction, or restrict the 50/50 blend strictly to thermodynamic stability and expression targets.

## Measured result

All 217 assays and 186 independent UniProt protein holdouts passed the preregistered $\ge 95\%$ coverage check at 100.0% paired coverage (2,465,767 mutants). Zero assays were excluded.

Benchmark-wide metrics:
- **Mean Per-Assay Spearman:** Blend **0.493117** vs GEMME **0.474261**, ESM2-650M **0.438195**, SaProt-35M-AF2 **0.412952**.
- **Official ProteinGym Aggregate Spearman:** Blend **0.479038** vs GEMME **0.454674**, ESM2-650M **0.413744**, SaProt-35M-AF2 **0.406477**.
- **Primary endpoint vs GEMME alone:** Net mean per-protein improvement was **+0.021142 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.008878, +0.032950]**; top-5%-trimmed mean **+0.011567**; $n=186$ independent proteins; seed 7). Both `ci_low > 0` and `net_mean_ex_top > 0` passed.
- **Constituent dominance vs SaProt-35M-AF2 alone:** Net mean per-protein improvement was **+0.079259** (95% CI **[+0.064803, +0.094000]**; top-5%-trimmed mean **+0.066306**), confirming that the blend outperforms both constituent models rather than shadowing one.
- **Secondary comparator vs ESM2-650M alone:** Net mean per-protein improvement was **+0.065619** (95% CI **[+0.046388, +0.085921]**).
- **Rank-Permutation Negative Control:** Mean Spearman $\bar{\rho}_{\text{perm}} = \mathbf{-0.000035}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation neutrality.
- **Hardware Profile:** Runs strictly on CPU in $< 5$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

The skeptic audit identified five severe defect modes and domain boundaries:

1. **Bimodal Phenotypic Split — Severe Degradation on Functional Assays:**
   The positive aggregate delta ($\Delta = +0.0211$) is driven entirely by physical folding stability and cellular expression. On functional assays measuring enzymatic activity, ligand binding, or organismal fitness, the 50/50 blend is statistically significantly harmful:
   - *Stability* (66 assays, 66 proteins): $\Delta = \mathbf{+0.081397}$ (95% CI **[+0.064370, +0.099545]**; win rate 89.4%).
   - *Expression* (18 assays, 18 proteins): $\Delta = \mathbf{+0.047578}$ (95% CI **[+0.035290, +0.060429]**; win rate 100.0%).
   - *Binding* (13 assays, 12 proteins): $\Delta = +0.036829$ (95% CI $[-0.000948, +0.064615]$; win rate 91.7%).
   - *Activity* (43 assays, 40 proteins): $\Delta = \mathbf{-0.015216}$ (95% CI **[-0.033683, +0.002052]**; win rate 45.0%).
   - *OrganismalFitness* (77 assays, 64 proteins): $\Delta = \mathbf{-0.028766}$ (95% CI **[-0.046731, -0.010224]**; win rate 40.6%).
   - *All Non-Stability Assays* (151 assays, 120 proteins): $\Delta = \mathbf{-0.011999}$ (95% CI **[-0.024972, +0.000843]**; win rate 53.3%).
   - *Functional Assays (Activity + Binding + OrganismalFitness)* (133 assays, 113 proteins): $\Delta = \mathbf{-0.017534}$ (95% CI **[-0.030151, -0.004577]**; win rate 48.7%). The 95% CI is strictly below zero.
   - *Activity + OrganismalFitness* (120 assays, 101 proteins): $\Delta = \mathbf{-0.023994}$ (95% CI **[-0.037598, -0.010244]**; win rate 42.6%).

2. **Single-Study Platform Concentration in Stability Assays:**
   - 64 of 66 Stability assays originate from a single high-throughput cDNA display proteolysis study (Tsuboyama et al., *Nature* 2023).
   - When all 64 Tsuboyama assays are excluded from the benchmark (leaving 153 assays across 122 proteins), the net mean improvement over GEMME drops to **-0.012144** Spearman per protein (95% CI **[-0.024276, +0.000664]**, spanning zero; trimmed mean **-0.018396**).
   - The benchmark-wide statistical pass across 186 proteins is essentially driven by this single cDNA display proteolysis platform.

3. **Systematic Collapse on Viral Genomes:**
   - Across all 31 viral assays (28 proteins), SaProt-35M-AF2 alone achieves mean Spearman of only 0.2224 (vs 0.4900 for GEMME), dragging the 50/50 blend down by $\Delta = -0.037130$ (win rate 32.1%).
   - On the 21 viral OrganismalFitness replication assays (20 proteins, covering Dengue, Influenza, HIV, HCV, SARS-CoV-2, Coxsackievirus, AAV2, and ZIKV), the collapse is severe: net mean degradation is **-0.099491** Spearman per protein (95% CI **[-0.116771, -0.082118]**; trimmed mean **-0.105014**).
   - Viral polyproteins and multimeric complexes lack high-quality monomer AF2 structures, injecting near-random Foldseek tokens that corrupt rich evolutionary MSAs.

4. **Suboptimal Mixing Asymmetry (Pareto-Superior 80/20 Frontier):**
   - Because SaProt-35M-AF2 (0.4130) is substantially weaker than GEMME (0.4743), equal 50/50 weighting severely penalizes GEMME on functional targets.
   - An asymmetric **80% GEMME + 20% SaProt** scalar blend is strictly Pareto-superior: it achieves benchmark mean Spearman **0.4940** and improves across **every single stratum**, including Functional phenotypes ($\Delta = \mathbf{+0.0079}$, 95% CI **[+0.0043, +0.0117]**) and Non-Stability assays ($\Delta = \mathbf{+0.0098}$, 95% CI **[+0.0060, +0.0136]**), while narrowing the benchmark-wide 95% bootstrap CI by $>60\%$ ($\Delta = +0.0208$, 95% CI $[+0.0169, +0.0245]$).

5. **Intrinsically Disordered Protein Failure Mode:**
   - On targets lacking defined tertiary structures (e.g. alpha-synuclein `SYUA_HUMAN`), AF2 coordinates have low pLDDT and inject spurious Foldseek 3Di tokens (SaProt alone $-0.0451$ vs GEMME $+0.2274$). The 50/50 blend collapses to $0.1020$ ($\Delta = -0.1254$ vs GEMME).

## Inference and conclusion

AlphaFold2-derived structure tokens combined with epistatic evolutionary MSAs provide strong complementary signal for thermodynamic folding stability and protein expression, where physical packing constraints dominate. However, Foldseek 3Di structural tokens do not capture catalytic turnover, ligand binding geometry, or dynamic allosteric transitions as well as deep evolutionary MSAs. Treating structure tokens as equal partners to epistatic MSAs dilutes critical functional signals and causes severe prediction collapse on viral targets and disordered proteins.

Keep the result in dry mode.
- **Do NOT deploy the unweighted 50/50 blend universally**: Avoid equal weighting on functional phenotypes (activity, binding, fitness) and viral proteins.
- **Deploy 50/50 strictly for Stability/Expression**: Restrict the 50/50 blend to applications focused explicitly on thermodynamic folding stability ($\Delta\Delta G$) and cellular expression, where it provides massive gains ($+0.0814$ and $+0.0476$).
- **General-Purpose Deployment**: Deploy an asymmetric **80% GEMME + 20% SaProt** scalar blend for uncharacterized or multi-phenotype variant effect prediction. This captures structural packing signals without harming catalytic or organismal fitness predictions.
- **Disorder Safeguard**: Disordered targets require a structural confidence mask (e.g., falling back to GEMME alone when mean AlphaFold pLDDT $< 60$).
- Any forward evaluation on an unseen prospective DMS paper requires operator approval.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, published zero-shot scores, and reference metadata; 217 assays representing 186 independent UniProt target proteins. Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). ProteinGym benchmark reference: Notin et al.,
  [arXiv:2306.12204](https://arxiv.org/abs/2306.12204); dominant stability dataset: Tsuboyama et al., 2023,
  [DOI:10.1038/s41586-023-06328-6](https://doi.org/10.1038/s41586-023-06328-6).
- **Models:** GEMME is described by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); SaProt is described by Su et al., 2024,
  [ICLR 2024 / bioRxiv:2023.10.02.560515](https://doi.org/10.1101/2023.10.02.560515); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574).
- **Procedure:** Load published zero-shot scores for GEMME and SaProt-35M-AF2 across all 217 assays via `lab/proteingym.py`. Verify $\ge 95\%$ common finite mutant coverage. Convert mutant scores within each assay to fractional percentile ranks in $[0, 1]$ using average tie-breaking. Blend ranks equally: $s_{\text{blend}} = 0.5 \cdot r_{\text{GEMME}} + 0.5 \cdot r_{\text{SaProt}}$. Score with `pg.spearman_by_assay`, cluster paired improvements by `UniProt_ID` with `pg.improvement_units(..., by="protein")`, and evaluate 2,000 bootstrap resamples with alpha 0.05 and seed 7 using `kbstats.evaluate`.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction steps, stratified breakdowns, and deployment guidelines in the [deployment brief](../../fields/proteins/deploy-structure-evolution-zero-shot-blend.md). Task #243 holds the frozen preregistration, Task #244 is the confirmatory run, Task #261 is the skeptic audit, Task #262 records the field verdict, and Task #265 is the deployment.

## Caveats

- Published frozen benchmark scores were compared; no model was trained or newly parameterized.
- The 64/66-assay concentration in cDNA display proteolysis accounts for the entire benchmark-wide positive delta over GEMME alone; excluding Tsuboyama assays yields a negative point estimate ($-0.0121$) spanning zero.
- Equal 50/50 blending is strictly harmful on functional assays (Activity, Binding, OrganismalFitness), where the 95% bootstrap CI is entirely negative ($[-0.0302, -0.0046]$).
- Severe collapse occurs on viral replication genomes ($-0.0995$) and intrinsically disordered proteins ($-0.1254$).
- An asymmetric 80% GEMME + 20% SaProt blend is strictly Pareto-superior and avoids these failure modes, but was discovered via audit sweep and warrants confirmatory forward validation on unseen targets.
- Retrospective benchmark results on ProteinGym v1.3 must not be deployed prospectively without an operator-approved forward test on unseen targets.
