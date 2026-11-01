# Candidate experiments

The niche: protein mutation-effect prediction on ProteinGym v1.3 (217 DMS substitution assays). Every candidate
runs on 8 CPU cores / 7 GB / no GPU and is scored only through `lab/proteingym.py`. Units = assays (or proteins:
use `by="protein"` when one protein has several assays). The chief picks; the scout adds more.

## Starter slate (operator + Claude, 2026-11-01)

### C1. Cheap zero-shot ensemble vs its best member
- **Idea:** rank-average the published scores of models that are cheap to run (Site-Independent, EVmutation,
  GEMME, ESM2 8M/35M, VESPA) and compare with the best single cheap model.
- **Why:** if a free ensemble of cheap models approaches the 650M-3B models, protein engineers without GPUs gain
  the most. Published scores exist for every mutant, so this costs minutes.
- **Data:** `pg.published_scores` for each member. **Baseline:** the best member by mean Spearman (fixed in the
  prereg from the leaderboard, not chosen after). **Units:** proteins. **CPU:** minutes.

### C2. Label-efficient model selection (24 labels)
- **Idea:** with only 24 labeled mutants of a protein, choose which published model (or a 2-3 model weighted
  blend) to trust for THAT protein; score on the remaining mutants.
- **Why:** model rankings vary wildly by protein and assay type; an engineer always has a few measurements.
- **Baseline:** the single best model globally (fixed in advance). **Split:** `pg.low_n(n_train=24, reps=5)`.
- **Units:** proteins. **CPU:** minutes to an hour.

### C3. Augmented low-N regression
- **Idea:** ridge regression on one-hot features plus a zero-shot score as a feature (Hsu et al. 2022,
  Nat Biotechnol, "augmented" models) at n = 24 / 48 / 96, contiguous folds, vs zero-shot alone.
- **Baseline:** the zero-shot score alone (Spearman on the same test mutants). **Units:** assays.
- **CPU:** one-hot ridge is seconds per assay.

### C4. Where do small PLMs fail?
- **Idea:** explain the per-assay gap between ESM2-35M and the best MSA-based models by MSA depth
  (`MSA_Neff_L_category`), taxon, selection type, sequence length.
- **Output:** an understanding page plus the 1-2 sharpest follow-up experiments. Not a pass/fail test.

### C5. Positional prior from a few labels
- **Idea:** with n labeled mutants, estimate a per-position tolerance (mean fitness at positions seen) and add
  it to a zero-shot score; positions are the main source of variance in many DMS assays.
- **Baseline:** the zero-shot score alone. **Split:** `random` vs `contiguous` (contiguous is the honest one:
  positions in the test fold are unseen). **Units:** assays.

## Scout additions
(newest first)
