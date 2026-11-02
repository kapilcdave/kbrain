# SaProt-35M structure-token stability edge: qualified reproduction note

## What was validated

On ProteinGym v1.3's predeclared **Stability** subset, published
`SaProt_35M_AF2` zero-shot scores out-ranked published sequence-only
`ESM2_35M` scores by **+0.135743 Spearman per UniProt protein** (95%
protein-cluster bootstrap CI **[+0.098878, +0.173060]**; **66** proteins and
66 assays). Mean per-assay Spearman was **0.574932** for SaProt versus
**0.439189** for ESM2. The frozen primary endpoint passed.

## Reproduce

1. Use ProteinGym v1.3 DMS substitutions, the frozen preregistration
   `inputs/structure-tokens-stability-edge.md`, and only the published
   `SaProt_35M_AF2` and `ESM2_35M` columns.
2. Select every assay whose `coarse_selection_type` is `Stability`. For each
   assay, align scores by mutant and retain the common finite mask. Stop rather
   than omit an assay if either score is unavailable or coverage is below 95%.
3. Score both masked vectors using `lab/proteingym.py`
   `pg.spearman_by_assay`; no DMS labels may be used to alter a score.
4. Form paired deltas with `pg.improvement_units(..., by="protein")`, then run
   `kbstats.evaluate` with 2,000 bootstrap resamples, alpha 0.05, and seed 7.
   The observed paired coverage was 100% for every assay and the primary
   protein-level result was +0.135743.
5. Accept only if every frozen availability and coverage check passes and the
   bootstrap CI lower bound is positive. The observed lower bound was
   +0.098878.

## Caveats

This is a comparison of frozen published benchmark scores, not new model
training or evidence of causal mechanism. It does not show that SaProt beats
MSA-based methods such as GEMME, only the stated same-scale ESM2 baseline.

The Stability result is heavily concentrated: 64 of its 66 assays come from
the Tsuboyama et al. cDNA-display proteolysis platform, on small single domains
(mean length 70.4 aa, range 37--118). The two other Stability assays average a
negative delta (-0.0182). Do not apply this as evidence for large,
multi-domain, flexible proteins, another stability assay technology, or a
prospective engineering campaign. SaProt's positive descriptive advantage in
other phenotype categories also means this is not proof of a
Stability-exclusive effect.

## Next decision

Obtain operator approval before a forward paper test or a prospective
structure-token comparison. Keep the model pair, score orientation, coverage
rule, protein-level endpoint, and bootstrap settings frozen before seeing any
new DMS labels. A useful replication should include independent stability
measurement platforms and longer/multi-domain targets; report it through
`lab/proteingym.py` with protein-clustered uncertainty.
