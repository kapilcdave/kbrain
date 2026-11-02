# Label-efficient zero-shot model selection: qualified deployment note

## What was validated

With an initial batch of **24 labelled mutants** per ProteinGym v1.3 substitution assay, select the published GEMME or ESM2-650M score by whichever has higher Spearman correlation on those 24 labels. Across five fixed random train/test splits, this produced held-out Spearman **+0.01645 per UniProt protein** over GEMME (95% protein-cluster bootstrap CI **[+0.00776, +0.02608]**; **186** protein units). The frozen primary endpoint passed.

## Reproduce

1. Use ProteinGym v1.3 DMS substitutions, the frozen preregistration `inputs/label-efficient-model-selection.md`, and the published `GEMME` and `ESM2_650M` mutant scores.
2. For every assay, call `lab/proteingym.py` `pg.low_n` with `n_train=24`, five random replicates, and seed 0.
3. Within each replicate, calculate training-only Spearman for GEMME and ESM2-650M against the 24 observed DMS scores. Return the complete test-mutant score vector from ESM2-650M only if its training correlation is strictly greater; otherwise return GEMME.
4. Score the exact held-out rows, average replicate correlations within assay, calculate paired improvements with `pg.improvement_units(..., by="protein")`, then use `kbstats.evaluate` with 2,000 bootstrap replicates, alpha 0.05, and seed 7.
5. Accept only if the protein-clustered CI lower bound and trimmed mean are positive. The observed values were +0.00776 and +0.00697, respectively.

## Caveats

This is evidence of improvement over GEMME, not evidence that label-driven hard selection beats every cheaper alternative: the preregistered label-free 50/50 rank blend also improved over GEMME (+0.01583; CI [+0.00512, +0.02695]). Softmax correlation weighting was a stronger secondary result (+0.03183; CI [+0.02348, +0.04090]), but it was not the primary decision rule.

The evaluation has random mutation splits. Other substitutions at a held-out position can remain in the 24-label training set, so it does not demonstrate position-unseen generalization or a prospective engineering outcome. ESM2-650M is a published frozen score in this benchmark, rather than a CPU-inference recommendation.

## Next decision

Before operational use, secure operator approval for a forward test on a completely unseen DMS paper or prospectively supplied target. Freeze the hard-selection, softmax, static-blend, and GEMME procedures before any labels from that target are inspected; report paired, protein-level results through `lab/proteingym.py` and `kbstats`.
