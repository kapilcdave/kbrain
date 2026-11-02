# Cross-protein shrinkage gives a small 24-label routing gain

_2026-11-01. Validated retrospective experiment (Tasks #323 and #325); deployed in dry mode by Task #328._

## Claim

On the frozen ProteinGym v1.3 24-label random-split replay, shrinking a target's noisy support-set model
utility toward a leave-protein-out historical prediction improved held-out ranking over the frozen target-only
softmax router. This is a qualified retrospective result, not a production recommendation or evidence of
generalization to unseen positions or a new DMS target.

## Measured result

Across 217 assays grouped into 186 independent `UniProt_ID` proteins, the cross-protein-shrunk router achieved
mean held-out assay Spearman **0.509373**, versus **0.506510** for target-only softmax. The paired mean gain was
**+0.002994 Spearman per protein** (95% bootstrap CI **[+0.002016, +0.004115]**; 146 positive and 40 negative
units). The preregistered top-5%-trimmed mean remained positive at **+0.001743**, so both primary gates passed.

The candidate also beat the uniform 50/50 blend by **+0.018003** (95% CI **[+0.011310, +0.025301]**), GEMME
by **+0.033840** (95% CI **[+0.026015, +0.042539]**), a support-label permutation control by **+0.020814**
(95% CI **[+0.014281, +0.028359]**), and a metadata-only historical prior by **+0.001495** (95% CI
**[+0.000511, +0.002534]**).

## Inference and conclusion

Cross-protein historical utility supplies a small amount of useful shrinkage beyond the 24 target labels, and
the permutation and metadata-only controls support the specified feature-informed mechanism in this replay.
The magnitude is modest: the direct improvement over target-only softmax is about 0.003 Spearman per protein.

Keep the router in dry mode. ProteinGym is a burned retrospective benchmark, random splits can place different
substitutions at the same residue in support and test, and the experiment used staged published ESM2-650M
scores. The result authorizes an unchanged forward evaluation, not tuning or operational use.

## Data, procedure, and code

- **Data:** ProteinGym v1.3 DMS substitutions and published GEMME and ESM2-650M scores, 217 assays grouped into
  186 UniProt targets; Zenodo accessions [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). Benchmark reference: Notin et al.,
  ProteinGym, [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** GEMME is described by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574).
- **Procedure:** Rank each model within assay. For each of five fixed `pg.low_n` repeats with 24 support
  labels, combine target support utility equally with a historical utility estimate from
  `Pipeline(StandardScaler(), Ridge(alpha=10.0))` trained only on other proteins, then map the shrunk utility
  through the frozen sigmoid temperature of 0.10. Average repeats within assay, aggregate paired differences
  by protein, and grade 2,000 bootstrap replicates with seed 7.
- **Code pointer:** trusted split and scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); the exact
  frozen reproduction recipe, metrics, and use boundary are in the
  [deployment brief](../../fields/proteins/deploy-cross-protein-shrunk-low-n-router.md). Tasks #323 and #325
  retain the audit and preregistration artifacts.

## Caveats and next test

- Random held-out mutants are not position-disjoint and do not establish extrapolation to unseen residues.
- The historical training proteins and evaluation targets all come from the already-inspected ProteinGym
  benchmark; leave-protein-out fitting prevents direct target leakage but does not make the test prospective.
- ESM2-650M was evaluated from published scores, so this does not establish an affordable inference path for a
  new target.
- Before reading labels from an unseen public DMS paper or prospective 24-label batch, freeze the model pair,
  score orientation, percentile-rank convention, ridge and shrinkage parameters, support split, leave-target-
  protein exclusion, coverage rules, protein-clustered endpoint, and all five controls. Any paid score
  generation requires separate operator approval.
