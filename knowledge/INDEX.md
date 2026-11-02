# Knowledge index

The map of our niche: protein mutation-effect prediction. The scout keeps this current; pages marked _(thin)_ need depth.

## The niche
- [Mutation-effect prediction dossier](../fields/proteins/DOSSIER.md): state of the art, ProteinGym, baselines, our verdicts
- [The lab](../lab/proteingym.py): the trusted evaluator

## Maps
- [Models](models.md): taxonomy, 97-model ProteinGym v1.3 benchmark, scaling limits, 2026 preprints (DEEP-Boltz, inference dropout, OOD priors, site-mean traps), and CPU feasibility
- [Low-N prediction](low-n.md): guide to supervised regimes (N=24..192), split leakage traps (random vs contiguous), linear fitness subspaces, site-mean dominance, and empirical crossover dynamics
- [Datasets](datasets.md): guide to ProteinGym v1.3 (DMS/indels/clinical), MaveDB, MegaScale, FLIP, and data leakage rules
- [Labs and companies](labs-and-companies.md): landscape of academic hubs (Marks, Fowler, LCQB, Rost, Baker), foundation consortia, and commercial platforms (Cradle, Generate)

## Pipeline
- [Candidate experiments](CANDIDATES.md): C1–C13 (CPU ensembles, model selection, low-N crossover, subspace projection, MC dropout, site-mean controls).
- [Opportunities](OPPORTUNITIES.md): 10 commercial and research opportunities (CPU engine, low-N auditor, model router, DEEP distogram potentials, MC uncertainty calibration).
- [Findings](findings/): validated experiments, one page each.
  - [Lab validation](findings/lab-validation.md): trusted evaluator reproduces the ProteinGym leaderboard.
  - [Augmented low-N regression](findings/augmented-low-n-regression.md): random-split ridge gain passes, but
    the single-substitution stratum is null and unseen-position design remains unvalidated.
  - [Label-efficient model selection](findings/label-efficient-model-selection.md): 24-label routing between
    GEMME and ESM2-650M beats GEMME on random splits, but remains dry-run pending unseen-target validation.
  - [Structure-token Stability edge](findings/structure-tokens-stability-edge.md): SaProt-35M-AF2 beats
    same-scale ESM2-35M on the frozen Stability subset, qualified to Tsuboyama-heavy small-domain data.
