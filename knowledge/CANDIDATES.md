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

### C10. Decision-Benchmarked Crossover: At What N Does Empirical Ridge Overtake Zero-Shot Priors on Contiguous Splits?
- **Idea:** Measure the exact training size $N \in \{12, 24, 48, 96, 192\}$ where a pure empirical ridge regression
  (one-hot features alone) and an augmented ridge regression (one-hot + zero-shot prior) surpass frozen zero-shot
  priors (GEMME, ESM2-35M) on held-out mutants under `fold_contiguous_5` (position-disjoint test mutants).
- **Why:** Ding et al. (bioRxiv Oct 2026) established that wet-lab measurements overtake foundation models between
  $N=50$ and $N=100$ in active acquisition. However, protein engineers face a critical dilemma: when mutating
  unseen structural positions (the `fold_contiguous_5` regime), can empirical data at $N \approx 48-96$ generalize
  without an evolutionary prior, or does the evolutionary prior retain an enduring margin? Pinpointing this crossover
  resolves when a wet-lab team can stop relying on foundation models and rely purely on local assay feedback.
- **Data:** Single-substitution assays with `fold_contiguous_5` in `data/proteingym/dms/` and `pg.published_scores`.
- **Baseline:** Frozen zero-shot GEMME and ESM2-35M scores alone.
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 5–10 minutes on 8 CPU cores (closed-form scikit-learn Ridge across 5 folds).

### C9. Structure-Aware vs Sequence-Only Small PLMs on CPU: SaProt-35M vs ESM2-35M by Selection Type
- **Idea:** Compare SaProt-35M-AF2 against ESM2-35M across all 217 ProteinGym v1.3 DMS substitution assays
  (186 independent UniProt proteins) and test whether 3D structure conditioning (Foldseek 3Di tokens) provides
  a statistically significant improvement across all functional selection types (Stability, Activity, Binding,
  Expression, OrganismalFitness), or if the benefit is confined to stability phenotypes.
- **Why:** At an identical 35M parameter budget (both running in seconds on an 8-core CPU), SaProt-35M achieves
  ~0.4130 mean Spearman vs ESM2-35M's ~0.3188—nearly matching the 650M-parameter ESM2-650M (0.4382). However,
  structural models are hypothesized to overfit rigid backbone coordinates and fail on allosteric binding or
  catalytic turnover where conformational dynamics matter. Stratifying by `coarse_selection_type` resolves where
  structure tokens add genuine predictive edge vs where pure sequence representations suffice.
- **Data:** `pg.published_scores(aid, "SaProt_35M_AF2")` and `pg.published_scores(aid, "ESM2_35M")`, with
  selection metadata from `pg.reference()`.
- **Baseline:** ESM2-35M published scores (fixed baseline).
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** < 1 minute (scores are precomputed in `data/proteingym/zero_shot/`).

### C8. Additive vs Epistatic Fitness Prediction on Multiple-Mutant Assays
- **Idea:** On the 69 assays in ProteinGym v1.3 containing multiple substitutions (~1.77M mutants), test whether
  epistatic models with explicit pairwise couplings (GEMME, EVmutation) outperform additive PLM log-odds sums
  (ESM2-35M, ESM2-650M) by a wider margin than on single mutants.
- **Why:** Multiple mutations exhibit epistatic non-additivity (sign epistasis, stability collapse). Standard zero-shot
  PLM scoring sums single-site marginal log-odds ($\sum_i \Delta \log P_i$), assuming site independence. If GEMME's
  spectral co-variation terms capture true physical epistasis, its advantage over PLMs should widen markedly on
  multiple mutants compared to single substitutions.
- **Baseline:** ESM2 (650M) and ESM2 (35M) published scores evaluated on the same multiple-mutant subsets.
- **Data:** `pg.load_assay(aid)` for assays where `DMS_number_multiple_mutants > 0`, plus `pg.published_scores`.
- **Units:** proteins (or assays).
- **CPU:** minutes (scores pre-computed).

### C7. MSA-depth gated blend: GEMME vs ESM2-35M
- **Idea:** Scale the weighting between GEMME (MSA-based) and ESM2-35M (sequence PLM) by alignment depth
  (`MSA_Neff_L_category` in `reference()`). When $N_{eff}/L$ is low, weight ESM2 higher; when high, weight
  GEMME higher.
- **Why:** GEMME degrades when alignments are sparse, where PLMs remain stable. A simple parametric gate based
  on $N_{eff}/L$ should strictly dominate either fixed blend across all 217 assays.
- **Baseline:** Fixed 50/50 rank average of GEMME and ESM2-35M.
- **Units:** assays.
- **CPU:** <1 minute.

### C6. CPU-native zero-shot baseline: GEMME + ESM2-35M vs ESM2-650M
- **Idea:** Rank-average GEMME and ESM2-35M (both run locally on an 8-core CPU) and test against ESM2-650M
  (the standard GPU baseline) across all 217 DMS assays.
- **Why:** If a 35M PLM + analytical MSA beats a 650M GPU model with a positive CI, kbrain establishes a
  strictly superior, zero-GPU baseline for the community.
- **Data:** `pg.published_scores(aid, "GEMME")`, `pg.published_scores(aid, "ESM2 (35M)")`.
- **Baseline:** ESM2 (650M) published scores (fixed from leaderboard: 0.4382).
- **Units:** proteins (or assays).
- **CPU:** seconds to minutes.
