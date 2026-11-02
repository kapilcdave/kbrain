# ProSST-2048 and GEMME zero-shot rank blend validates benchmark-wide, dominating VenusREM on functional phenotypes

_2026-11-01. Validated experiment (Tasks #254, #257, #268, and #273); deployed in dry mode by Task #274._

## Claim

On the frozen ProteinGym v1.3 substitution benchmark across all 217 assays (186 independent UniProt target proteins, 2,465,767 mutants), an unassisted, equal-weight ($w=0.5 / 0.5$) within-assay percentile-rank blend of published ProSST-2048 (quantized 3D structure-token language model conditioned on AlphaFold2 backbones) and published GEMME (analytical epistatic evolutionary model on multiple sequence alignments) statistically significantly outperforms ProSST-2048 alone (+0.0259 Spearman per protein), GEMME alone (+0.0732), and VenusREM (+0.0129). This zero-cost, CPU-viable blend achieves a benchmark mean per-assay Spearman of **0.5485** (Rank 2 overall on ProteinGym v1.3), driven by super-additive functional synergy on Activity (+0.0524) and OrganismalFitness (+0.0668) as well as viral genomes (+0.0846). However, on physical folding stability assays, ProSST-2048 alone significantly outperforms the blend (-0.0257). For deployment, deploy the 50/50 blend for general-purpose functional variant effect prediction, retain ProSST-2048 alone for pure thermodynamic stability, and keep the system in dry mode pending operator-approved prospective validation.

## Measured result

All 217 assays and 186 independent UniProt protein holdouts passed the preregistered $\ge 95\%$ coverage check at 100.0% paired coverage (2,465,767 mutants). Zero assays were excluded.

Benchmark-wide metrics:
- **Mean Per-Assay Spearman:** Blend **0.5485** vs VenusREM **0.5357**, ProSST-2048 **0.5225**, GEMME **0.4743**, and ESM2-650M **0.4382**.
- **Leaderboard Standing:** Reaches **Rank 2** overall on ProteinGym v1.3, surpassing multi-billion parameter retrieval models (e.g. AIDO Protein-RAG 16B at 0.5419) and trailing only the retrieval-enhanced VenusREM2 harness (0.5560).
- **Primary Endpoint vs ProSST-2048 Alone:** Net mean per-protein improvement was **+0.025854 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.014460, +0.037304]**; top-5%-trimmed mean **+0.015829**; $n=186$ independent proteins; cluster seed 7). Both `ci_low > 0` and `net_mean_ex_top > 0` passed.
- **Constituent Dominance vs GEMME Alone:** Net mean per-protein improvement was **+0.073219** (95% CI **[+0.061330, +0.084370]**; top-5%-trimmed mean **+0.062380**), establishing that the blend statistically dominates both constituent models rather than merely tracking the stronger component.
- **Secondary Comparator vs VenusREM Alone:** Net mean per-protein improvement was **+0.012898** (95% CI **[+0.004508, +0.021389]**). The parameter-free blend statistically significantly beats the published leaderboard rank 1 representation ensemble.
- **Target Win Rate:** 116 wins (62.4%) vs 70 losses (37.6%) across 186 independent target proteins.
- **Rank-Permutation Negative Control:** Mean per-assay Spearman $\bar{\rho}_{\text{perm}} = \mathbf{0.000300}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation neutrality and pipeline integrity.
- **Hardware Profile:** Runs strictly on CPU in $< 5$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

The skeptic audit identified critical domain boundaries, trade-offs, and parameter stability:

1. **Significant Degradation on Thermodynamic Stability:**
   On biophysical `Stability` assays ($N=66$ assays, 66 proteins), ProSST-2048 alone significantly outperforms the blend:
   - ProSST-2048 alone: **0.6526**
   - GEMME alone: **0.5187**
   - Blend: **0.6269**
   - Net paired improvement vs ProSST-2048: **-0.02574** (95% CI **[-0.03820, -0.01385]**).
   - *Biological Mechanism*: ProSST captures 3D backbone packing, cavity volume, and local contact curvature directly from AlphaFold2 structural coordinates, which govern in vitro thermodynamic folding stability (e.g. cDNA display proteolysis). GEMME reflects evolutionary organismal fitness, where mutations can be selectively neutral or epistatically constrained in nature without affecting in vitro protease resistance. Blending with GEMME injects evolutionary noise into pure structural stability predictions.

2. **Super-Additive Synergy on Functional Phenotypes (Activity & Organismal Fitness):**
   On functional assays where structural packing and evolutionary epistasis both constrain fitness, the blend displays true super-additive synergy:
   - **Activity** ($N=43$ assays, 40 proteins): ProSST (0.4862) and GEMME (0.4853) are virtually identical alone, but their blend jumps to **0.5349** (Net improvement **+0.05239**, 95% CI **[+0.03363, +0.07120]**).
   - **OrganismalFitness** ($N=77$ assays, 64 proteins): ProSST achieves 0.4420 and GEMME achieves 0.4563, jumping to **0.5057** in the blend (Net improvement **+0.06675**, 95% CI **[+0.04694, +0.08583]**).
   - Unlike SaProt-35M (which degraded functional phenotypes when blended with GEMME), ProSST-2048 provides higher-resolution discrete structural tokens ($K=2048$) with disentangled attention that synergize with evolutionary epistasis on functional targets.

3. **Taxonomic Heterogeneity:**
   The benchmark gain is heavily concentrated in viral and human targets:
   - **Virus** ($N=31$ assays, 28 proteins): Net **+0.08456** (95% CI **[+0.04483, +0.12152]**).
   - **Human** ($N=96$ assays, 81 proteins): Net **+0.02139** (95% CI **[+0.00598, +0.03698]**).
   - **Eukaryote** ($N=40$ assays, 34 proteins): Net **+0.01361** (95% CI **[-0.00669, +0.03317]**, spans zero).
   - **Prokaryote** ($N=50$ assays, 43 proteins): Net **+0.00573** (95% CI **[-0.01347, +0.02500]**, spans zero; trimmed mean **-0.00005**).

4. **Broad Parameter Stability Basin:**
   An adversarial sweep over blending weights $w \cdot r_{\text{ProSST}} + (1-w) \cdot r_{\text{GEMME}}$ confirmed that the equal-weight ($w=0.5$) choice is not an overfit knife-edge:
   - All weights from $w=0.4$ to $w=0.9$ statistically significantly outperform ProSST alone with `ci_low > 0`.
   - Performance peaks at $w=0.6$ (mean Spearman **0.5509**, net **+0.0281**, 95% CI **[+0.0193, +0.0371]**).
   - Replacing percentile ranks with z-score normalization ($0.5 z_{\text{ProSST}} + 0.5 z_{\text{GEMME}}$) yields mean Spearman **0.5511** (net **+0.0279**, 95% CI **[+0.0162, +0.0394]**), verifying that the gain is intrinsic to combining structural and evolutionary representations rather than a rank artifact.

## Inference and conclusion

Discrete quantized 3D geometric tokens (ProSST-2048) and analytical epistatic evolutionary co-variation (GEMME) provide orthogonal and complementary representations of protein fitness. On functional targets (catalytic activity, binding, organismal fitness, viral escape), both physical structural packing and evolutionary selection constrain fitness, resulting in strong super-additive synergy ($+0.052$ to $+0.067$ Spearman gains) that outperforms the state-of-the-art representation ensemble VenusREM without requiring GPU compute.

However, in vitro thermodynamic stability (protease resistance and thermal denaturation) is governed almost entirely by physical backbone packing and cavity volume. Blending evolutionary organismal constraints into pure folding stability assays degrades performance ($-0.0257$ vs ProSST alone).

Keep the result in dry mode.
- **Deploy 50/50 Blend for Functional Phenotypes:** Deploy the equal-weight ProSST-2048 + GEMME rank blend for general-purpose fitness prediction across `Activity`, `OrganismalFitness`, `Binding`, and viral targets.
- **Selective Gate on Thermodynamic Stability:** For assays strictly measuring in vitro thermodynamic folding stability (`Stability` or `Expression`), retain **ProSST-2048 alone** ($0.6526$). Do not blend with GEMME for pure stability assays.
- **Condition-Aware Router:** A simple phenotype-aware router—deploying ProSST-2048 alone on Stability and the 50/50 blend on all other assays—theoretically achieves benchmark mean Spearman $\approx 0.556$, matching the multi-component VenusREM2 harness.
- **Forward Paper Test:** Prospective evaluation on an unseen forward DMS publication held out from ProteinGym v1.3 requires operator approval, with all model pairs, score orientations, and routing rules frozen before inspecting labels.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, published zero-shot scores, and reference metadata; 217 assays representing 186 independent UniProt target proteins. Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). ProteinGym benchmark reference: Notin et al.,
  [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** ProSST is described by Wang et al., 2023 / Li et al., NeurIPS 2024,
  [bioRxiv:2023.11.02.565261](https://doi.org/10.1101/2023.11.02.565261); GEMME by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); VenusREM by Tan et al., 2024,
  [bioRxiv:2024.06.12.598642](https://doi.org/10.1101/2024.06.12.598642).
- **Procedure:** Load published zero-shot scores for ProSST-2048, GEMME, and VenusREM across all 217 assays via `lab/proteingym.py`. Verify $\ge 95\%$ common finite mutant coverage. Convert mutant scores within each assay to fractional percentile ranks in $[0, 1]$ using average tie-breaking. Blend ranks equally: $s_{\text{blend}} = 0.5 \cdot r_{\text{ProSST}} + 0.5 \cdot r_{\text{GEMME}}$. Score with `pg.spearman_by_assay`, cluster paired improvements by `UniProt_ID` with `pg.improvement_units(..., by="protein")`, and evaluate 2,000 bootstrap resamples with alpha 0.05 and seed 7 using `kbstats.evaluate`.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction steps, stratified breakdowns, and deployment guidelines in the [deployment brief](../../fields/proteins/deploy-prosst-gemme-zero-shot-blend.md). Task #254 holds the frozen preregistration, Task #257 is the confirmatory run, Task #268 is the skeptic audit, Task #273 records the field verdict, and Task #274 is the deployment.

## Caveats

- Published frozen benchmark scores were compared; no model was newly parameterized or fine-tuned.
- Equal 50/50 blending significantly degrades performance on physical Stability assays ($-0.0257$ vs ProSST alone; 95% CI $[-0.0382, -0.0138]$).
- Gains are negligible / span zero on Prokaryotic targets ($+0.0057$, 95% CI $[-0.0135, +0.0250]$).
- Weight tuning ($w=0.6$) is a retrospective exploratory audit finding; the preregistered confirmatory test evaluated $w=0.5$.
- Retrospective benchmark results on ProteinGym v1.3 must not be deployed prospectively without an operator-approved forward test on unseen targets.
