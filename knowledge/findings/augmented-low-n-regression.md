# Augmented low-N ridge passes random splits, not unseen-position design

_2026-11-01. Validated experiment (Tasks #174, #187, and #191)._

## Claim

With 48 labelled mutants per assay, a ridge model combining frozen GEMME scores with sparse
position/amino-acid indicators improved held-out Spearman under five fixed random splits. The result is a
qualified benchmark finding: it does **not** establish an advantage for single-substitution or unseen-position
protein design.

## Measured result

The preregistered primary endpoint passed across all 217 ProteinGym v1.3 substitution assays. After averaging
repeated assays by UniProt target, the augmented model improved over frozen GEMME by **+0.00994 mean
Spearman** (95% cluster-bootstrap CI **[+0.00451, +0.01570]**; **186 proteins**). The independent skeptic
reproduced the endpoint exactly from the saved per-protein results and found no test-label leakage.

The effect was concentrated in 33 multi-mutant-dominated proteins: **+0.05271** (95% CI
**[+0.03402, +0.07464]**). In the 153 single-mutant-dominated proteins, the improvement was **+0.00071**
(95% CI **[-0.00393, +0.00474]**), a null result. Removing the ten highest-improvement proteins also made the
all-protein interval cross zero (lower bound **-0.00043**).

## Inference and conclusion

Random splits let test variants reuse positions represented among the 48 training examples, so the indicator
features can learn positional fitness effects. That mechanism is useful for the tested random-split,
multi-mutant regime but does not show generalization to new positions. Keep frozen GEMME as the default when
candidate positions are unseen; test the augmentation next on ProteinGym's fixed contiguous-position folds,
restricted to single substitutions.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, 217 assays and 186 UniProt targets; Zenodo accessions
  [10.5281/zenodo.7259140](https://doi.org/10.5281/zenodo.7259140),
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500), and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). Benchmark reference: Notin et al.,
  ProteinGym, [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Procedure:** `n_train=48`, five random replicates, seed 0; training-only GEMME standardization; sparse
  position/mutant-amino-acid indicators; `RidgeCV` over `{0.01, 0.1, 1, 10, 100, 1000}`; protein-clustered
  bootstrap grading. The evolutionary-augmentation precedent is Hsu et al., 2022,
  [DOI:10.1038/s41587-021-01146-5](https://doi.org/10.1038/s41587-021-01146-5).
- **Code pointer:** trusted split/scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen
  reproduction procedure and caveat in the
  [deployment brief](../../fields/proteins/deploy-augmented-low-n-regression.md). Task #174 holds the experiment
  implementation and per-assay/per-protein outputs; Task #187 is the skeptic audit.

## Caveats

The preregistered random split is not position-disjoint. The pure-supervised control was scoreable for only
69/217 assays, and the `alpha=1e9` control shrank the GEMME coefficient too, making it a constant-prediction
control rather than a GEMME-equivalence control. Neither issue changes the paired primary endpoint, but both
controls should be corrected or labelled explicitly in any reuse.
