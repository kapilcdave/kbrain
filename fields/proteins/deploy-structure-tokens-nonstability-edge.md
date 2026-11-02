# SaProt-35M structure-token non-stability edge: qualified reproduction note

## What was validated

On ProteinGym v1.3's predeclared non-Stability assays (`coarse_selection_type != "Stability"`, comprising 151 assays across 120 unique UniProt IDs in Activity, Binding, Expression, and OrganismalFitness), published `SaProt_35M_AF2` (resolved via `pg.published_scores(aid, "SaProt (35M)")`) zero-shot scores outperformed same-scale sequence-only `ESM2_35M` scores by **+0.068882 Spearman per UniProt protein** (95% protein-cluster bootstrap CI **[+0.050325, +0.089884]**). Mean per-assay Spearman was **0.342152** for SaProt-35M versus **0.266218** for ESM2-35M.

The effect is broadly distributed across proteins rather than driven by outliers:
- 92 of 120 proteins (**76.7%**) favored SaProt over ESM2 (sign test $p = 1.88 \times 10^{-9}$, Wilcoxon signed-rank $p = 6.30 \times 10^{-11}$).
- Excluding the top 5% of proteins (6 units), the trimmed mean difference remained **+0.052686** (95% CI $[+0.037388, +0.067786]$).
- Excluding the top 10% of proteins (12 units), the trimmed mean remained **+0.041989** (95% CI $[+0.028397, +0.055706]$).
- Every non-Stability functional stratum demonstrated a statistically significant advantage: Activity $+0.0584$ (CI $[+0.0289, +0.0923]$), Binding $+0.0662$ (CI $[+0.0125, +0.1228]$), Expression $+0.0955$ (CI $[+0.0429, +0.1623]$), and OrganismalFitness $+0.0725$ (CI $[+0.0450, +0.1020]$).
- The confirmatory decision gate ($\text{ci\_low} > 0$) passed.

## Reproduce

1. Use staged ProteinGym v1.3 substitutions data (`data/proteingym/`), `DMS_substitutions_reference.csv`, and the frozen preregistration `inputs/structure-tokens-nonstability-edge.md` (Task #204).
2. Filter for all assays where `coarse_selection_type` is one of `Activity`, `Binding`, `Expression`, or `OrganismalFitness` (151 assays, 120 UniProt IDs).
3. For each assay, load published scores via `lab/proteingym.py` using `pg.published_scores(aid, "SaProt (35M)")` (resolving via alias `saprot35m -> saprot35maf2`) and `pg.published_scores(aid, "ESM2 (35M)")`.
4. Reindex both scores to the assay's `mutant` identifier and retain only finite paired mutant predictions. Require $\ge 95\%$ paired coverage per assay. (Observed: 151/151 assays passed at exactly 100.0% coverage; 0 excluded).
5. Compute per-assay Spearman rank correlations via `pg.spearman_by_assay` on the common mutant set.
6. Form paired per-protein improvement units using `pg.improvement_units(saprot_rho, esm2_rho, by="protein")`, which averages multiple assays sharing a UniProt ID before inference.
7. Run `kbstats.evaluate(units, n_boot=2000, alpha=0.05, seed=7)`. The observed result is `net_mean = 0.068882`, `ci_low = 0.050325`, `ci_high = 0.089884`, `n_units = 120`.

## Caveats and Failure Modes

1. **Intrinsically Disordered Proteins (IDPs)**: The primary failure mode of structure conditioning is disordered targets. On alpha-synuclein (`SYUA_HUMAN`), an IDP lacking stable tertiary structure where AlphaFold2 exhibits low confidence ($pLDDT < 50$), SaProt scores dropped to Spearman $-0.0451$ whereas ESM2 achieved $+0.1423$ ($\Delta\rho = -0.1874$). Forcing Foldseek 3Di tokens onto disordered conformational ensembles introduces misleading geometric noise. SaProt should not be applied to disordered proteins or low-pLDDT regions without a fallback mechanism.
2. **Not a Causal Ablation**: SaProt-35M and ESM2-35M were trained with different vocabularies, tokenizers, and corpora. While this validates an empirical zero-shot benchmark edge between the published artifacts, it does not constitute mathematical causal proof that 3Di geometric tokens alone created the lift.
3. **Absolute Performance Context**: While SaProt-35M ($0.342$) substantially outperforms ESM2-35M ($0.266$), both models trail MSA-based epistatic models like GEMME ($0.474$) and larger PLMs like ESM2-650M ($0.438$). SaProt-35M provides an efficient CPU-viable zero-shot baseline, not state-of-the-art absolute predictive power.

## Next Decision and Bigger Experiments

1. **Forward Paper Test (Requires Operator Approval)**: Before claiming general prospective utility, evaluate the frozen SaProt-35M vs ESM2-35M comparison on a newly published post-2024 DMS dataset not included in ProteinGym v1.3. As with all external evaluations, model definitions, score orientations, coverage rules, and bootstrap parameters must remain frozen before inspecting experimental labels.
2. **Confidence-Gated Hybrid Routing**: Test whether an automated structure-confidence gate (e.g. falling back to sequence-only ESM2 when AlphaFold2 residue-level pLDDT is $< 60$ or IUPred predicts disorder) mitigates the alpha-synuclein failure mode while preserving the $+0.069$ non-stability structural lift on well-folded domains.
3. **Low-N Supervised Representations**: Investigate whether SaProt-35M hidden representations or zero-shot scores provide better low-N transfer ($N=24, 48$) than ESM2-35M for supervised fitness regression on non-stability phenotypes.
