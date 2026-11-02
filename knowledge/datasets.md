# Datasets for Protein Mutation-Effect Prediction

_A comprehensive guide to experimental and computational datasets for variant effect prediction, fitness landscapes, biophysical stability, and clinical pathogenicity._

Last updated: 2026-11-01 (Scout shift). Grounded in the ProteinGym v1.3 benchmark, MaveDB, MegaScale, and the peer-reviewed DMS literature.

---

## 1. Executive Summary & Data Landscape

Predicting how amino-acid substitutions alter protein function requires distinct types of experimental ground truth. The literature spans four primary dataset classes:

```
+----------------------------------------------------------------------------------------------------+
|                                 VARIANT EFFECT DATASET CLASSES                                     |
+------------------------------------+-----------------------------------+---------------------------+
| Class                              | Experimental Readout              | Primary Benchmarks        |
+------------------------------------+-----------------------------------+---------------------------+
| 1. Deep Mutational Scanning (DMS)  | Cellular fitness, growth rate,    | ProteinGym v1.3 (DMS),    |
|                                    | display binding, FACS enrichment  | MaveDB                    |
+------------------------------------+-----------------------------------+---------------------------+
| 2. Biophysical Stability           | Direct free energy of unfolding   | MegaScale,                |
|                                    | (ΔΔG in kcal/mol), Tm, proteolysis| FireProtDB, ProThermDB    |
+------------------------------------+-----------------------------------+---------------------------+
| 3. Supervised Generalization       | Split benchmarks testing distance | FLIP, FLIP-2,             |
|                                    | extrapolation and low-N fitness   | ProteinGym CV folds       |
+------------------------------------+-----------------------------------+---------------------------+
| 4. Clinical Pathogenicity          | Organismal disease association,   | ProteinGym Clinical,      |
|                                    | human penetrance, population MAF  | ClinVar, gnomAD           |
+------------------------------------+-----------------------------------+---------------------------+
```

### Critical Axiom for kbrain:
Not all "fitness" is the same physical quantity:
- **DMS fitness** is a composite non-linear readout conflating expression, folding stability, catalytic turnover, and host cellular toxicity.
- **Biophysical stability ($\Delta\Delta G$)** is a pure thermodynamic property. A mutation can severely destabilize a protein ($\Delta\Delta G > 3\text{ kcal/mol}$) while retaining wild-type cellular fitness if expression exceeds a stability threshold; conversely, an active-site mutation can completely ablate function while having $\Delta\Delta G \approx 0$.
- **Clinical pathogenicity** reflects organismal phenotype in a diploid genome over decades, subject to genetic background, expression dosage, and evolutionary buffering.

---

## 2. ProteinGym v1.3: The Canonical Benchmark Suite

**ProteinGym** (Notin et al., NeurIPS 2023; [proteingym.org](https://proteingym.org)) is kbrain's primary benchmark and the undisputed gold standard for evaluating variant effect predictors.

### 2.1 DMS Substitutions Benchmark (The Lab Standard)
Evaluated strictly via `lab/proteingym.py`:
- **Assays:** 217 distinct deep mutational scanning assays.
- **Unique Target Proteins:** 186 UniProt IDs.
- **Total Mutants:** 2,465,767.
- **Single Substitutions:** 696,311 mutants across all 217 assays.
- **Multiple Substitutions:** 1,769,456 mutants across 69 assays (up to 7 substitutions per mutant).
- **Assays with Singles Only:** 148 assays.
- **Assays with Multiples:** 69 assays.

#### Taxonomic Distribution
| Taxon | Assays | Percentage | Key Exemplars |
|---|---|---|---|
| **Human** | 96 | 44.2% | TP53, BRCA1, PTEN, VKOR1, MSH2, CBS, CCR5 |
| **Prokaryote** | 50 | 23.0% | Beta-lactamase (bla), ParE3, GyrA, TEM-1 |
| **Eukaryote (Non-human)** | 40 | 18.4% | Yeast (GAL4, URA3), GFP, Spike (SARS-CoV-2) |
| **Virus** | 31 | 14.3% | Influenza HA/NA, HIV Env, Polio VP1 |

#### Coarse Selection Categories
| Functional Category | Assays | Percentage | Description / Experimental Mechanism |
|---|---|---|---|
| **OrganismalFitness** | 77 | 35.5% | Cell growth, competitive proliferation, viral replication |
| **Stability** | 66 | 30.4% | cDNA display proteolysis, VAMP-seq, cellular abundance |
| **Activity** | 43 | 19.8% | Enzymatic turnover, antibiotic resistance, transcription |
| **Expression** | 18 | 8.3% | Surface display level, GFP reporter fluorescence |
| **Binding** | 13 | 6.0% | Phage/yeast display affinity to antibody, receptor, or ligand |

#### Evolutionary Alignment Depth ($N_{\text{eff}} / L$)
Alignment depth ($N_{\text{eff}}$: number of non-redundant sequences divided by sequence length $L$) dictates whether MSA-based methods dominate PLMs:
- **Low ($N_{\text{eff}}/L \le 1$):** 36 assays (16.6%). Alignment is sparse. PLMs (ESM-2, ESM-C) often outperform classical MSA models.
- **Medium ($1 < N_{\text{eff}}/L \le 10$):** 109 assays (50.2%). Typical enzyme and viral targets.
- **High ($N_{\text{eff}}/L > 10$):** 72 assays (33.2%). Ancient, highly conserved protein families (kinases, globins). GEMME, EVmutation, and EVE dominate here.

### 2.2 Low-N and Supervised Cross-Validation Folds
ProteinGym single-substitution assays include three standardized 5-fold cross-validation schemes:

1. **`fold_random_5` (Uniform Random Split):**
   - Mutants are partitioned uniformly at random into 5 folds.
   - **Warning (Leakage Trap):** Other mutations at the exact same residue position appear in the training set. Models easily learn per-position tolerance rather than substitution biophysics.
2. **`fold_modulo_5` (Position Modulo Split):**
   - Partitioned by residue index modulo 5 ($pos \pmod 5$).
   - Positions are interleaved uniformly throughout the primary sequence.
3. **`fold_contiguous_5` (Contiguous Structural Block Split):**
   - Sequence is divided into 5 contiguous linear blocks ($pos \in [L_k, L_{k+1}]$).
   - Test positions are completely unseen during training.
   - **The Honest Generalization Test:** Tests whether an algorithm can generalize to uncharacterized regions of a protein.

### 2.3 ProteinGym Indels Benchmark
- **Assays:** 35 deep mutational scanning assays.
- **Total Mutants:** 412,410 insertion and deletion variants.
- **Significance:** Insertions and deletions shift sequence coordinates and alter length. Fixed-length PLM masked marginal scoring breaks on indels; scoring requires autoregressive generation (e.g. Progen2, Tranception) or profile hidden Markov models.

### 2.4 ProteinGym Clinical Benchmark
- **Scope:** Zero-shot pathogenicity prediction for human missense variants.
- **Coverage:** 2,484 clinically relevant human genes.
- **Labels:** ClinVar pathogenic/likely pathogenic vs. benign/likely benign, augmented by gnomAD common neutral variants.
- **Evaluation Metric:** Area Under the ROC Curve (AUC) and Area Under the Precision-Recall Curve (AUPRC), evaluated per gene and aggregated across disease categories.

---

## 3. MaveDB: The Primary Multiplexed Assay Repository

**MaveDB** ([mavedb.org](https://www.mavedb.org); Esposito et al., *Nat Genet* 2019; Rubin et al., *Genome Biol* 2024):
- **Role:** The community-curated, open-access repository developed by the Atlas of Variant Effects (AVE) Alliance.
- **Accession Format:** Universal Resource Names: `urn:mavedb:00000001-a-1`.
- **Scale:** Over 400 published experiments covering human, model organism, viral, and synthetic proteins.
- **Data Layers:**
  1. **Raw Counts:** High-throughput sequencing read counts per variant across experimental time points, replicates, and sorting gates.
  2. **Processed Scores:** Log-enrichment ratios calculated via statistical pipelines like **Enrich2**, **DiMSum**, or **DESeq2**.
  3. **Metadata Schema:** MIAPAR standard (Minimum Information About a Protein Assay Readout) capturing target sequence, UniProt ID, selection agent, library generation method, and sequencing platform.

---

## 4. MegaScale: High-Throughput Biophysical Stability

**MegaScale** (Tsuboyama et al., *Nature* 2023, [DOI: 10.1038/s41586-023-06240-5](https://doi.org/10.1038/s41586-023-06240-5)):
- **What:** Quantitative cDNA display proteolysis measuring direct thermodynamic folding stability ($\Delta G$ and $\Delta\Delta G$ in kcal/mol).
- **Scale:** 776,000 mutations across 359 natural and de novo designed protein domains (lengths 40–120 residues).
- **Why it matters:**
  - Unlike cell-growth DMS, MegaScale measures an intrinsic thermodynamic property independent of cellular expression or metabolic networks.
  - Features reversible two-state folding transitions for hundreds of diverse folds (alpha-helical bundles, beta-barrels, mixed folds).
  - Demonstrates that inverse-folding models (e.g. ProteinMPNN) correlate moderately with $\Delta\Delta G$ ($\rho \approx 0.45$), but struggle to predict non-additive multi-mutation destabilization.

---

## 5. FLIP / FLIP-2: Supervised Fitness Landscapes

**FLIP** (Functional Landscapes of Induced Patches; Dallago et al., *NeurIPS Datasets & Benchmarks* 2021; Wittmann et al., 2024):
- **Role:** Standardized benchmark for evaluating supervised representation learning on protein fitness landscapes.
- **Core Datasets:**
  - **GB1** (Protein G domain B1; Wu et al. 2016): 4-position combinatorial landscape (149,361 sequences out of 160,000 possible variants). Gold standard for epistasis and combinatorial navigation.
  - **AAV2** (Adeno-Associated Virus capsid; Bryant et al. 2021): Viability and packaging fitness across single and multiple substitutions.
  - **GFP** (Green Fluorescent Protein; Sarkisyan et al. 2016): Fluorescence intensity across 50,000+ local mutants up to 15 substitutions away from wild-type.
  - **Meltome Atlas** (Jarzab et al. 2020): In vivo melting temperatures across 48 species.
- **Split Regimes:** Specifically constructed to evaluate out-of-distribution generalization:
  - *Sample size scaling:* $N \in [24, 96, 384, 1536]$.
  - *Mutational distance shift:* Train on 1-mutant sequences; test on 2+ mutant sequences.
  - *Low vs. High sequence similarity:* Train on sequence clusters $\le 40\%$ identity to test set.

### 5.1 TadA-Bench: Million-Variant Campaign-Chronology Directed Evolution Benchmark

**TadA-Bench** (Gao et al., arXiv:2606.02624, May 2026; [arXiv:2606.02624](https://arxiv.org/abs/2606.02624)):
- **What:** A high-throughput wet-lab replay benchmark tracking 31 consecutive directed evolution rounds of tRNA adenosine deaminase (TadA), encompassing over 1,000,000 variants. Released with multi-modal views (aligned DNA, RNA, protein) and unified cross-round fitness labels via `Seq2Graph`.
- **Role in Protein Engineering:** Unlike static single-round DMS screens, directed evolution proceeds iteratively where each round samples variants conditioned on previous winners. TadA-Bench formalizes a fixed-data temporal replay challenge: models are trained on variants up to round $t$ and evaluated on their ability to rank variants that were actually screened in future round $t+1$.
- **Rigor Insight & Split Illusion:** Random cross-validation splits show artificially inflated interpolation performance ($\rho > 0.70$). However, when evaluated on prospective future-round candidate ranking, model performance plunges ($\rho < 0.25$). Evolutionary sequence coverage, rather than local data point density, governs prospective discovery success.

### 5.2 DeePEn: Depth-Sensitive Benchmark for Protein Engineering

**DeePEn** (Schmirler et al., bioRxiv, June 2026; [bioRxiv preprint](https://doi.org/10.1101/2026.06.18.660142)):
- **What:** A standardized benchmark suite built by extracting multi-mutational trajectories across ProteinGym deep mutational scanning datasets to evaluate fitness prediction models as a function of **mutational edit distance ($K$)** from wild-type.
- **Why it matters:** Most benchmarks evaluate aggregate Spearman correlation heavily dominated by single amino-acid substitutions ($K=1$). Real-world protein engineering campaigns require introducing 3–6 simultaneous mutations to achieve targeted shifts in catalytic activity, thermal stability, or binding selectivity.
- **Key Empirical Finding:** Unsupervised PLMs and supervised neural regressors exhibit steep monotonic performance decay as mutational distance increases. At $K \ge 3$, zero-shot model rank correlation drops by 40–70% compared to $K=1$, driven by unmodeled higher-order epistatic interactions and distribution shift. DeePEn establishes mutational distance stratification as an essential reporting requirement.

### 5.3 Intrinsic Dataset Determinants of PLM Fitness Prediction

**Dataset Dynamics** (Vieira, Lin, & Wilke, bioRxiv, March 2026; [DOI: 10.64898/2026.03.08.710389](https://doi.org/10.64898/2026.03.08.710389)):
- **What:** Systematic empirical dissection of supervised transfer learning using PLM embeddings across viral vs. cellular DMS assays from ProteinGym.
- **Why it matters:** PLM performance varies wildly across the 217 ProteinGym assays (Spearman ranging from $< 0.15$ to $> 0.85$). Vieira et al. identify the intrinsic dataset features that account for this variance:
  1. **Viral vs. Cellular Regimes:** PLMs systematically underperform on viral surface proteins (e.g., HIV Env, Influenza HA, SARS-CoV-2 Spike) relative to conserved cellular enzymes. Viral targets experience active immune selection and structural plasticity, violating the neutral evolutionary drift assumptions embedded in UniRef-trained PLMs.
  2. **Assay Dynamic Range & Non-Linearity:** Assays with severe selection bottlenecks or binary viability cutoffs penalize rank-order correlation compared to quantitative continuous fluorescence or kinetic readouts.
  3. **Site Conservation Variance:** Datasets with uniform residue conservation offer poor discriminative signal for PLMs compared to assays with sharp contrasts between catalytic cores and flexible loops.

---

## 6. Clinical & Population Variation Repositories

### 6.1 ClinVar (NCBI)
- **Access:** [ncbi.nlm.nih.gov/clinvar](https://www.ncbi.nlm.nih.gov/clinvar)
- **Contents:** Human genomic variations mapped to medical phenotypes with review status (1-star to 4-star expert consensus).
- **Five-tier classification:** Pathogenic, Likely Pathogenic, Variant of Uncertain Significance (VUS), Likely Benign, Benign.
- **Evaluation caution:** Over 50% of submitted missense variants remain classified as VUS. Training models on uncurated ClinVar sets introduces high label noise from misclassified private variants.

### 6.2 gnomAD (Genome Aggregation Database)
- **Access:** [gnomad.broadinstitute.org](https://gnomad.broadinstitute.org)
- **Contents:** Whole-genome and exome sequencing from >700,000 diverse individuals.
- **Application in mutation prediction:** Common missense variants (e.g., Minor Allele Frequency $\text{MAF} > 0.001$) in outbred populations are assumed to be benign/tolerated under negative selection, serving as high-confidence negative controls.

---

## 7. Homology, Structure & Alignment Infrastructure

Zero-shot and structure-aware predictors depend on underlying sequence and structural databases:

1. **UniRef (UniProt Reference Clusters):**
   - **UniRef50 / UniRef90 / UniRef100:** Clustered sequence sets at 50%, 90%, and 100% identity. ESM-1v and ESM-2 are trained on UniRef50/90 to minimize over-representation of model organisms.
2. **ColabFold / MMseqs2 Environmental MSAs:**
   - Deep alignments generated from BFD (Big Fantastic Database), MGnify metagenomics, and UniRef30. These provide the sequence diversity required for GEMME, EVmutation, and EVE to infer co-evolutionary couplings.
3. **AlphaFold Protein Structure Database (AlphaFold DB):**
   - >200 million predicted structures. Used by structure-informed models (ProSST, SaProt, ESCOTT) to supply 3D coordinates when experimental PDB structures are unavailable.

---

## 8. Data Leakage Traps & Empirical Realities

| Data Leakage / Confounding Trap | Mechanism of Failure | Strict Prevention Rule |
|---|---|---|
| **Positional Tolerance Leakage** | In uniform random CV (`fold_random_5`), training on 10 substitutions at position 42 allows the model to learn that position 42 is intolerant to any substitution. Test scores look high, but the model learned residue importance, not amino-acid chemistry. | Evaluate supervised models strictly on `fold_contiguous_5` or enforce position-disjoint splits. |
| **Pre-Training Contamination** | Large PLMs trained on UniRef50 have observed wild-type sequences and close homologs. Models performing retrieval (e.g. RAG, KNN) can retrieve identical training targets. | Standardize zero-shot evaluations across all 217 assays without target-specific fine-tuning; verify retrieval databases exclude wild-type and query homologs. |
| **Holo vs. Apo Structural Leakage** | Using experimental PDB structures crystallized with co-factors or drug ligands leaks active-site coordinates to inverse-folding models that would not be present in apo structures. | Standardize structural inputs on predicted AlphaFold2 coordinates to ensure unbiased apo backbones. |
| **DMS Assay Saturation & Non-Linearity** | In cellular growth selections, high-activity mutants plateau once growth rate reaches maximum doubling time; low-activity mutants drop below detection threshold (sequencing zero-floor). | Use monotonic rank correlation (Spearman $\rho$), never linear Pearson $r$, when evaluating DMS scores. |
| **Protein-Level Non-Independence** | ProteinGym's 217 assays cover 186 UniProt IDs; multiple assays measure the same protein under different conditions. Treating all 217 assays as independent underestimates variance. | Resample independent units by clustering on UniProt ID (`by="protein"` in `improvement_units`) with bootstrap confidence intervals. |
| **Viability Bimodality & Deleterious Tail Inflation** | Deep mutational scanning assays typically exhibit bimodal fitness distributions: a large cluster of non-viable/unfolded variants with strongly negative scores, and a narrower distribution of functional/near-WT variants. High aggregate Spearman $\rho$ is often driven entirely by separating dead from alive mutants, masking a total failure to rank among viable variants ([Woolley et al., bioRxiv 2026](https://doi.org/10.64898/2026.06.04.730121)). | Report stratified rank correlations for the viable stratum ($y \ge y_{\text{wt}}$ or top 50%) alongside global Spearman $\rho$ to audit fine-grained functional ranking power. |

### 8.1 The Viable-Subspace Evaluation Criterion (Woolley-Wilke Precedent)
In applied protein engineering and directed evolution, experimentalists do not need an algorithm to distinguish between a functional enzyme and an unfolded null mutant; simple viability filters or laboratory selection assays already accomplish this. The critical engineering challenge is **ranking among viable variants** ($y \ge y_{\text{wt}}$) to identify mutations that improve activity, thermostability, or binding affinity. 

Woolley et al. (bioRxiv June/Oct 2026) demonstrated that:
1. Aggregate ProteinGym Spearman correlations give an overly optimistic picture of zero-shot utility because predicting catastrophic loss-of-function is easy for evolutionary models.
2. When evaluated strictly within the subset of viable mutants, rank correlations for leading foundation models (ESM-2, ESM-1v, Tranception) collapse toward zero ($\rho \approx 0.05 \pm 0.10$).
3. On "new-to-nature" phenotypes where natural selection has not operated, zero-shot evolutionary log-odds correlate negligibly or negatively with experimental enhancements.

Therefore, robust evaluation of variant effect models must include stratified viable-subspace diagnostics.

---

## 9. Computational Edge for kbrain (8 CPU Cores / No GPU)

Given our hardware boundary, we exploit pre-computed and analytical resources:
1. **Pre-computed ProteinGym v1.3 scores:** `data/proteingym/zero_shot/` houses mutant-level predictions for ~100 models, allowing instant evaluation of new ensembling, gating, and calibration hypotheses.
2. **Fast tabular low-N regression:** Closed-form ridge regression, Gaussian processes, and empirical Bayes positional shrinkage run in milliseconds per assay.
3. **Analytical MSA models:** GEMME runs on CPU in minutes from pre-aligned MSAs, bypassing deep learning inference while delivering state-of-the-art accuracy.
