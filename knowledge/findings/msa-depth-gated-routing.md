# GEMME–ESM2 blending helps, but MSA depth does not justify the gate

_2026-11-01. Validated experiment (Tasks #181, #193, and #212); deployed in dry mode by Task #215._

## Claim

On the frozen ProteinGym v1.3 substitution benchmark, using an equal-rank GEMME/ESM2-650M blend on
`High`-MSA-depth assays and GEMME elsewhere improved over GEMME alone. The proposed mechanism did not
validate: an unconditional blend performed better, and randomized depth labels also produced a positive
gain. MSA depth should therefore not be used as an operational routing rule from this evidence.

## Measured result

The preregistered primary endpoint passed with complete score coverage across 217 assays. After repeated
assays were grouped by UniProt target, the depth-gated rule improved over GEMME by **+0.013821 mean
Spearman per protein** (95% protein-cluster bootstrap CI **[+0.008664, +0.019153]**; top-5%-trimmed mean
**+0.007936**; **186 proteins**). Mean per-assay Spearman was **0.4884** for the gated rule.

The mechanism controls do not support depth gating. The unconditional 50/50 within-assay rank blend reached
mean per-assay Spearman **0.4936** and improved over GEMME by **+0.016038 per protein**, exceeding the gated
rule (95% CI **[+0.005430, +0.027202]**). Their direct paired difference was **-0.0022** for gating (95% CI
**[-0.0121, +0.0066]**), which is inconclusive but points in the wrong direction. Randomly permuting the
depth categories still improved over GEMME by **+0.007379** (95% CI **[+0.000668, +0.014621]**).

## Inference and conclusion

Combining the frozen evolutionary and language-model rankings is useful on this retrospective benchmark,
but the evidence does not attribute that gain to MSA depth. The observed failure pattern is more consistent
with taxonomy being relevant: ESM2-650M was weak on viral assays (mean Spearman **0.2687**, versus **0.4662**
for GEMME), while 25 of 36 `Low`-depth assays were human and that depth stratum benefited from blending by
**+0.0314** over GEMME.

Keep the result in dry mode. Do not deploy the depth gate for a new target. The next defensible test is a
label-blind, entirely unseen DMS paper comparing GEMME, the static 50/50 blend, and a predeclared taxon-aware
viral-exclusion rule.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, published zero-shot scores, and reference MSA-depth metadata;
  217 assays grouped into 186 UniProt targets. Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). ProteinGym is described by Notin et al.,
  [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** GEMME is described by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574).
- **Procedure:** Align frozen GEMME and ESM2-650M scores by mutant, convert each to within-assay percentile
  ranks, average the ranks on `High`-depth assays, and use GEMME on `Medium` and `Low` assays. Score only with
  `pg.spearman_by_assay`, aggregate paired differences with `pg.improvement_units(..., by="protein")`, and
  grade 2,000 bootstrap resamples with alpha 0.05 and seed 7.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction
  steps and deployment constraints in the
  [deployment brief](../../fields/proteins/deploy-msa-depth-gated-routing.md). Task #181 holds the
  preregistration and experiment artifacts, Task #193 is the skeptic audit, and Task #212 records the field
  verdict.

## Caveats

- This is a retrospective comparison of published benchmark scores, not a prospective engineering result.
- The positive primary endpoint establishes improvement over GEMME, not superiority to static blending.
- The randomized-depth control also passed, so the result does not validate MSA depth as the mechanism.
- The taxonomic pattern is descriptive and was not the frozen primary rule; it needs an external,
  preregistered test before use.
- ESM2-650M is not CPU-native on the firm's machine; this experiment used ProteinGym's published scores.
