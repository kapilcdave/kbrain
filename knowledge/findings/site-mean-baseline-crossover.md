# Site-Mean Baseline vs Supervised Models Across Random and Contiguous Splits

**Status:** proposed  
**Date:** 2026-11-01  
**Task:** #286 (chief plan)  
**Field:** proteins  
**Units:** proteins (186 UniProt IDs) clustered via `by="protein"` in `kbstats.evaluate`

## Hypothesis
A simple "Site-Mean Predictor" (predict empirical mean fitness of observed mutations at residue position $i$ in training, fall back to training global mean for unseen positions) will match or exceed complex supervised models under random splits due to positional-tolerance leakage, but collapse under `fold_contiguous_5` (position-disjoint) where no position-level information is available.

## Baselines
- Frozen zero-shot: GEMME, ESM2-35M (published)
- Pure empirical one-hot ridge
- Zero-shot augmented ridge (Hsu et al. 2022)

## Splits
- `fold_random_5` (random)
- `fold_contiguous_5` (contiguous/position-disjoint)

## Regimes
- $N \in \{24, 48, 96\}$ training mutants per protein

## Scoring
Use `lab/proteingym.py` only. Grade by protein-clustered bootstrap CI of improvement over stated baseline via `kbstats.evaluate({unit: improvement})`.

## Expected outcome
Quantify how much apparent supervised gain is trivial position-tolerance memorization vs transferable mutational biophysics. This is a decisive negative control for low-N claims.
