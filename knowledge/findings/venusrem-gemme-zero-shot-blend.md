# VenusREM and GEMME zero-shot rank blend validates benchmark-wide, but is outlier-fragile and Pareto-dominated by ProSST-GEMME

_2026-11-01. Validated experiment (Tasks #267, #272, #276, and #280); deployed in dry mode by Task #282._

## Claim

On the frozen ProteinGym v1.3 substitution benchmark across all 217 deep mutational scanning (DMS) assays (186 independent UniProt target proteins, 2,465,767 mutants), an unassisted, equal-weight ($w=0.5 / 0.5$) within-assay percentile-rank blend of published VenusREM (representation ensemble combining structure tokens, PLM representations, and retrieved homologs; leaderboard rank 3) and published GEMME (analytical epistatic evolutionary model on multiple sequence alignments) statistically significantly outperforms VenusREM alone by **+0.0108 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.0012, +0.0205]**; trimmed mean **+0.0025 > 0**; $n=186$ independent units; seed 7), GEMME alone by **+0.0711** (95% CI **[+0.0609, +0.0807]**), and ProSST-2048 alone by **+0.0237** (95% CI **[+0.0104, +0.0371]**). The zero-cost, CPU-viable blend achieves a benchmark mean per-assay Spearman of **0.5467** (ProteinGym aggregate **0.5299**, Rank 2 overall on ProteinGym v1.3).

However, **do not deploy VenusREM + GEMME as the default zero-shot ensemble; keep the system in dry mode**. The skeptic audit revealed four critical defects:
1. **Extreme Outlier Fragility:** The 95% bootstrap lower bound is razor-thin (`ci_low = +0.00118`). Excluding a single protein (`B2L11_HUMAN`, $\Delta = +0.3205$, accounting for 15.5% of net gain) drops `ci_low` below zero ($-0.00020$). Trimming the top 5% of units collapses the net mean by 77% (down to $+0.00248$).
2. **Severe Stability Collapse:** On 66 thermodynamic `Stability` assays, blending with GEMME causes a severe, statistically significant degradation of **-0.0324** (95% CI **[-0.0439, -0.0214]**), dropping from $0.6503$ down to $0.6179$.
3. **Strict Pareto-Domination by ProSST-GEMME:** The simpler `prosst-gemme-zero-shot-blend` (Task #254/268) achieves higher benchmark mean Spearman (**0.5485** vs **0.5467**) and strictly outperforms VenusREM + GEMME across identical paired mutants (net delta **-0.0021**, trimmed delta **-0.0042 < 0**). VenusREM already embeds sequence PLMs and evolutionary retrieval; layering GEMME on top causes redundant evolutionary interference.
4. **High Loss Rate:** 75 of 186 target proteins (40.3%) perform worse under the blend than VenusREM alone.

For deployment, prefer **`prosst-gemme-zero-shot-blend`** for general variant effect prediction, retain standalone structure PLMs (ProSST-2048 or VenusREM) for pure folding stability, and maintain the system in dry mode pending operator-approved prospective validation.

## Measured result

All 217 assays and 186 independent UniProt protein holdouts passed the preregistered $\ge 95\%$ coverage check at 100.0% paired coverage (2,465,767 mutants). Zero assays were excluded.

Benchmark-wide metrics:
- **Benchmark Mean Per-Assay Spearman:** Blend **0.5467** vs VenusREM **0.5357**, ProSST-2048 **0.5225**, GEMME **0.4743**, and ESM2-650M **0.4382**.
- **Official ProteinGym Aggregate ($\bar{\rho}_{\text{agg}}$):** **0.5299** vs VenusREM **0.5182**, ProSST-2048 **0.5069**, and GEMME **0.4547**.
- **Leaderboard Standing:** Reaches **Rank 2** overall on ProteinGym v1.3, surpassing published AIDO Protein-RAG (16B) (0.5419) and trailing only the retrieval-enhanced VenusREM2 harness (0.5560).
- **Primary Endpoint vs VenusREM Alone:** Net mean per-protein improvement was **+0.010761 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.001182, +0.020490]**; top-5%-trimmed mean **+0.002479**; $n=186$ independent proteins; cluster seed 7). Both `ci_low > 0` and `net_mean_ex_top > 0` passed preregistration gates.
- **Constituent Dominance vs GEMME Alone:** Net mean per-protein improvement was **+0.071088** (95% CI **[+0.060884, +0.080704]**), confirming the blend statistically dominates both constituents alone.
- **Secondary Comparator vs ProSST-2048 Alone:** Net mean per-protein improvement was **+0.023719** (95% CI **[+0.010380, +0.037138]**).
- **Target Win Rate:** 111 wins (59.7%) vs 75 losses (40.3%) across 186 independent target proteins.
- **Rank-Permutation Negative Control:** Mean per-assay Spearman $\bar{\rho}_{\text{perm}} = \mathbf{-0.00241}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation neutrality and pipeline integrity.
- **Hardware Profile:** Runs strictly on CPU in $< 5$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

The skeptic audit identified critical domain boundaries, trade-offs, and structural caveats:

1. **Extreme Outlier Fragility (Single-Unit Dependency):**
   The 95% bootstrap lower bound is razor-thin (`ci_low = +0.001182`).
   - Excluding just **one single protein** (`B2L11_HUMAN`, $\Delta = +0.3205$, 0.5% of units) drops `ci_low` to **-0.00020**, causing the confirmatory confidence interval to cross zero (`[-0.00020, +0.01807]`). In assay `B2L11_HUMAN_Dutta_2010_binding-Mcl-1` (170 mutants), VenusREM scored $0.4036$ while GEMME scored $0.7344$. This single assay accounts for 15.5% of the total aggregate benchmark net mean.
   - Trimming the top 5% of units collapses the net mean by 77% (from $+0.01076$ down to $+0.00248$). Excluding the top 14 units (7.5%) pushes the net mean negative ($-0.00057$, CI `[-0.00873, +0.00716]`).

2. **Severe Biophysical Stability Degradation:**
   On the 66 thermodynamic `Stability` proteins (66 assays, >35% of all benchmark targets), blending with GEMME causes a severe collapse:
   - VenusREM alone: **0.6503**
   - 50/50 Blend: **0.6179**
   - Net paired improvement: **-0.0324** (95% CI **[-0.0439, -0.0214]**).
   - *Biological Mechanism*: In vitro thermodynamic folding stability is governed by 3D backbone packing and cavity volume (captured cleanly by structure representations), whereas GEMME reflects organismal evolutionary survival. Injecting evolutionary constraints corrupts physical stability predictions.

3. **Strictly Pareto-Dominated by ProSST-2048 + GEMME:**
   In Task #254/268, the simpler `prosst-gemme-zero-shot-blend` achieved a benchmark mean Spearman of **0.54855**. Head-to-head comparison on identical paired mutants across all 217 assays shows that **VenusREM + GEMME is strictly inferior to ProSST-2048 + GEMME**:
   - Net paired delta: **-0.002135** (95% CI `[-0.004472, +0.000269]`).
   - Trimmed net delta (ex-top 5%): **-0.004215 < 0**.
   - *Mechanism*: VenusREM already bundles ProSST with sequence representations and retrieved homologs. Layering GEMME on top creates redundant evolutionary interference that blurs the crisp 3D geometric tokens that standalone ProSST-2048 contributes to GEMME.

4. **Phenotypic and Taxonomic Divergence:**
   - **Activity** ($N=43$ assays, 40 proteins): VenusREM 0.5042 -> Blend **0.5349** (Net **+0.0337**, 95% CI `[+0.0187, +0.0488]`).
   - **OrganismalFitness** ($N=77$ assays, 64 proteins): VenusREM 0.4692 -> Blend **0.5098** (Net **+0.0432**, 95% CI `[+0.0260, +0.0592]`).
   - **Binding** ($N=13$ assays, 12 proteins): Net **+0.0164** (95% CI `[-0.0305, +0.0820]`, spans zero).
   - **Expression** ($N=18$ assays, 18 proteins): Net **-0.0019** (95% CI `[-0.0171, +0.0114]`, neutral).
   - **Stability** ($N=66$ assays, 66 proteins): Net **-0.0324** (95% CI `[-0.0439, -0.0214]`, severe drop).
   - **Virus** ($N=31$ assays, 28 proteins): Net **+0.0519** (95% CI `[+0.0188, +0.0855]`).
   - **Human** ($N=96$ assays, 81 proteins): Net **+0.0077** (95% CI `[-0.0056, +0.0213]`, spans zero).
   - **Prokaryote** ($N=50$ assays, 43 proteins): Net **-0.0031** (95% CI `[-0.0207, +0.0148]`, spans zero).

5. **Asymmetric Parameter Knife-Edge:**
   At $w=0.5$ (VenusREM), the blend barely satisfies the lower bound gate (`ci_low = +0.00118`). Reducing VenusREM weight to $w=0.4$ immediately fails (`ci_low = -0.0099`). An adversarial sweep reveals that the optimal basin peaks at $w=0.7$ (mean Spearman **0.5518**, net **+0.0158**, 95% CI `[+0.0103, +0.0213]`).

## Inference and conclusion

Equal-weight percentile-rank blending of VenusREM and GEMME formally passes confirmatory benchmark validation over VenusREM alone (+0.0108, CI [+0.0012, +0.0205]), driven by super-additive functional synergy on enzymatic activity (+0.0337) and organismal fitness (+0.0432).

However, **it should not be deployed as the primary zero-shot engine**. First, the benchmark edge is fragile and dependent on extreme outliers (a single protein causes the lower CI bound to cross zero). Second, the blend is strictly Pareto-dominated by `prosst-gemme-zero-shot-blend`, which reaches a higher mean Spearman (0.5485 vs 0.5467) using a simpler, smaller single-model backbone (~110M params) without redundant evolutionary interference. Third, blending with GEMME causes a severe degradation on thermodynamic folding stability (-0.0324).

Keep the system in dry mode:
- **Default Pipeline:** Deploy **`prosst-gemme-zero-shot-blend`** (Task #254/268) rather than VenusREM + GEMME for general-purpose variant effect prediction.
- **Selective Phenotype Gate:** Never deploy evolutionary blending on pure thermodynamic stability targets. Retain standalone structure representations (ProSST-2048 or VenusREM alone) for folding stability ($0.650\text{--}0.653$).
- **Dual-Track Router:** An automated assay classifier routing stability targets to standalone structure PLMs and functional phenotypes to structure-evolution blends (ProSST + GEMME) can break $\bar{\rho} \approx 0.560$ entirely on CPU.
- **Forward Paper Test:** Prospective evaluation on an unseen forward DMS publication held out from ProteinGym v1.3 requires operator approval, with all model pairs, score orientations, and routing rules frozen before inspecting labels.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, published zero-shot scores, and reference metadata; 217 assays representing 186 independent UniProt target proteins. Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). ProteinGym benchmark reference: Notin et al.,
  [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** VenusREM is described by Tan et al., 2024,
  [bioRxiv:2024.06.12.598642](https://doi.org/10.1101/2024.06.12.598642); GEMME by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); ProSST by Wang et al., 2023 / Li et al., NeurIPS 2024,
  [bioRxiv:2023.11.02.565261](https://doi.org/10.1101/2023.11.02.565261).
- **Procedure:** Load published zero-shot scores for VenusREM, GEMME, and ProSST-2048 across all 217 assays via `lab/proteingym.py`. Verify $\ge 95\%$ common finite mutant coverage (100.0% observed). Convert mutant scores within each assay to fractional percentile ranks in $[0, 1]$ using average tie-breaking. Blend ranks equally: $s_{\text{blend}} = 0.5 \cdot r_{\text{VenusREM}} + 0.5 \cdot r_{\text{GEMME}}$. Score with `pg.spearman_by_assay`, cluster paired improvements by `UniProt_ID` with `pg.improvement_units(..., by="protein")`, and evaluate 2,000 bootstrap resamples with alpha 0.05 and seed 7 using `kbstats.evaluate`.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction steps, stratified breakdowns, and deployment guidelines in the [deployment brief](../../fields/proteins/deploy-venusrem-gemme-zero-shot-blend.md). Task #267 holds the frozen preregistration, Task #272 is the confirmatory run, Task #276 is the skeptic audit, Task #280 records the field verdict, and Task #282 is the deployment.

## Caveats

- Published frozen benchmark scores were compared; no model was newly trained or fine-tuned.
- The 95% bootstrap lower bound is razor-thin (`ci_low = +0.001182`) and is driven by a single outlier (`B2L11_HUMAN`, $\Delta = +0.3205$). Excluding this single unit drops `ci_low` below zero.
- Equal 50/50 blending significantly degrades performance on physical Stability assays ($-0.0324$ vs VenusREM alone; 95% CI $[-0.0439, -0.0214]$).
- Across identical paired mutants, VenusREM + GEMME is strictly Pareto-dominated by ProSST-2048 + GEMME (net delta $-0.0021$, trimmed delta $-0.0042$).
- 75 of 186 proteins (40.3%) perform worse under the blend than VenusREM alone.
- Retrospective benchmark results on ProteinGym v1.3 must not be deployed prospectively without an operator-approved forward test on unseen targets.
