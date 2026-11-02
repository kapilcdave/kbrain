# SaProt-35M beats same-scale ESM2 on ProteinGym Stability assays

_2026-11-01. Validated experiment (Tasks #186, #188, and #209); deployed in dry mode by Task #210._

## Claim

On the frozen ProteinGym v1.3 Stability subset, published SaProt-35M-AF2 scores rank substitutions better
than published sequence-only ESM2-35M scores. This is a qualified benchmark result for short, predominantly
Tsuboyama cDNA-display domains, not evidence of prospective engineering performance or a general advantage
across stability platforms.

## Measured result

All 66 preregistered Stability assays, representing 66 UniProt proteins, passed the frozen availability and
95% common-coverage checks; observed paired coverage was 100% in every assay. Mean per-assay Spearman was
**0.574932** for SaProt-35M-AF2 and **0.439189** for ESM2-35M. The paired improvement was **+0.135743 mean
Spearman per protein** (95% protein-cluster bootstrap CI **[+0.098878, +0.173060]**; **66 proteins**), so the
preregistered lower-bound-above-zero gate passed. The independent skeptic reproduced the primary result from
the staged assay and published-score files.

The evidence is concentrated rather than platform-diverse: 64 of 66 assays are from the Tsuboyama et al.
cDNA-display proteolysis dataset and cover small single domains (mean length 70.4 amino acids; range 37--118).
Across the two remaining Stability assays, the mean paired difference was **-0.0182**.

## Inference and conclusion

AlphaFold2-derived structure-token conditioning is associated with a large ranking improvement over the
parameter-matched sequence-only baseline in this frozen Stability benchmark. The comparison does not isolate
the causal contribution of structure tokens, show superiority to MSA methods such as GEMME, or establish that
the effect is specific to Stability phenotypes.

Use SaProt-35M-AF2 as the preferred published small-model comparator for this narrow benchmark regime. Keep
the result in dry mode until it is replicated on a label-blind, independent stability dataset that includes
other measurement platforms and longer or multi-domain proteins.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions and published zero-shot scores; Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). ProteinGym is described by Notin et al.,
  [arXiv:2306.12204](https://arxiv.org/abs/2306.12204); the dominant experimental platform by Tsuboyama et al.,
  2023, [DOI:10.1038/s41586-023-06240-5](https://doi.org/10.1038/s41586-023-06240-5).
- **Models:** SaProt is described by Su et al., 2024,
  [bioRxiv:2023.10.02.560515](https://doi.org/10.1101/2023.10.02.560515); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574).
- **Procedure:** Select the preregistered `Stability` assays, align both published score columns by mutant,
  apply their common finite mask, score each with `pg.spearman_by_assay`, form protein-level paired differences
  with `pg.improvement_units(..., by="protein")`, and grade 2,000 bootstrap resamples with alpha 0.05 and seed 7.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction
  steps and deployment qualifications in the
  [deployment brief](../../fields/proteins/deploy-structure-tokens-stability-edge.md). Task #188 is the skeptic
  audit and Task #209 records the field verdict.

## Caveats

- Published frozen benchmark scores were compared; no model was trained or newly run.
- The 64/66-assay platform concentration makes the nominal assay count look more diverse than the evidence is.
- The two assays outside the dominant platform do not support an advantage, but are too few for a decisive
  platform-generalization test.
- The result does not cover large, flexible, or multi-domain targets, a prospective campaign, or non-Stability
  phenotype categories.
