# Knowledge index

The map of our niche: protein mutation-effect prediction. The scout keeps this current; pages marked _(thin)_ need depth.

## The niche
- [Mutation-effect prediction dossier](../fields/proteins/DOSSIER.md): state of the art, ProteinGym, baselines, our verdicts
- [The lab](../lab/proteingym.py): the trusted evaluator

## Maps
- [Models](models.md): taxonomy, 97-model ProteinGym v1.3 benchmark, scaling limits, 2026 preprints (Sparse Causal SAE circuits, PRIZM low-N selection, ProtModernBERT compute efficiency, BioEvidence LLM scaling, VenusRAR multi-agent reasoning, Woolley-Wilke viability bimodality, PG-LLM frontier LLMs & MSA depth invariance, AINN-P1 linear mLSTM, zero-shot epistasis limits, CIR-DDG geometry adapters, ORBIT-FMIB epistasis tracking, AssayRouter utility priors, RegimeFormer perturbation regimes, SPURS anti-symmetry, RipplePLM perturbation fields, orthogonal PLM projection, VenusREM2 retrieval harness, Cerebra-Epistasis, EvoIF IRL, AIDO.Protein-RAG, TriFit dynamics, reverse distillation, Proust, DEEP-Boltz, inference dropout, OOD priors, site-mean traps), and CPU feasibility
- [Low-N prediction](low-n.md): guide to supervised regimes (N=24..192), split leakage traps (random vs contiguous), tabular in-context learning (TabPFN), linear fitness subspaces, site-mean dominance, PRIZM low-N model selection, and empirical crossover dynamics
- [Datasets](datasets.md): guide to ProteinGym v1.3 (DMS/indels/clinical), viability bimodality & deleterious tail inflation, DeePEn mutational distance trajectories, viral vs cellular DMS dynamics, TadA-Bench campaign replay, MaveDB, MegaScale, FLIP, and data leakage rules
- [Labs and companies](labs-and-companies.md): landscape of academic hubs (Marks, Fowler, LCQB, Rost, Baker, Wilke/Ellington, ai4protein/SJTU, Loschmidt Labs/DTU Biosustain, Green Lab/Harvard), foundation consortia (EvolutionaryScale, Meta, DeepMind, GenBio, Multiverse Computing), and commercial platforms (Cradle, Generate)

## Pipeline
- [Candidate experiments](CANDIDATES.md): C1–C27 (CPU ensembles, model selection, low-N crossover, subspace projection, MC dropout, site-mean controls, GNM dynamics, TabPFN low-N, position-adaptive logit fusion, composable multi-mutant epistasis, thermodynamic anti-symmetry, orthogonal property projection, historical utility routing, interface contact density residuals, mutational depth decay profiling, hard-threshold MSA gating, viable-subspace collapse auditing, post-PLM structural steric & SASA gating, PRIZM low-N model selection, 3D contact-dense causal weighting).
- [Opportunities](OPPORTUNITIES.md): 25 commercial and research opportunities (CPU engine, low-N auditor, model router, static ensemble validation, DEEP distograms, MC dropout, GNM dynamics, TabPFN screening, VRH retrieval middleware, composable epistasis profiler, temporal campaign auditor, thermodynamic anti-symmetry enforcer, meta-utility predictor router, interface geometric adapter, mutational distance decay auditor, constant-memory mLSTM inference engine, viable-subspace model auditor, structural CoT sanity-check middleware, PRIZM low-N model selection engine, sparse causal circuit auditor).
- [Findings](findings/): validated experiments, one page each.
  - [Lab validation](findings/lab-validation.md): trusted evaluator reproduces the ProteinGym leaderboard.
  - [Augmented low-N regression](findings/augmented-low-n-regression.md): random-split ridge gain passes, but
    the single-substitution stratum is null and unseen-position design remains unvalidated.
  - [Label-efficient model selection](findings/label-efficient-model-selection.md): 24-label routing between
    GEMME and ESM2-650M beats GEMME on random splits, but remains dry-run pending unseen-target validation.
  - [Structure-token Stability edge](findings/structure-tokens-stability-edge.md): SaProt-35M-AF2 beats
    same-scale ESM2-35M on the frozen Stability subset, qualified to Tsuboyama-heavy small-domain data.
  - [MSA-depth gated routing](findings/msa-depth-gated-routing.md): GEMME/ESM2-650M blending beats GEMME,
    but an unconditional blend is better and randomized depth also passes; do not deploy the depth gate.
