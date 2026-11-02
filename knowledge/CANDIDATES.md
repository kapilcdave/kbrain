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

### C34. Combinatorial Multi-Mutant Epistatic Density Degradation: PLMs vs Homology Baselines (The Talpir-Fleishman Benchmark)
- **Idea:** On ProteinGym v1.3's 69 multiple-mutant assays (~1.77M variants), stratify predictions by mutational Hamming distance ($K \in \{2, 3, 4, 5+\}$) and benchmark the decay rate of zero-shot PLMs (ESM2-35M, ESM2-650M) against evolutionary homology models (GEMME, EVmutation) and simple site-independent position weight matrices. Test whether the PLM predictive advantage over simple position-specific frequencies monotonically collapses to zero as mutational density $K$ increases, as hypothesized by Talpir & Fleishman (bioRxiv 2026).
- **Why:** Talpir & Fleishman (bioRxiv May 2026, DOI: 10.64898/2026.05.01.722313) proved that PLMs do not consistently outperform classical homology baselines on mutation-dense designs. By evaluating this across all 69 multi-mutant ProteinGym assays using precomputed scores, we establish whether PLM fitness scoring on multi-point variants is an illusion driven by single-point marginals.
- **Data:** ProteinGym multiple-mutant assays in `data/proteingym/dms/` and precomputed published scores (`zero_shot/`).
- **Baseline:** ESM2-650M published scores.
- **Units:** Proteins (`by="protein"` across multi-mutant UniProt IDs).
- **CPU:** 2–3 minutes on 8 CPU cores.

### C33. Parameter-Free RSALOR vs Small PLMs on CPU: Dissecting Core Conservation vs Surface Solvent Accessibility
- **Idea:** Benchmark the parameter-free RSALOR model ($\text{Score} = \text{RSA} \times \text{LOR}$) against small PLMs (ESM2-35M, SaProt-35M) and GEMME across all 217 ProteinGym substitution assays, stratifying by residue solvent exposure ($\text{RSA} < 0.2$ buried core vs $\text{RSA} \ge 0.2$ surface exposed). Test whether an analytical hybrid combining RSALOR with GEMME or ESM2-35M strictly dominates each individual predictor without GPU compute.
- **Why:** Tsishyn et al. (Bioinformatics 2025, DOI: 10.1093/bioinformatics/btaf322) reported 0.4848 average Spearman across ProteinGym with zero learned parameters, beating ESM2-650M (0.4382). Evaluating where RSALOR outperforms or complements PLMs isolates whether neural attention weights add predictive value beyond solvent accessibility and MSA frequencies, and offers a parameter-free calibration term.
- **Data:** ProteinGym v1.3 substitution reference, published scores for GEMME, ESM2-35M, SaProt-35M, and RSALOR scores.
- **Baseline:** GEMME alone (0.4743) and ESM2-35M (0.3188).
- **Units:** Proteins (`by="protein"` across 186 UniProt IDs) via `improvement_units()`.
- **CPU:** 2–3 minutes on 8 CPU cores.

### C32. Nucleotide Mutational Supply & Codon-Distance Decoupling from Zero-Shot PLM Log-Odds (The MacLean-Robertson Bias Filter)
- **Idea:** For all single-nucleotide reachable vs 2-/3-nucleotide reachable substitutions in ProteinGym assays where wild-type cDNA/mRNA codon sequences are known, test whether adjusting zero-shot PLM log-odds ($\Delta \log P$) by subtracting expected codon transition-transversion log-odds (decoupling mutational supply from biophysical selection) improves Spearman correlation on unbiased saturation mutagenesis (NNK/NNS) assays.
- **Why:** MacLean et al. (bioRxiv July 2026, DOI: 10.64898/2026.07.06.736753) proved that PLMs conflate nucleotide mutational accessibility with protein fitness because natural training databases reflect mutational supply. Saturation mutagenesis screens test all 19 amino acids regardless of codon distance. If PLMs penalize 2-nt and 3-nt substitutions simply because they are rare in natural evolution, a lightweight nucleotide distance correction restores true biophysical ranking on CPU in seconds.
- **Data:** ProteinGym substitution reference table (`pg.reference()`), wild-type coding sequences, and precomputed ESM2-35M / ESM2-650M published scores.
- **Baseline:** Raw ESM2-35M and ESM2-650M published scores.
- **Units:** Proteins (`by="protein"` across UniProt IDs) via `improvement_units()`.
- **CPU:** 2–3 minutes on 8 CPU cores.

### C31. Hybrid Ranking-Regression Loss (RankReg) vs Pure Ridge Regression in Low-N Regimes (N=24, 48)
- **Idea:** Benchmark a hybrid ranking-regression loss function (RankReg: $\min_w \alpha \mathcal{L}_{\text{MSE}}(y, \hat{y}) + (1-\alpha) \mathcal{L}_{\text{Rank}}(y, \hat{y})$ with pairwise ranking hinge/logistic loss) against standard MSE-minimizing Ridge regression across ProteinGym substitution assays at $N \in \{24, 48, 96\}$ under both `fold_random_5` and `fold_contiguous_5`. Inputs are frozen zero-shot scores (GEMME, ESM2-35M) and one-hot indicators.
- **Why:** Standard supervised models in directed evolution optimize MSE, which overfits absolute assay measurement noise and non-linear readout compression at the expense of candidate rank ordering. Conversely, pure pairwise ranking objectives lose metric calibration. Xu et al. (REAP / RankReg, Nature Communications 2026, DOI: 10.1038/s41467-026-76264-2) proved that joint ranking-regression optimization enabled rapid functional hotspot discovery and 57- to 104-fold activity gains in automated enzyme campaigns. Optimizing RankReg on CPU via fast SciPy L-BFGS takes seconds per assay and directly tests whether rank-preserving supervision beats standard Ridge on held-out mutants.
- **Data:** ProteinGym v1.3 substitution assays with `fold_random_5` and `fold_contiguous_5` in `data/proteingym/dms/` and `pg.published_scores`.
- **Baseline:** Standard MSE-minimizing Ridge regression (Candidate C3) and frozen zero-shot priors alone.
- **Units:** Proteins (`by="protein"` across 186 UniProt IDs) via `improvement_units()`.
- **CPU:** 3–5 minutes on 8 CPU cores.

### C30. Cross-Assay "Variant Soundness" Consensus Gating for Multi-Assay Protein Targets (The ESMRank Protocol)
- **Idea:** For proteins with multiple overlapping DMS assays in ProteinGym (e.g., beta-lactamase, GB1, PTEN, TP53, SARS-CoV-2 RBD, CFTR), compute the cross-experiment rank-fusion consensus score ("variant soundness" from Arnese & Gambardella, Nature / npj 2026). Evaluate whether zero-shot foundation models (GEMME, ESM2-35M, SaProt-35M) correlate significantly higher with the consensus rank landscape than with individual raw assay readouts, and whether filtering out variants with high inter-assay divergence clarifies true biophysical model accuracy.
- **Why:** Arnese & Gambardella (Nature / npj 2026, DOI: 10.1038/s44320-026-00252-3) demonstrated across ~1,100 MAVEs that cross-assay disagreement represents experiment-specific noise (e.g. selection thresholds, FACS gating, host cell stress), whereas overlap-aware rank fusion isolates a consensus landscape enriched for structural stability constraints. Testing this across ProteinGym's multi-assay proteins reveals whether foundation models are unfairly penalized by assay-specific noise and establishes a clean, consensus benchmark for variant effect prediction.
- **Data:** ProteinGym v1.3 assays for proteins with $\ge 2$ independent DMS datasets and precomputed zero-shot predictions (`data/proteingym/zero_shot/`).
- **Baseline:** Raw single-assay Spearman rank correlations.
- **Units:** Proteins (multi-assay UniProt IDs) via `improvement_units()`.
- **CPU:** 1–2 minutes on 8 CPU cores.

### C29. Intrinsic Disorder & pLDDT Masking Filter for Structure-Augmented Zero-Shot Ensembles (The Sharma-Gitter Disordered Filter)
- **Idea:** Benchmark whether filtering or gating structure-based scores (SaProt-35M, ProteinMPNN, ESM-IF1) by local AlphaFold2 pLDDT and predicted disorder—relying exclusively on sequence PLMs (ESM2-35M) or evolutionary MSAs (GEMME) at positions with pLDDT < 70 or high disorder—improves overall zero-shot ranking performance across ProteinGym substitution assays compared to naive unmasked structure-sequence blends.
- **Why:** Sharma & Gitter (arXiv:2504.16886, ICLR 2025) proved that structure-based inverse folding and 3D token models collapse severely in intrinsically disordered regions (IDRs) and flexible loops, where predicted AlphaFold conformations generate spurious, rigid physical contacts. In kbrain's Task #255 GNM structural dynamics audit, 130 of 217 assays failed a strict 95% structure confidence cutoff, leaving the dynamics evaluation underpowered. A position-resolved confidence mask allows exploiting high-confidence folded cores without suffering hallucinated penalties in disordered segments.
- **Data:** `pg.published_scores()` for SaProt-35M, ESM2-35M, and GEMME; per-residue pLDDT extracted from AlphaFold Database (AFDB) PDB structures.
- **Baseline:** Fixed unmasked 50/50 SaProt-35M + ESM2-35M rank blend (and GEMME alone).
- **Units:** Proteins (`by="protein"` across UniProt IDs with AFDB structures).
- **CPU:** < 2 minutes on 8 CPU cores (precomputed scores and cached pLDDT).

### C28. WT Pseudo-Perplexity Gating for Zero-Shot Model Routing (The Gordon-Abbeel Likelihood Prior)
- **Idea:** Evaluate whether wild-type sequence pseudo-perplexity (or average masked log-likelihood) under ESM2-35M provides an unsupervised, label-free ($N=0$) decision boundary to route between sequence PLMs (ESM2-35M / 650M) and MSA-based statistical physics (GEMME). Test whether wild-types with low pseudo-perplexity (high sequence likelihood) are routed to ESM2, while outlier/orphan proteins with high pseudo-perplexity (under-preferred sequences) are routed to GEMME.
- **Why:** Gordon, Lu, and Abbeel (ICLR 2025 / bioRxiv 2024, DOI: 10.1101/2024.10.03.616542) demonstrated that PLM zero-shot fitness prediction accuracy is dictated by the model's implicit preference for the wild-type sequence, exhibiting an inverted-U relationship where under-represented sequences experience severe performance degradation. Because GEMME builds a target-specific MSA directly from sequence databases and does not rely on a frozen pretraining distribution, it is immune to PLM pretraining corpus gaps. An unsupervised WT perplexity router requires zero labeled mutants and runs on CPU in minutes.
- **Data:** ProteinGym v1.3 substitution reference table (`pg.reference()`), published scores for GEMME and ESM2-35M / ESM2-650M.
- **Baseline:** Fixed 50/50 GEMME + ESM2 blend (and GEMME alone).
- **Units:** Proteins (`by="protein"` across 186 UniProt IDs) via `improvement_units()`.
- **CPU:** 2–3 minutes on 8 CPU cores (computing WT pseudo-perplexity on 186 sequences with ESM2-35M).

### C27. 3D Contact-Dense Residue Sensitivity Weighting (The Green SAE Causal Filter)
- **Idea:** Benchmark whether weighting or gating zero-shot PLM substitution scores by local 3D contact density (residues within 8 Å sphere around the mutation site in AlphaFold structures) improves Spearman rank correlation and top-$K$ enrichment over raw unweighted PLM scores across ProteinGym assays.
- **Why:** Mohanty et al. (Green Lab, bioRxiv 2026, DOI: 10.64898/2026.08.28.747907) proved using Sparse Autoencoders and causal activation patching on ESM-2 that the model's zero-shot mutation predictions are causally mediated by latent circuits that map directly to 3D physical contact networks. When a residue has few physical contacts (disordered loops / high solvent accessibility), PLM sequence log-odds are prone to hallucinating severe penalties that do not reflect true biophysical sensitivity. Modulating PLM scores by contact density tests whether this causal circuit insight can be operationalized training-free on CPU.
- **Data:** ProteinGym v1.3 substitution assays, precomputed ESM-2 / SaProt scores, and AlphaFold2 PDB backbones.
- **Baseline:** Raw unweighted ESM-2 (650M or 35M) zero-shot scores.
- **Units:** Proteins (`by="protein"` across UniProt IDs with AF2 structures).
- **CPU:** 2–3 minutes on 8 CPU cores.

### C26. Low-N (N=20) Zero-Shot Model Selector on ProteinGym (The PRIZM Protocol)
- **Idea:** Test whether an ultra-low-N sample of $N=20$ labeled variants (under both random and contiguous sampling) can reliably select the single best zero-shot model among {GEMME, ESM2-650M, SaProt-35M, EVE, Tranception} on each assay, compared to defaulting to GEMME alone or a fixed 50/50 blend. Evaluate on held-out variants across ProteinGym v1.3 substitution assays.
- **Why:** Harding-Larsen et al. (PRIZM, bioRxiv/Bioinformatics Advances 2026) demonstrated that evaluating zero-shot models on $N \approx 20$ variants successfully isolated top performers that delivered wet-lab enhancements on enzyme targets. In kbrain's prior finding (`findings/label-efficient-model-selection.md`), 24-label routing between GEMME and ESM2-650M beat GEMME (+0.016 held-out Spearman), but was tested only on a 2-model pair on random splits. Testing the PRIZM protocol across a 5-model candidate pool on both random and contiguous splits provides the definitive test of whether low-N hypothesis selection generalizes across diverse protein families.
- **Data:** ProteinGym v1.3 substitution reference table and precomputed zero-shot predictions (`data/proteingym/zero_shot/`).
- **Baseline:** GEMME alone (or fixed uniform ensemble).
- **Units:** Proteins (`by="protein"` across 186 UniProt IDs) via `improvement_units()`.
- **CPU:** 1–2 minutes on 8 CPU cores (analytical evaluation over precomputed scores).

### C25. Post-PLM Structural Steric & SASA Gating for Top-K Candidate Selection (VenusRAR CPU Filter)
- **Idea:** Simulate prospective directed evolution candidate selection (Top-$K$ with $K \in \{20, 50, 96\}$) from zero-shot foundation models (ESM2-650M, SaProt-35M, GEMME) with and without a training-free structural audit filter (rejecting mutations that introduce severe atomic van der Waals clashes $>0.4$ Å in AlphaFold2 backbones, or bury charged residues [Arg, Lys, Asp, Glu] in core positions where relative solvent accessibility $\text{RSA} < 0.05$). Measure whether structural auditing improves top-$K$ mean true experimental fitness and positive hit rate compared to raw unconstrained PLM ranking.
- **Why:** Liang et al. (VenusRAR, arXiv:2602.00197, Feb 2026) showed that zero-shot PLMs frequently assign high statistical likelihoods to mutations that violate elementary physical packing rules, and that an automated structural audit boosted Top-5 Hit Rate by up to 367% on ProteinGym-DMS99 while yielding 4- to 5-fold activity improvements on Cas12i3. We can validate this training-free hypothesis across ProteinGym assays with available AlphaFold coordinates on CPU in minutes.
- **Data:** ProteinGym v1.3 DMS substitution assays (`dms/`), AlphaFold2 PDB structures, and precomputed zero-shot model scores (`zero_shot/`).
- **Baseline:** Top-$K$ mean fitness of raw, unconstrained zero-shot PLM ranking (e.g. ESM2-650M or GEMME).
- **Units:** Proteins (`by="protein"` across UniProt IDs with AF2 structures).
- **CPU:** 2–3 minutes on 8 CPU cores using Biopython PDB contact and RSA routines.

### C24. Viable-Subspace Zero-Shot Collapse Auditor (The Woolley-Wilke Bimodality Test)
- **Idea:** Benchmark all primary zero-shot model classes (GEMME, ESM2-35M, SaProt-35M, ESM2-650M, EVE, Tranception) across the 217 ProteinGym substitution assays stratified into two subsets: (1) full assay (standard leaderboard Spearman), versus (2) viable variants only ($y \ge y_{\text{wt}}$ or top 50% fitness percentile). Quantify the magnitude of Spearman correlation collapse ($\Delta \rho_{\text{viable} - \text{full}}$) across model classes.
- **Why:** Woolley et al. (bioRxiv June/Oct 2026, DOI: 10.64898/2026.06.04.730121) proved that broad benchmark correlations are heavily inflated by the binary separation between functional and non-functional/unfolded variants (bimodal tails). For directed protein engineering, where engineers only select among viable variants to find functional gains, zero-shot models reportedly collapse towards $\rho \approx 0$. Testing this across our trusted evaluator will reveal which model classes (e.g., structure-aware vs Potts vs pure sequence PLMs) retain real functional ranking power among fit variants.
- **Data:** ProteinGym v1.3 substitution reference table and precomputed zero-shot predictions (`data/proteingym/zero_shot/`).
- **Baseline:** Full-assay Spearman correlation vs Viable-subspace Spearman correlation.
- **Units:** Proteins (`by="protein"` across 186 UniProt IDs) via `improvement_units()`.
- **CPU:** 1–2 minutes on 8 CPU cores (purely analytical ranking over existing precomputed scores).

### C23. Hard-Threshold MSA Resilience Gating vs. Uniform Ensembling
- **Idea:** Test a hard-threshold gating policy between GEMME and ESM2-650M conditioned on extreme alignment sparsity ($N_{\text{eff}} / L \le 1.0$ vs. $N_{\text{eff}} / L > 1.0$), evaluating whether strict unaligned sequence PLM routing exclusively on the 36 sparse ProteinGym assays outperforms an unconditional 50/50 uniform blend.
- **Why:** Arora et al. (PG-LLM, bioRxiv 2026) proved that unaligned parametric sequence representations maintain ranking power at low alignment depth where evolutionary/MSA methods collapse. In our previous finding (`findings/msa-depth-gated-routing.md`), a soft continuous depth gate failed because depth acted as a general difficulty proxy rather than a calibrated mixing weight. Testing a hard step-function focused strictly on the $N_{\text{eff}}/L \le 1.0$ boundary provides the clean falsification test for MSA-depth routing.
- **Data:** ProteinGym v1.3 substitution reference table and precomputed zero-shot predictions for GEMME and ESM2-650M (`pg.published_scores`).
- **Baseline:** Fixed 50/50 uniform blend of GEMME and ESM2-650M.
- **Units:** Proteins (`by="protein"` across 186 UniProt IDs) via `improvement_units()`.
- **CPU:** 1–2 minutes on 8 CPU cores.

### C22. Mutational Depth ($K$) Generalization Decay Profiler on ProteinGym Multi-Mutants
- **Idea:** Benchmark all primary model classes (GEMME, ESM2-35M, SaProt-35M, ESM2-650M, Tranception, FoldX) on the 69 ProteinGym multi-mutant assays stratified strictly by mutational edit distance ($K \in \{1, 2, 3, 4+\}$). Determine whether structure-informed representations (SaProt-35M) or co-evolutionary Potts terms (GEMME) decay slower than pure sequence PLM masked-marginals (ESM2) as mutational depth grows.
- **Why:** Schmirler et al. (DeePEn, bioRxiv 2026) and Kolchina et al. (bioRxiv 2026) demonstrated that zero-shot PLMs behave additively and degrade rapidly at higher edit distances. Determining which architecture best retains ranking correlation at $K \ge 3$ will identify the optimal foundation model for multi-site protein engineering.
- **Data:** ProteinGym v1.3 multi-mutant assays (`dms/`) and precomputed scores (`zero_shot/`).
- **Baseline:** ESM2-650M Spearman rank correlation stratified by edit distance $K$.
- **Units:** Assays or proteins across the 69 multi-mutant assays.
- **CPU:** ~3 minutes on 8 CPU cores.

### C21. Explicit Geometric Contact Density Residual for Zero-Shot Interface DMS Assays (CIR-DDG Residual)
- **Idea:** On the 13 ProteinGym binding assays and complex interface targets (e.g., SARS-CoV-2 RBD-ACE2, antibody-antigen interfaces), evaluate whether adding an explicit, training-free geometric contact density residual (coordination number within 8 Å, interface distance, relative solvent accessibility computed from PDB structures via Biopython) to frozen zero-shot PLM scores (ESM2-35M, SaProt-35M, GEMME) improves interface mutation Spearman correlation over raw scores.
- **Why:** Yu et al. (CIR-DDG, arXiv:2608.27530, Aug 2026) showed that zero-shot PLMs and structure models systematically drop critical interface contact geometry in their scalar predictions, and that adding 22 interpretable contact descriptors boosted absolute Spearman correlation by +0.026 to +0.081 on SARS-CoV-2 RBD interface mutations without any retraining.
- **Data:** ProteinGym v1.3 binding assays (`coarse_selection_type == 'Binding'`), PDB/AlphaFold structures, and precomputed zero-shot scores (`data/proteingym/zero_shot/`).
- **Baseline:** Raw published zero-shot scores (ESM2-35M, ESM2-650M, GEMME) alone.
- **Units:** Assays (13 binding assays).
- **CPU:** 1–2 minutes on 8 CPU cores using Biopython PDB contact parsing.

### C20. Historical Utility Prior for 24-Label Model Routing (AssayRouter for ProteinGym)
- **Idea:** Replace noisy support-set argmax correlation selection in Candidate C2 (24-label routing) with a meta-learned historical utility prior: train a cross-assay linear utility regressor across completed ProteinGym assays (leave-one-protein-out) that maps model support-set agreement, variance, and entropy to the held-out marginal utility of each frozen predictor (GEMME, ESM2-35M, SaProt-35M, ESM2-650M), selecting an optimal convex predictor combination on a new assay with $N=24$ support labels.
- **Why:** Xu et al. (AssayRouter, arXiv:2609.37285, Sep 2026) proved that when selecting among frozen predictors with $N \in [16, 64]$ labels, choosing the empirical best model on the support set (`Support-CV@1`) suffers from high selection variance and failure to generalize. Historical utility priors transferred across completed assays lowered negative log-likelihood by 0.0409 and stabilized model ensembling.
- **Data:** ProteinGym v1.3 substitution reference and precomputed scores (`pg.published_scores`).
- **Baseline:** Argmax support-set Spearman selection (Candidate C2 baseline) and fixed uniform ensemble.
- **Units:** Proteins (`by="protein"` across all 186 UniProt IDs).
- **CPU:** ~3 minutes on 8 CPU cores.

### C19. Orthogonal Feature Projection: Quantifying Pure Structural Variance in Small PLMs
- **Idea:** Orthogonally project out standard amino-acid physicochemical features (charge, hydropathy, volume, polarity from AAindex) from frozen ESM2-35M and SaProt-35M residue embeddings across all 217 ProteinGym substitution assays, evaluating how much of the zero-shot Spearman correlation remains.
- **Why:** Sarmiento et al. (arXiv:2608.25548, Aug 2026) demonstrated that a substantial fraction of apparent PLM prediction accuracy is attributable to linear projection of basic tabular amino acid properties rather than learned 3D structural context. Measuring the Spearman correlation of the residual orthogonal embedding $E_{orth} = (I - P_{AA})E$ tests whether small PLMs (ESM2-35M) retain genuine contextual fitness modeling capacity or collapse once basic physicochemical heuristics are subtracted.
- **Data:** ProteinGym v1.3 substitution assays (217 assays) and precomputed ESM2-35M / SaProt-35M embeddings.
- **Baseline:** Full unmodified PLM embeddings and simple AAindex tabular regression.
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 5–8 minutes on 8 CPU cores.

### C18. Exact Thermodynamic Anti-Symmetry Regularization in Low-N Stability Regression
- **Idea:** Benchmark an anti-symmetrized ridge regression estimator where forward and reverse mutations are jointly constrained ($y_{wt \to mut} = -y_{mut \to wt}$) using an anti-symmetric kernel formulation ($K_{anti}(x, x') = K(x, x') - K(x, -x')$) or paired inverse mutation data augmentation on the 64 biophysical stability DMS assays of ProteinGym under low-N regimes ($N \in \{24, 48, 96\}$).
- **Why:** Shivram et al. (arXiv:2606.08100, Jun 2026) proved that unconstrained PLM fitness heads suffer from severe forward-reverse thermodynamic bias, predicting unphysical directional preferences that degrade out-of-distribution generalization. On CPU, evaluating anti-symmetric kernel ridge costs virtually zero additional compute and enforces exact thermodynamic consistency without neural retraining.
- **Data:** ProteinGym v1.3 biophysical stability assays (MegaScale cDNA proteolysis subset) in `data/proteingym/dms/` with published zero-shot stability priors (DEEP-Boltz, ProSST, FoldX).
- **Baseline:** Standard unconstrained augmented ridge regression (C3) and frozen zero-shot stability priors alone.
- **Units:** assays or proteins via `improvement_units()`.
- **CPU:** 3–5 minutes on 8 CPU cores.

### C17. Composable Additive vs Epistatic Interaction Ridge in Multi-Mutant ProteinGym Assays
- **Idea:** Benchmark an explicit pairwise epistatic ridge regression model ($y = w_0 + \sum_i w_i x_i + \sum_{i < j} J_{ij} x_i x_j$) against a purely additive augmented ridge model ($y = w_0 + \sum_i w_i x_i + w_{prior} \cdot \text{Prior}$) across ProteinGym combinatorial multi-mutant DMS assays at $N \in \{48, 96, 192\}$ under held-out cross-validation folds.
- **Why:** Cerebra-Epistasis (Wang et al., bioRxiv Sep 2026) showed that zero-shot PLMs decay sharply at mutation depth $\ge 3$ because standard sequence models assume additive log-odds, missing epistatic sign inversions and cooperative stability effects. Furthermore, kbrain's skeptic verified that low-N augmented ridge gains at $N=48$ were concentrated entirely in multi-mutants and null on single substitutions. Testing whether parameterizing explicit pairwise coupling terms ($J_{ij}$) reliably beats additive ridge isolates whether low-N supervised advantage in directed evolution is driven by local epistatic contact learning.
- **Data:** ProteinGym multi-mutant DMS assays (GB1, beta-lactamase, fluorescent proteins, etc. in `data/proteingym/dms/`) and zero-shot priors from `pg.published_scores`.
- **Baseline:** Pure additive augmented ridge (C3) and frozen zero-shot priors alone.
- **Units:** assays or proteins via `improvement_units()`.
- **CPU:** 5–10 minutes on 8 CPU cores (regularized closed-form pairwise ridge regression or low-rank kernel ridge).

### C16. Training-Free Position-Adaptive Logit Fusion (VenusREM-style) on CPU Using Published Scores
- **Idea:** Benchmark a position-adaptive logit fusion scheme that dynamically weights evolutionary MSA log-odds (GEMME, Site-Independent) and sequence/structure PLM log-odds (ESM2-35M, SaProt-35M) based on local position conservation entropy, comparing against unconditional rank blending (C1) and the best single model across all 217 ProteinGym substitution assays.
- **Why:** VenusREM2 (Tan et al., arXiv:2609.34654, Sep 2026) attained the highest recorded Spearman correlation on ProteinGym (0.556) using training-free retrieval logit fusion. While kbrain's assay-level MSA-depth gate failed because assay-level depth was too coarse (finding in `findings/msa-depth-gated-routing.md`), VenusREM demonstrates that *position-level* confidence weighting (giving high weight to MSA conservation at deeply conserved sites, but defaulting to PLM priors at variable, poorly-aligned loops) is the true mathematical driver of retrieval gains. Because per-mutant published scores for GEMME, Site-Independent, and ESM2 already exist in `pg.published_scores`, this hypothesis can be tested in minutes entirely on CPU.
- **Data:** ProteinGym v1.3 single-substitution assays with published scores for GEMME, ESM2-35M, ESM2-650M, Site-Independent, and SaProt-35M.
- **Baseline:** Unconditional static 50/50 blend and the best single model (GEMME).
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 3–5 minutes on 8 CPU cores (vectorized NumPy array operations on precomputed score tables).

### C15. Tabular In-Context Learning (TabPFN) vs Ridge Regression in Low-N Regimes on Contiguous Splits
- **Idea:** Benchmark TabPFN (an in-context transformer foundation model pretrained on synthetic causal graphs that generates Bayesian posterior predictions without gradient descent) against closed-form Ridge regression and frozen zero-shot priors at $N \in \{24, 48, 96\}$ on ProteinGym single-substitution assays under `fold_contiguous_5` (position-disjoint test mutants). Inputs are frozen zero-shot scores (GEMME, ESM2-35M) combined with one-hot indicators or PLS-reduced embedding deltas.
- **Why:** Guan et al. (arXiv:2606.31126, Jun 2026) showed that TabPFN in-context learning paired with PLM representations matches or exceeds task-specific supervised regressors on ProteinGym. Standard regression models suffer from hyperparameter overfitting when $N \le 48$. Because TabPFN evaluates the dataset context in a single forward pass on CPU using an internal causal prior, it may prevent severe weight explosion on unseen structural positions.
- **Data:** ProteinGym v1.3 single-substitution assays with `fold_contiguous_5` in `data/proteingym/dms/` and `pg.published_scores`.
- **Baseline:** Frozen zero-shot GEMME / ESM2-35M scores alone and standard Ridge regression.
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 5–10 minutes on 8 CPU cores (TabPFN CPU inference on small $N \le 96$ tables).

### C14. CPU-Computable Gaussian Network Model (GNM) Dynamics as an Orthogonal Prior to Sequence PLMs
- **Idea:** Compute analytical residue flexibility profiles (mean-square fluctuations / B-factors) from AlphaFold2 predicted C-alpha coordinates using the Gaussian Network Model (GNM; Kirchhoff contact Laplacian decomposition), and evaluate whether scaling zero-shot PLM/GEMME log-odds by GNM flexibility improves Spearman correlation over unweighted scores across ProteinGym substitution assays.
- **Why:** Cho (arXiv:2604.12026, Apr 2026, TriFit) demonstrated that conformational dynamics provides the single largest marginal gain over sequence and static structure in variant effect prediction (AUROC 0.897). Unlike heavy molecular dynamics simulations, GNM normal mode analysis requires only an $L \times L$ Kirchhoff contact matrix inversion, executing analytically in <0.1 seconds per protein on an 8-core CPU. If dynamic rigidity penalizes mutations at functionally sensitive sites that sequence models miss, GNM provides an entirely GPU-free physical prior.
- **Data:** AlphaFold2 C-alpha coordinates for 186 ProteinGym UniProt targets; published zero-shot GEMME and ESM2-35M scores from `pg.published_scores`.
- **Baseline:** Published unweighted GEMME and ESM2-35M scores.
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 2–5 minutes on 8 CPU cores (analytical GNM Laplacian eigensolver in SciPy).

### C13. Site-Mean Fitness Baseline vs Supervised Models Across Random and Contiguous Splits
- **Idea:** Benchmark an explicit "Site-Mean Predictor" (predicting the empirical mean fitness of observed mutations at residue position $i$, falling back to the training global mean for unseen positions) across ProteinGym v1.3 single-substitution assays under both `fold_random_5` and `fold_contiguous_5` at $N \in \{24, 48, 96\}$, and compare against:
  (1) Frozen zero-shot GEMME and ESM2-35M priors.
  (2) Pure empirical one-hot ridge regression.
  (3) Zero-shot augmented ridge regression (Hsu et al. 2022).
- **Why:** Vieira, Lin, & Wilke (bioRxiv Mar 2026) demonstrated that a simple site-mean model matches or outperforms complex supervised PLMs across numerous DMS assays under random splits because random splits permit extensive position-variance leakage. kbrain's skeptic verified that augmented ridge gains at $N=48$ were concentrated in multi-mutants and null on single substitutions. Measuring the Site-Mean Predictor directly establishes a decisive negative control: it quantifies exactly how much apparent supervised gain is trivial position tolerance memorization (which collapses to zero under `fold_contiguous_5`) vs transferable mutational biophysics.
- **Data:** ProteinGym v1.3 single-substitution assays with `fold_random_5` and `fold_contiguous_5` in `data/proteingym/dms/` and `pg.published_scores`.
- **Baseline:** Frozen zero-shot GEMME / ESM2-35M and pure Site-Mean Predictor.
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 3–5 minutes on 8 CPU cores (closed-form group means and scikit-learn Ridge).

### C12. Inference-Time Monte Carlo Dropout on CPU PLMs (ESM2-35M / 8M)
- **Idea:** Inject an inference-only stochastic dropout layer ($p=0.1$, $K=10$ stochastic forward passes) between the embedding layer and transformer blocks of CPU-runnable ESM2-35M (or ESM2-8M), compute the Monte Carlo average marginal log-odds across passes ($\bar{s}(x) = \frac{1}{K}\sum_{k=1}^K \log \frac{P_k(x_{mut})}{P_k(x_{wt})}$), and evaluate whether this test-time stochastic ensemble beats deterministic single-pass ESM2-35M across ProteinGym DMS substitution assays.
- **Why:** Ravuri & Lawrence (arXiv:2506.14793, Jun 2025) demonstrated that test-time dropout boosts zero-shot Spearman correlations by up to ~22% for small PLMs (8M and 35M parameters) without any fine-tuning or retraining. If marginalizing over representation uncertainty via 10 CPU passes yields a statistically significant positive bootstrap CI over deterministic ESM2-35M on ProteinGym, it delivers a CPU-native accuracy upgrade that narrows the gap to 650M GPU models at zero hardware spend.
- **Data:** ProteinGym v1.3 single-substitution assays; ESM2-35M PyTorch weights executed on CPU.
- **Baseline:** Published deterministic ESM2-35M scores (`pg.published_scores(aid, "ESM2 (35M)")`).
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 15–30 minutes on 8 CPU cores (10 fast PyTorch CPU forward passes per wild-type sequence).

### C11. Subspace Projection vs One-Hot Ridge in Low-N Regimes (N=24, 48) on Contiguous Folds
- **Idea:** Compare two CPU-tractable feature representations for low-N fitness prediction under `fold_contiguous_5` (position-disjoint test mutants):
  (1) Standard one-hot amino acid indicators + frozen zero-shot prior (augmented ridge baseline from C3).
  (2) Low-dimensional Partial Least Squares (PLS) or PCA projection (5–10 components) of ESM2-35M residue embedding deltas ($\Delta z = z_{\text{mut}} - z_{\text{wt}}$) + zero-shot prior.
- **Why:** The Linear Fitness Subspace hypothesis (Ma et al., arXiv:2610.07607, Oct 2026) posits that mutation-induced embedding deltas $\Delta z$ compress functional variation into a compact linear subspace accessible with few labels ($N \le 48$). On position-disjoint splits (`fold_contiguous_5`), standard one-hot features completely fail because test positions were never seen during training (their weights remain zero). In contrast, continuous PLM embedding deltas encode biochemical and spatial relationships across all positions. Testing whether subspace projection enables generalization across unseen positions directly tests if PLM embeddings can unlock position-extrapolative low-N engineering on CPU.
- **Data:** ProteinGym v1.3 single-substitution assays with `fold_contiguous_5` in `data/proteingym/dms/` and `pg.published_scores`.
- **Baseline:** Frozen zero-shot GEMME / ESM2-35M scores alone and one-hot augmented ridge.
- **Units:** proteins (186 UniProt IDs) via `improvement_units(by="protein")`.
- **CPU:** 5–10 minutes on 8 CPU cores (closed-form scikit-learn `PLSRegression` / `PCA` + `Ridge` on ESM2-35M embedding deltas across 5 folds).

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
