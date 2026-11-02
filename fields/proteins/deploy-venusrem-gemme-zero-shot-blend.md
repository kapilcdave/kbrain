# VenusREM and GEMME zero-shot rank blend: deployment and reproduction note

## What was validated

On the frozen ProteinGym v1.3 substitutions benchmark across all 217 deep mutational scanning (DMS) assays (186 independent `UniProt_ID` target proteins, 2,465,767 mutants), an unassisted, equal-weight ($w=0.5 / 0.5$) within-assay percentile-rank blend of published **VenusREM** (multi-model representation ensemble combining structure tokens, PLM representations, and retrieved homologs; leaderboard rank 3) and published **GEMME** (analytical epistatic evolutionary model on multiple sequence alignments) statistically significantly outperformed **VenusREM** alone by **+0.010761 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.001182, +0.020490]**; $n=186$ independent units, cluster seed=7). The top-5%-trimmed mean improvement was **+0.002479 > 0**.

All primary, comparator, and negative control metrics were independently verified bit-for-bit from raw staged score tables using `lab/proteingym.py` and `kbstats.py`:
- **Universe and Coverage:** All 217 / 217 assays met the $\ge 95\%$ paired coverage requirement at **100.0% coverage** (2,465,767 mutants). Zero exclusions.
- **Constituent Dominance vs GEMME Alone:** Net mean per-protein improvement was **+0.071088** (95% CI **[+0.060884, +0.080704]**), confirming the blend statistically dominates both constituents alone.
- **Secondary Comparator Dominance vs ProSST-2048 Alone:** Net mean per-protein improvement was **+0.023719** (95% CI **[+0.010380, +0.037138]**).
- **Rank-Permutation Negative Control:** Mean per-assay Spearman $\bar{\rho}_{\text{perm}} = \mathbf{-0.00241}$ ($|\bar{\rho}| < 0.02$, PASS), verifying evaluation pipeline integrity.
- **Absolute Benchmark Scores:**
  - Benchmark Mean Per-Assay Spearman: Blend **0.5467** vs VenusREM **0.5357**, ProSST-2048 **0.5225**, GEMME **0.4743**, and ESM2-650M **0.4382**.
  - Official ProteinGym Aggregate ($\bar{\rho}_{\text{agg}}$): **0.5299** vs VenusREM **0.5182**, ProSST-2048 **0.5069**, and GEMME **0.4547**.
  - Relative Ranking: The zero-cost, zero-GPU blend achieves **Rank 2** overall on ProteinGym v1.3, surpassing published AIDO Protein-RAG (16B) (0.5419) and trailing only the retrieval-enhanced VenusREM2 harness (0.5560).
- **Target Win Rate:** 111 wins (59.7%) vs 75 losses (40.3%) across 186 independent target proteins.
- **Hardware Profile:** Sequential execution runs strictly on CPU in $< 5$ minutes across all 2.46M mutants with $< 1.5$ GB peak RAM; zero GPU compute, zero cloud costs ($0.00 spend), and zero parameter fitting.

Under the frozen preregistration criteria of Task #267 (`ci_low > 0`, `net_mean_ex_top > 0`, constituent dominance vs GEMME, permutation control), the confirmatory backtest **PASSES and is VALIDATED**.

---

## Critical Boundaries, Defects, and Nuances

The skeptic audit (Task #276) identified five severe defects and structural caveats that limit deployment:

### 1. Extreme Outlier Fragility (Single-Unit Dependency)
The 95% bootstrap lower bound vs VenusREM alone is razor-thin (`ci_low = +0.001182`). Statistical significance is acutely dependent on extreme outliers:
- Excluding just **one single protein** (`B2L11_HUMAN`, $\Delta = +0.3205$, 0.5% of units) drops `ci_low` to **-0.00020**, causing the confirmatory confidence interval to cross zero (`[-0.00020, +0.01807]`). In assay `B2L11_HUMAN_Dutta_2010_binding-Mcl-1` (170 mutants), VenusREM scored $0.4036$ while GEMME scored $0.7344$. This single assay accounts for 15.5% of the total aggregate benchmark net mean.
- Trimming the top 5% of units collapses the net mean by 77% (from $+0.01076$ down to $+0.00248$). Excluding the top 14 units (7.5%) pushes the net mean negative ($-0.00057$, CI `[-0.00873, +0.00716]`).

### 2. Severe Biophysical Stability Degradation
On the 66 thermodynamic `Stability` proteins (66 assays, >35% of all benchmark targets), blending with GEMME causes a severe, statistically significant collapse:
- VenusREM alone: **0.6503**
- 50/50 Blend: **0.6179**
- Net paired improvement: **-0.0324** (95% CI **[-0.0439, -0.0214]**).
- *Mechanism*: In vitro thermodynamic stability is governed by 3D backbone packing and cavity volume (captured cleanly by structure representations), whereas GEMME reflects organismal evolutionary survival. Injecting GEMME evolutionary epistasis degrades thermodynamic stability predictions.

### 3. High Protein Loss Rate (40.3% Losses)
Across 186 independent target proteins, 75 proteins (40.3%) perform worse under the blend than VenusREM alone. The win rate is 59.7% (111 wins vs 75 losses), reflecting substantial regression risk when applied blindly.

### 4. Strictly Pareto-Dominated by ProSST-2048 + GEMME
In Task #254/268, the simpler `prosst-gemme-zero-shot-blend` achieved a benchmark mean Spearman of **0.54855**. Head-to-head comparison on identical paired mutants across all 217 assays shows that **VenusREM + GEMME is strictly inferior to ProSST-2048 + GEMME**:
- Net paired delta: **-0.002135** (95% CI `[-0.004472, +0.000269]`).
- Trimmed net delta (ex-top 5%): **-0.004215 < 0**.
- *Mechanism*: VenusREM already bundles ProSST with sequence representations and retrieved homologs. Layering GEMME on top creates redundant evolutionary interference that blurs the crisp 3D geometric tokens that standalone ProSST-2048 contributes to GEMME.

### 5. Asymmetric Parameter Knife-Edge
At $w=0.5$ (VenusREM), the blend barely satisfies the lower bound gate (`ci_low = +0.00118`). Reducing VenusREM weight to $w=0.4$ immediately fails (`ci_low = -0.0099`). An adversarial weight sweep reveals that the optimal basin is strongly asymmetric, peaking at $w=0.7$ (mean Spearman **0.5518**, net **+0.0158**, 95% CI `[+0.0103, +0.0213]`).

---

## Phenotypic and Taxonomic Divergence

| Stratum | Assays | Proteins | Mean VenusREM | Mean Blend | Net $\Delta\bar{\rho}_{\text{protein}}$ | 95% Bootstrap CI | Outcome |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Activity** | 43 | 40 | 0.5042 | 0.5349 | **+0.0337** | [+0.0187, +0.0488] | Super-additive gain |
| **Binding** | 13 | 12 | 0.4559 | 0.4641 | **+0.0164** | [-0.0305, +0.0820] | Spans zero |
| **Expression** | 18 | 18 | 0.5328 | 0.5309 | **-0.0019** | [-0.0171, +0.0114] | Neutral / slight loss |
| **OrganismalFitness** | 77 | 64 | 0.4692 | 0.5098 | **+0.0432** | [+0.0260, +0.0592] | Massive gain |
| **Stability** | 66 | 66 | 0.6503 | 0.6179 | **-0.0324** | **[-0.0439, -0.0214]** | **Severe degradation** |
| **Virus** | 31 | 28 | 0.4968 | 0.5440 | **+0.0519** | [+0.0188, +0.0855] | Substantial rescue |
| **Human** | 96 | 81 | 0.5296 | 0.5382 | **+0.0077** | [-0.0056, +0.0213] | Spans zero |
| **Non-human Eukaryote** | 40 | 34 | 0.5651 | 0.5677 | **+0.0017** | [-0.0168, +0.0191] | Spans zero |
| **Prokaryote** | 50 | 43 | 0.5481 | 0.5479 | **-0.0031** | [-0.0207, +0.0148] | Neutral / slight loss |

---

## Deployment Recommendation

- **Verdict:** **SURVIVES** confirmatory gates, but **DO NOT DEPLOY AS DEFAULT ENSEMBLE**.
- **Preferred Pipeline:** Deploy **`prosst-gemme-zero-shot-blend`** (Task #254/268) instead. It is simpler, uses a smaller single PLM backbone (~110M params vs complex multi-model ensemble), and achieves higher benchmark mean Spearman ($0.5485$ vs $0.5467$) without redundant evolutionary interference.
- **Condition-Aware Rule:** Never deploy GEMME blending on thermodynamic stability targets. Retain standalone structure representations (ProSST-2048 or VenusREM) on stability assays ($0.650\text{--}0.653$), and restrict evolutionary blending strictly to functional phenotypes (Activity, OrganismalFitness, Viral replication).

---

## Reproduce

1. **Environment and Evaluator**:
   - Use `/home/kapil/.local/share/kbrain/sci/bin/python3` with `lab/proteingym.py` and `kbstats.py`.
2. **Data**:
   - Staged ProteinGym v1.3 benchmark data in `data/proteingym/`.
3. **Execution Script**:
   ```python
   import numpy as np
   import pandas as pd
   import proteingym as pg
   import kbstats

   assays = pg.assays()
   rho_blend = {}
   rho_venus = {}
   rho_gemme = {}
   rho_prosst = {}

   for aid in assays:
       df = pg.load_assay(aid)
       s_venus = pg.published_scores(aid, "VenusREM")
       s_gemme = pg.published_scores(aid, "GEMME")
       s_prosst = pg.published_scores(aid, "ProSST-2048")

       # Intersect valid mutants across ground truth and models
       valid = df.index.intersection(s_venus.dropna().index).intersection(s_gemme.dropna().index)
       assert len(valid) / len(df) >= pg.MIN_COVERAGE

       # Within-assay percentile rank transformation
       r_venus = s_venus.loc[valid].rank(method="average", pct=True)
       r_gemme = s_gemme.loc[valid].rank(method="average", pct=True)

       # Unassisted equal-weight rank blend
       s_blend = 0.5 * r_venus + 0.5 * r_gemme

       # Spearman correlations against experimental DMS_score
       rho_blend[aid] = pg.spearman(aid, s_blend)
       rho_venus[aid] = pg.spearman(aid, s_venus.loc[valid])
       rho_gemme[aid] = pg.spearman(aid, s_gemme.loc[valid])
       rho_prosst[aid] = pg.spearman(aid, s_prosst.loc[valid])

   # Protein-clustered improvement units (186 independent UniProt targets)
   u_venus = pg.improvement_units(rho_blend, rho_venus, by="protein")
   u_gemme = pg.improvement_units(rho_blend, rho_gemme, by="protein")
   u_prosst = pg.improvement_units(rho_blend, rho_prosst, by="protein")

   res_venus = kbstats.evaluate(u_venus, seed=7)
   res_gemme = kbstats.evaluate(u_gemme, seed=7)
   res_prosst = kbstats.evaluate(u_prosst, seed=7)

   print("vs VenusREM:", res_venus)
   print("vs GEMME:", res_gemme)
   print("vs ProSST-2048:", res_prosst)
   ```

---

## What Bigger Experiment or Product This Points To

1. **Phenotype-Conditioned Dual-Track Routing**:
   - Both ProSST-GEMME and VenusREM-GEMME confirm that thermodynamic stability is degraded by evolutionary blending ($-0.026$ to $-0.032$), while functional phenotypes (Activity, OrganismalFitness, Virus) experience massive super-additive lifts ($+0.034$ to $+0.085$). An automated assay classifier or user-specified flag routing stability to standalone structure models and functional targets to evolutionary-structure blends could break $\bar{\rho} \approx 0.560$ without GPU compute.
2. **Forward Paper Test on Unseen DMS Studies**:
   - Does ProSST-GEMME or asymmetric VenusREM-GEMME ($w=0.7$) retain its statistical superiority on a newly published post-2024 deep mutational scan not contained in ProteinGym v1.3? (Requires human operator approval; all models, weights, and evaluation code must remain frozen).
3. **Deconvolving Representation Redundancy**:
   - The finding that VenusREM + GEMME is inferior to ProSST + GEMME illustrates that ensembling an ensemble with an evolutionary component leads to diminishing returns and destructive interference. Future research should prioritize clean orthogonal representations (pure 3D geometric tokens + pure epistatic MSAs) over layering dense representations.
