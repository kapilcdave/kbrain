# Lab validation: our evaluator reproduces the ProteinGym leaderboard

_2026-11-01. Operator + Claude. Not an experiment: a check that `lab/proteingym.py` scores like ProteinGym does._

**Measured.** Recomputing per-assay Spearman from the published v1.3 per-mutant scores, for all 217 DMS
substitution assays, matches the published `DMS_substitutions_Spearman_DMS_level.csv` to within 0.0005 (its
3-decimal rounding) for ESM2 8M / 35M / 650M, Site-Independent, GEMME and TranceptEVE L. The official
aggregation (mean within protein, then selection type, then across types) gives:

| Model | Mean per-assay Spearman | ProteinGym aggregate |
|---|---|---|
| TranceptEVE L | 0.4745 | 0.4558 |
| GEMME | 0.4743 | 0.4547 |
| ESM2 (650M) | 0.4382 | 0.4137 |
| Site-Independent | 0.3688 | 0.3594 |
| ESM2 (35M) | 0.3188 | 0.3208 |
| ESM2 (8M) | 0.2056 | 0.2257 |

**Inference.** GEMME (MSA-based, runs on a CPU) is level with TranceptEVE L and ahead of ESM2-650M on the
headline metric, while CPU-sized protein language models trail far behind. Cheap is not automatically weak in
this niche; that is the opening for candidate C1.

Data: ProteinGym v1.3 (`DMS_ProteinGym_substitutions`, `zero_shot_substitutions_scores`,
`cv_folds_singles_substitutions`), https://proteingym.org.
