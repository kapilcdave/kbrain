# Cross-protein-shrunk low-N router: reproduction and use note

## Result

On the frozen retrospective ProteinGym v1.3 24-label random-split protocol, the cross-protein-shrunk router achieved mean held-out assay Spearman **0.509373**, versus **0.506510** for the frozen target-only softmax router. The primary independent-unit result was **+0.002994 Spearman per `UniProt_ID` protein** (95% bootstrap CI **[+0.002016, +0.004115]**, $n=186$); its prescribed top-5%-trimmed mean was **+0.001743**. The protocol therefore passed its frozen statistical gates.

This is a small, qualified retrospective improvement, not a production recommendation. The test set is a burned ProteinGym benchmark; each random split can put different substitutions at the same residue in support and test; and it uses staged published ESM2-650M scores, not local inference.

## Frozen procedure

1. For each eligible assay, retain mutants with finite published GEMME and ESM2-650M scores and replace each whole-assay score vector by average-tie percentile ranks.
2. For each of the five `pg.low_n(..., n_train=24, reps=5, seed=0)` support sets, calculate the GEMME and ESM2 support Spearman correlations and their difference $d_s$.
3. Train `Pipeline(StandardScaler(), Ridge(alpha=10.0))` on source assay/repeat records from **other `UniProt_ID` proteins only**. The fixed features are $d_s$, the two support correlations, whole-assay GEMME/ESM2 Spearman agreement, and mean absolute rank difference. Source outcomes are their held-out ESM2-minus-GEMME correlations.
4. Set $\tilde d=0.5d_s+0.5\hat d_h$, choose ESM2 weight $\sigma(\tilde d/0.10)$, and predict the held-out rows with the corresponding rank mixture. Do not alter alpha, shrinkage, temperature, features, eligibility, or seeds.
5. Average repeat Spearman by assay, cluster the paired candidate-minus-softmax differences by `UniProt_ID`, then evaluate with `pg.improvement_units(..., by="protein")` and `kbstats.evaluate(..., n_boot=2000, alpha=0.05, seed=7)`.

The reported checks were: candidate minus uniform **+0.018003** (CI **[+0.011310, +0.025301]**), candidate minus GEMME **+0.033840** (CI **[+0.026015, +0.042539]**), candidate minus permuted-support control **+0.020814** (CI **[+0.014281, +0.028359]**), and candidate minus metadata-only prior **+0.001495** (CI **[+0.000511, +0.002534]**).

## Use boundary and next test

Do not deploy or tune this router from the ProteinGym replay. A real use test requires operator approval and an unseen forward DMS paper or a prospective 24-label batch. Before its labels are read, freeze the two published score sources and orientation, percentile-rank rule, Ridge and shrinkage parameters, 24-label split, leave-target-protein meta-training exclusion, coverage criteria, and protein-clustered endpoint. Also include target-only softmax, uniform mixing, GEMME, support-label permutation, and metadata-only prior controls.

Sources: frozen preregistration and Task #323 skeptic audit; ProteinGym v1.3 [Zenodo 7352500](https://doi.org/10.5281/zenodo.7352500), [Zenodo 10052327](https://doi.org/10.5281/zenodo.10052327); GEMME [Laine et al., 2019](https://doi.org/10.1093/molbev/msz179); ESM2 [Lin et al., 2023](https://doi.org/10.1126/science.ade2574).
