---
title: "C13: Site-Mean Baseline vs Supervised Models Across Random and Contiguous Splits"
id: site-mean-crossover
kind: prereg
status: draft
date: 2026-11-01
field: proteins
hypothesis_slug: site-mean-baseline-crossover
baseline: "frozen zero-shot GEMME (and ESM2-35M)"
units: "proteins (by=protein)"
splits:
  - fold_random_5
  - fold_contiguous_5
n_train: [24, 48, 96]
evaluator: lab/proteingym.py
cluster: kbstats.evaluate
compute_budget: "minutes on 8 CPU cores"
---
