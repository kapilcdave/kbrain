# MSA-depth gated GEMME/ESM2 routing: qualified reproduction note

## What was validated

On the frozen ProteinGym v1.3 backtest, a rule that blends published GEMME and
ESM2-650M ranks only for `High` MSA-depth assays, and otherwise uses GEMME,
improved over GEMME alone by **+0.013821 Spearman per UniProt protein** (95%
protein-cluster bootstrap CI **[+0.008664, +0.019153]**; **186** proteins,
217 assays). Its top-5%-trimmed mean improvement was **+0.007936**, so the
preregistered primary endpoint passed with complete score coverage.

This is not validation of MSA depth as a useful routing rule. The
preregistered unconditional 50/50 rank blend was better: mean per-assay
Spearman **0.4936** versus **0.4884** for the depth-gated rule, and
protein-level improvement over GEMME **+0.016038** versus **+0.013821**. The
direct paired difference was inconclusive but unfavorable to gating
(**-0.0022**, 95% CI **[-0.0121, +0.0066]**).

## Reproduce

1. Use ProteinGym v1.3 DMS substitutions and the frozen preregistration
   `inputs/msa-depth-gated-routing.md`. Load only published `GEMME` and
   `ESM2_650M` score columns and the reference `MSA_Neff_L_category`.
2. For every one of 217 assays, match the two score vectors and DMS labels by
   mutant. Require at least 95% coverage; the observed run had 100% coverage.
   Do not use any DMS label to select an assay, set a weight, or choose the
   depth threshold.
3. Convert each model's score vector to within-assay percentile ranks. On
   `High` assays, predict with their equal average. On `Medium` and `Low`
   assays, use GEMME alone.
4. Score through `lab/proteingym.py` `pg.spearman_by_assay`, form paired
   differences against GEMME with `pg.improvement_units(..., by="protein")`,
   and evaluate them using `kbstats.evaluate` with 2,000 bootstrap resamples,
   alpha 0.05, and seed 7.
5. Accept the narrow endpoint only if the confidence-interval lower bound and
   the top-5%-trimmed mean are positive. The observed values were +0.008664
   and +0.007936 respectively.

## Caveats

The result compares frozen published benchmark scores; it neither trains a
new model nor proves why either model succeeds. It is a backtest, not a
prospective protein-engineering result.

Its key mechanistic claim failed its own controls. Randomly assigning depth
labels also produced a positive improvement over GEMME (+0.007379, 95% CI
[+0.000668, +0.014621]). The depth-gated rule therefore should not be chosen
over an unconditional blend based on this evidence.

The model failure pattern is also taxonomic: ESM2-650M is weak on viral assays
(mean Spearman 0.2687 versus GEMME 0.4662), while Low-depth assays are mostly
Human and benefit from blending. MSA depth misses many viral failures and
suppresses some useful blends. Do not deploy the depth gate for a new target.

## Next decision

Before a forward paper test, obtain operator approval. Freeze GEMME-only,
static 50/50 blending, and a predeclared taxon-aware viral-exclusion rule;
freeze score orientation, coverage checks, taxonomy definitions, protein-level
endpoint, and bootstrap settings before inspecting any new DMS labels. A
useful replication needs an entirely unseen paper or prospective assay set and
must report through `lab/proteingym.py` with protein-clustered uncertainty.
