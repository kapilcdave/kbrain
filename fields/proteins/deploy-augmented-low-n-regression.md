# Augmented low-N ridge: qualified reproduction note

## What was validated

With 48 labelled mutants per assay and five fixed **random** train/test replicates, a ridge model using frozen GEMME plus mutation-position/amino-acid indicators improved held-out Spearman over frozen GEMME by **+0.00994 per protein** (95% cluster-bootstrap CI **[+0.00451, +0.01570]**; **186** UniProt protein units). This satisfies the frozen primary endpoint.

## Reproduce

1. Use ProteinGym v1.3 DMS substitutions and the preregistration `inputs/augmented-low-n-regression.md`.
2. For every assay, use `lab/proteingym.py` `low_n` with `n_train=48`, five random replicates, and seed 0.
3. Fit the frozen procedure: training-only standardized GEMME score plus sparse `(position, mutant-amino-acid)` indicators; `RidgeCV` alpha grid `{0.01, 0.1, 1, 10, 100, 1000}`.
4. Compare to GEMME on the identical held-out rows, average replicates per assay, aggregate differences by UniProt ID with `pg.improvement_units(..., by="protein")`, and evaluate the 186 units with `kbstats.evaluate`.

## Caveat: do not deploy for new-position mutation design

This is not a general low-N protein-engineering method yet. The positive aggregate is driven by multi-mutant-dominated proteins (+0.05271; CI [+0.03402, +0.07464]). Single-mutant-dominated proteins are null (+0.00071; CI [-0.00393, +0.00474]). Random splits expose test mutations at positions seen in training, allowing positional fitness memorization. Use frozen GEMME rather than this augmentation when test positions are new.

## Next decision

The needed validation is a preregistered contiguous-position, single-substitution experiment. It must keep all test positions out of training and report protein-clustered paired improvements through `lab/proteingym.py` and `kbstats`.
