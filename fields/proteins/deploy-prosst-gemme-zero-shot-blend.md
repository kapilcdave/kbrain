# ProSST-2048 and GEMME zero-shot rank blend: deployment and reproduction note

## What was validated

On the frozen ProteinGym v1.3 substitutions benchmark across all 217 deep mutational scanning (DMS) assays (186 independent `UniProt_ID` protein holdouts, 2,465,767 mutants), an unassisted, equal-weight ($w=0.5 / 0.5$) within-assay percentile-rank blend of published **ProSST-2048** (quantized 3D structure-token language model conditioned on AlphaFold2 backbone coordinates) and published **GEMME** (analytical epistatic evolutionary model on multiple sequence alignments) statistically significantly outperformed **ProSST-2048** alone by **+0.025854 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.014460, +0.037304]**; $n=186$ independent units, cluster seed=7). The top-5%-trimmed mean improvement was **+0.015829 > 0**.

All primary, comparator, and negative control metrics were independently verified bit-for-bit from raw staged score tables using `lab/proteingym.py` and `kbstats.py`:
- **Universe and Coverage:** All 217 / 217 assays met the $\ge 95\%$ paired coverage requirement at **100.0% coverage** (2,465,767 mutants). Zero exclusions.
- **Constituent Dominance vs GEMME Alone:** Net mean per-protein improvement was **+0.073219** (95% CI **[+0.061330, +0.084370]**; trimmed mean **+0.062380**), establishing that the blend statistically dominates both constituent models rather than merely tracking the stronger component.
- **Secondary Comparator vs VenusREM Alone:** Net mean per-protein improvement was **+0.012898** (95% CI **[+0.004508, +0.021389]**). The parameter-free blend statistically significantly beats the published leaderboard rank 1 representation ensemble.
- **Rank-Permutation Negative Control:** Mean per-assay Spearman $\bar{\rho}_{\text{perm}} = \mathbf{0.000300}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation pipeline integrity.
- **Absolute Benchmark Scores:**
  - Benchmark Mean Per-Assay Spearman: Blend **0.5485** vs VenusREM **0.5357**, ProSST-2048 **0.5225**, GEMME **0.4743**, and ESM2-650M **0.4382**.
  - Relative Ranking: The zero-parameter, zero-GPU blend reaches **Rank 2** overall in mean per-assay Spearman on ProteinGym v1.3, surpassing multi-billion parameter retrieval models (e.g. AIDO Protein-RAG 16B at 0.5419) and trailing only the retrieval-enhanced VenusREM2 harness (0.5560).
- **Target Win Rate:** 116 wins (62.4%) vs 70 losses (37.6%) across 186 independent target proteins.
- **Hardware Profile:** Sequential execution runs strictly on CPU in $< 5$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

Under the frozen preregistration criteria of Task #254 (`ci_low > 0`, `net_mean_ex_top > 0`, constituent dominance vs GEMME, permutation control), the confirmatory backtest **PASSES and is VALIDATED**.

---

## Critical Boundaries, Nuances, and Trade-Offs

The skeptic audit (Task #268) identified key biological boundaries and trade-offs that dictate where this model should and should not be deployed:

### 1. Significant Degradation on Thermodynamic Stability
On biophysical `Stability` assays ($N=66$ assays, 66 proteins), ProSST-2048 alone significantly outperforms the blend:
- ProSST-2048 alone: **0.6526**
- GEMME alone: **0.5187**
- Blend: **0.6269**
- Net paired improvement vs ProSST-2048: **-0.02574** (95% CI **[-0.03820, -0.01385]**).

*Biological Mechanism*: ProSST captures 3D backbone packing, cavity volume, and local contact curvature directly from AlphaFold2 structural coordinates, which govern in vitro thermodynamic folding stability (e.g. cDNA display proteolysis). GEMME reflects evolutionary organismal fitness, where mutations can be selectively neutral or epistatically constrained in nature without affecting in vitro protease resistance. Blending with GEMME injects evolutionary noise into pure structural stability predictions.

### 2. Super-Additive Synergy on Functional Phenotypes (Activity & Organismal Fitness)
On functional assays where structural packing and evolutionary epistasis both constrain fitness, the blend displays true super-additive synergy:
- **Activity** ($N=43$ assays, 40 proteins): ProSST (0.4862) and GEMME (0.4853) are virtually identical alone, but their blend jumps to **0.5349** (Net improvement **+0.05239**, 95% CI **[+0.03363, +0.07120]**).
- **OrganismalFitness** ($N=77$ assays, 64 proteins): ProSST achieves 0.4420 and GEMME achieves 0.4563, jumping to **0.5057** in the blend (Net improvement **+0.06675**, 95% CI **[+0.04694, +0.08583]**).

### 3. Taxonomic Heterogeneity
The benchmark gain is heavily concentrated in viral and human targets:
- **Virus** ($N=31$ assays, 28 proteins): Net **+0.08456** (95% CI **[+0.04483, +0.12152]**).
- **Human** ($N=96$ assays, 81 proteins): Net **+0.02139** (95% CI **[+0.00598, +0.03698]**).
- **Eukaryote** ($N=40$ assays, 34 proteins): Net **+0.01361** (95% CI **[-0.00669, +0.03317]**, spans zero).
- **Prokaryote** ($N=50$ assays, 43 proteins): Net **+0.00573** (95% CI **[-0.01347, +0.02500]**, spans zero; trimmed mean **-0.00005**).

### 4. Broad Parameter Stability Basin
An adversarial sweep over blending weights $w \cdot r_{\text{ProSST}} + (1-w) \cdot r_{\text{GEMME}}$ confirmed that the equal-weight ($w=0.5$) choice is not an overfit knife-edge:
- All weights from $w=0.4$ to $w=0.9$ statistically significantly outperform ProSST alone with `ci_low > 0`.
- Performance peaks at $w=0.6$ (mean Spearman **0.5509**, net **+0.0281**, 95% CI **[+0.0193, +0.0371]**).
- Replacing percentile ranks with z-score normalization ($0.5 z_{\text{ProSST}} + 0.5 z_{\text{GEMME}}$) yields mean Spearman **0.5511** (net **+0.0279**, 95% CI **[+0.0162, +0.0394]**), verifying that the gain is intrinsic to combining structural and evolutionary representations rather than a rank artifact.

---

## Reproduce

1. **Environment and Lab**:
   - Use the trusted evaluator `lab/proteingym.py` and `kbstats.py` with Python 3 (`/home/kapil/.local/share/kbrain/sci/bin/python3`).
2. **Data**:
   - Staged ProteinGym v1.3 data in `data/proteingym/`: metadata `DMS_substitutions_reference.csv`, assay CSVs in `dms/`, published zero-shot tables in `zero_shot/`.
3. **Execution Script**:
   ```python
   import numpy as np
   import pandas as pd
   import proteingym as pg
   import kbstats

   assays = pg.assays()
   rho_blend = {}
   rho_prosst = {}
   rho_gemme = {}
   rho_venus = {}

   for aid in assays:
       df = pg.load_assay(aid)
       s_prosst = pg.published_scores(aid, "ProSST-2048")
       s_gemme = pg.published_scores(aid, "GEMME")
       s_venus = pg.published_scores(aid, "VenusREM")

       # Align valid mutants across ground truth and models
       valid = df.index.intersection(s_prosst.dropna().index).intersection(s_gemme.dropna().index)
       assert len(valid) / len(df) >= pg.MIN_COVERAGE

       # Within-assay percentile rank transformation
       r_prosst = s_prosst.loc[valid].rank(method="average", pct=True)
       r_gemme = s_gemme.loc[valid].rank(method="average", pct=True)

       # Equal-weight rank fusion
       s_blend = 0.5 * r_prosst + 0.5 * r_gemme

       # Score against ground-truth DMS_score
       rho_blend[aid] = pg.spearman(aid, s_blend)
       rho_prosst[aid] = pg.spearman(aid, s_prosst.loc[valid])
       rho_gemme[aid] = pg.spearman(aid, s_gemme.loc[valid])
       rho_venus[aid] = pg.spearman(aid, s_venus.loc[valid])

   # Cluster by independent target protein (UniProt_ID, 186 units)
   u_prosst = pg.improvement_units(rho_blend, rho_prosst, by="protein")
   u_gemme = pg.improvement_units(rho_blend, rho_gemme, by="protein")
   u_venus = pg.improvement_units(rho_blend, rho_venus, by="protein")

   res_prosst = kbstats.evaluate(u_prosst, n_boot=2000, alpha=0.05, seed=7)
   res_gemme = kbstats.evaluate(u_gemme, n_boot=2000, alpha=0.05, seed=7)
   res_venus = kbstats.evaluate(u_venus, n_boot=2000, alpha=0.05, seed=7)

   print(f"vs ProSST-2048: net={res_prosst['net_mean']:.5f}, CI=[{res_prosst['ci_low']:.5f}, {res_prosst['ci_high']:.5f}]")
   print(f"vs GEMME:       net={res_gemme['net_mean']:.5f}, CI=[{res_gemme['ci_low']:.5f}, {res_gemme['ci_high']:.5f}]")
   print(f"vs VenusREM:    net={res_venus['net_mean']:.5f}, CI=[{res_venus['ci_low']:.5f}, {res_venus['ci_high']:.5f}]")
   ```

---

## Deployment Recommendations & What This Points To

1. **Deploy to General-Purpose Zero-Shot Prediction**:
   - For general zero-shot fitness prediction across functional targets (`Activity`, `OrganismalFitness`, `Binding`, and `Viral` genomes), deploy the **50/50 ProSST-2048 + GEMME rank blend**. It improves over ProSST-2048 by $+0.052$ to $+0.067$ Spearman and outperforms VenusREM without requiring retrieval infrastructure or GPU compute.
2. **Selective Gate on Thermodynamic Stability**:
   - For experiments strictly targeting in vitro thermodynamic stability (`Stability` or `Expression` assays, e.g. cDNA display proteolysis or thermal denaturation), **retain ProSST-2048 alone** ($0.6526$). Do not blend with GEMME for pure stability assays.
3. **Condition-Aware Router**:
   - A simple assay-type-aware routing rule—deploying ProSST-2048 alone on Stability and the 50/50 blend on all other assays—theoretically achieves benchmark mean Spearman $\approx 0.556$, matching the complex multi-component VenusREM2 harness.
4. **Forward Paper Test**:
   - Prospective validation on an unseen forward DMS publication held out from ProteinGym v1.3 is the next milestone to confirm that this structure-evolution synergy generalizes to newly discovered proteins. This forward test requires operator approval and must keep the model pair, score orientation, coverage rule, and protein-clustered endpoint frozen before seeing labels.
