# Twenty-four labels can route between GEMME and ESM2-650M

_2026-11-01. Validated experiment (Task #194); deployed in dry mode by Task #197._

## Claim

On ProteinGym v1.3 random low-N splits, choosing between frozen GEMME and ESM2-650M scores from their
training-only Spearman correlations on 24 labelled mutants improved held-out ranking over GEMME. This is a
qualified benchmark result, not evidence that hard selection is better than a label-free blend or that the
rule will generalize to a wholly unseen protein assay.

## Measured result

The preregistered primary endpoint passed on all 217 substitution assays. After the five fixed replicates
were averaged within assay and repeated assays were grouped by UniProt target, hard selection improved over
GEMME by **+0.01645 mean Spearman per protein** (95% protein-cluster bootstrap CI
**[+0.00776, +0.02608]**; top-5%-trimmed mean **+0.00697**; **186 proteins**). Raw mean held-out
assay Spearman was **0.49203**, versus **0.47412** for GEMME.

The controls qualify the mechanism and scope. ESM2-650M alone was worse than GEMME by **-0.04475**
(95% CI **[-0.06871, -0.01921]**), while shuffling the 24 training labels made hard selection harmful by
**-0.02840** (95% CI **[-0.04343, -0.01435]**). A label-free 50/50 rank blend also beat GEMME by
**+0.01583** (95% CI **[+0.00512, +0.02695]**). The prespecified secondary softmax-weighting rule had a
larger gain of **+0.03183** (95% CI **[+0.02348, +0.04090]**), but it was not the frozen primary rule.

## Inference and conclusion

Twenty-four labels contain useful information about whether an evolutionary model or a protein language
model better matches a given assay under random held-out-mutant sampling. The negative label-shuffle control
supports label-model association, rather than selection noise alone, as the source of the gain.

Keep the result in dry mode. The experiment did not directly establish that hard selection beats static
blending, and random mutation splits can expose training examples at positions represented in the test set.
Before operational use, freeze hard selection, softmax weighting, static blending, and GEMME, then compare
them on an entirely unseen DMS paper or prospectively supplied target.

## Data, procedure, and code

- **Data:** ProteinGym v1.3 DMS substitutions and published zero-shot scores, 217 assays grouped into 186
  UniProt targets; Zenodo accessions [10.5281/zenodo.7259140](https://doi.org/10.5281/zenodo.7259140),
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500), and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). Benchmark reference: Notin et al.,
  ProteinGym, [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** GEMME is described by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574).
- **Procedure:** For each of five random replicates from `pg.low_n` (`n_train=24`, seed 0), select
  ESM2-650M only when its training-only Spearman correlation is strictly greater than GEMME's; otherwise
  select GEMME. Score the exact held-out rows, average replicates within assay, aggregate paired differences
  by protein, and grade 2,000 bootstrap replicates with seed 7.
- **Code pointer:** trusted split and scoring code in
  [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction steps and deployment constraints in the
  [deployment brief](../../fields/proteins/deploy-label-efficient-model-selection.md). Task #194 holds the
  preregistration, experiment implementation, and saved result artifacts.

## Caveats

- The random split is not position-disjoint, so the result does not establish unseen-position
  generalization or prospective protein-engineering utility.
- The overlapping gains of hard selection and static blending were not compared by a frozen direct endpoint.
- The larger softmax result is secondary and needs independent confirmation.
- ESM2-650M was evaluated from ProteinGym's published frozen scores; this experiment does not establish a
  CPU-native inference path.
