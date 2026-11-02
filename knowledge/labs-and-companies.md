# Labs and Companies in Protein Mutation-Effect Prediction

_A comprehensive landscape analysis of academic research laboratories, foundation model consortia, tech giants, and commercial biotechs driving variant effect prediction, deep mutational scanning (DMS), and machine-learning-guided protein engineering._

Last updated: 2026-11-01 (Scout shift). Grounded in the ProteinGym v1.3 benchmark, published model weights, and peer-reviewed literature.

---

## 1. Executive Summary & Ecosystem Topology

The field of protein mutation-effect prediction sits at the convergence of evolutionary biology, structural biophysics, and machine learning. Over the past five years, the ecosystem has bifurcated into:
1. **Academic and Open-Science Hubs:** Creators of foundational benchmarks (ProteinGym, MaveDB), biophysical measurement technologies (deep mutational scanning, VAMP-seq), and open evolutionary models (GEMME, EVE, VESPA).
2. **AI Foundation Model Consortia & Tech Spin-Offs:** Groups training massive self-supervised sequence and multimodal models (Meta FAIR, EvolutionaryScale, Google DeepMind, GenBio.ai).
3. **Structure-Aware & Hybrid Innovators:** Academic groups fusing structural alphabets, AlphaFold backbones, and retrieval-augmented generation (Westlake University, Fred Hutch, Sorbonne).
4. **Commercial Protein Engineering Platforms:** Venture-backed biotechs utilizing variant effect prediction and low-N active learning loops to design therapeutic antibodies, industrial enzymes, and synthetic cytokines (Cradle Bio, Generate:Biomedicines, Nabla Bio, Adaptyv Bio).

```
+---------------------------------------------------------------------------------------------------------+
|                                    ECOSYSTEM TOPOLOGY & STRATEGIC QUADRANTS                             |
+---------------------------------------------------+-----------------------------------------------------+
| ACADEMIC & OPEN SCIENCE HUBS                      | FOUNDATION MODEL CONSORTIA                          |
| - Marks Lab (Harvard) / OATML (Oxford)            | - EvolutionaryScale (ESM-3, ESM-C)                  |
| - Fowler & Starita Labs (UW / MaveDB)             | - Meta FAIR (ESM-1v, ESM-2, ESM-IF1, MSA Trans.)    |
| - LCQB / Sorbonne (GEMME, JET2+)                  | - Google DeepMind / Isomorphic (AlphaFold, AM)       |
| - Rost Lab (TUM) (VESPA, VespaG, ProtTrans)       | - GenBio.ai (AIDO Protein-RAG)                      |
| - Baker Lab / IPD (UW) (ProteinMPNN, Rosetta)     |                                                     |
+---------------------------------------------------+-----------------------------------------------------+
| STRUCTURE-AWARE & RETRIEVAL INNOVATORS            | COMMERCIAL PROTEIN DESIGN & WET-LABS                |
| - Westlake University (SaProt, ProSST, VenusREM)  | - Cradle Bio (Low-N active learning platform)       |
| - Bepler Lab (Fred Hutch) / Berger Lab (PoET)     | - Generate:Biomedicines (Chroma, de novo proteins)  |
| - Fraser & Kortemme Labs (UCSF) (Ensembles/DMS)   | - Nabla Bio (High-throughput antibody fitness)      |
| - Whitehead Lab (CU Boulder) (Enzyme DMS)         | - Adaptyv Bio (Robotic screening biofoundry)        |
|                                                   | - Basecamp Research (Environmental metagenomics)    |
+---------------------------------------------------+-----------------------------------------------------+
```

---

## 2. Premier Academic Research Laboratories

### 2.1 Marks Lab (Harvard Medical School) & OATML (Oxford)
- **Principal Investigators:** Debora Marks (Harvard Systems Biology) & Yarin Gal (Oxford Applied Technologies in Machine Learning).
- **Key Contributions:**
  - **ProteinGym** (Notin et al., NeurIPS 2023): The definitive 217-assay DMS and clinical benchmark suite.
  - **EVmutation** (Hopf et al., Nat Biotechnol 2017): Direct coupling analysis (Potts model) capturing pairwise epistatic couplings.
  - **EVE** (Frazer et al., Nature 2021): Bayesian Variational Autoencoder trained on MSA alignments for clinical variant pathogenicity.
  - **Tranception & TranceptEVE** (Notin et al., ICML 2022): Autoregressive transformer with retrieval and hybrid evolutionary ensembling.
- **Relevance to kbrain:** Marks Lab defines the benchmark we score against. Their work proves that evolutionary conservation and epistatic constraints are indispensable for variant effect prediction.
- **Open Science Stance:** Exemplary. Code, model checkpoints, alignment pipelines, and precomputed score tables are fully open (CC-BY 4.0 / MIT).

### 2.2 Fowler Lab & Starita Lab (University of Washington, Genome Sciences)
- **Principal Investigators:** Douglas M. Fowler & Lea M. Starita.
- **Key Contributions:**
  - **Deep Mutational Scanning (DMS)**: Co-invented high-throughput functional multiplex assays combining FACS/selection with deep sequencing (Fowler & Fields, Nat Methods 2014).
  - **MaveDB** (Rubin et al., Genome Biol 2024): The primary international repository for Multiplexed Assays of Variant Effect (MAVEs).
  - **Atlas of Variant Effects (AVE) Alliance**: International consortium standardizing DMS reporting, QC, and clinical data integration.
  - **VAMP-seq**: High-throughput assay for quantifying cellular protein abundance and degradation kinetics.
- **Relevance to kbrain:** Fowler and Starita produce the primary experimental data that populates ProteinGym. Understanding their experimental selection conditions (phage display vs cell growth vs proteolysis) is essential to avoiding data leakage and misinterpreting assay endpoints.
- **Open Science Stance:** Gold standard. All data public via MaveDB under Open Data licenses.

### 2.3 Laboratoire de Biologie Computationnelle et Quantitative (LCQB / Sorbonne Université)
- **Principal Investigators:** Alessandra Carbone & Elodie Laine.
- **Key Contributions:**
  - **GEMME** (Global Epistatic Model for Mutation Effects; Laine et al., Mol Biol Evol 2019): Analytical spectral decomposition of evolutionary conservation and co-variation from MSAs.
  - **JET / JET2+**: Joint Evolutionary Trees for identifying functional binding sites and catalytic residues.
- **Relevance to kbrain:** **Critical.** GEMME is kbrain's primary CPU-native baseline. It achieves a 0.4743 mean Spearman on ProteinGym v1.3 with zero GPU training, zero backpropagation, and execution times measured in minutes.
- **Open Science Stance:** Fully open-source C++ and Python implementations; web server available.

### 2.4 Rost Lab (Technical University of Munich / TUM)
- **Principal Investigator:** Burkhard Rost (Key researchers: Michael Heinzinger, Christian Dallago, Tim Bauer).
- **Key Contributions:**
  - **VESPA / VESPAl** (Marquet et al., Bioinformatics 2022): Fast mutation effect prediction combining single-sequence PLM embeddings with conservation features.
  - **VespaG** (Marquet et al., 2024): Extends VESPA with graph neural network representations of residue neighborhoods, achieving 0.4818 mean Spearman on ProteinGym.
  - **ProtTrans** (Elnaggar et al., IEEE TPAMI 2021): Pioneered large language models for proteins (ProtBERT, ProtT5-XL).
  - **FLIP** (Dallago et al., NeurIPS 2021): Functional Landscape Interaction and Prediction benchmark for supervised protein fitness.
- **Relevance to kbrain:** VESPA/VespaG models offer ultra-fast CPU inference and strong orthogonal representations that blend well with analytical MSA methods.
- **Open Science Stance:** Fully open-source weights and GitHub repositories (Academic Free License / MIT).

### 2.5 Institute for Protein Design (IPD) / Baker Lab (University of Washington)
- **Principal Investigator:** David Baker (Nobel Laureate in Chemistry 2024).
- **Key Contributions:**
  - **ProteinMPNN / LigandMPNN** (Dauparas et al., Science 2022): Autoregressive structural inverse-folding network.
  - **Rosetta / PyRosetta**: Classical macromolecular modeling suite ($\Delta\Delta G$ cartesian_ddg protocols).
  - **RFdiffusion & RoseTTAFold**: Diffusion and all-atom biomolecular structure generation.
- **Relevance to kbrain:** While ProteinMPNN is unmatched for de novo design, on ProteinGym single-mutant zero-shot fitness it scores poorly (~0.2950 Spearman) because its message-passing objective learns broad structural compatibility rather than fine biophysical fitness changes.
- **Open Science Stance:** Open for non-commercial academic use; widespread GitHub releases.

### 2.6 Bepler Lab (Fred Hutch) & Berger Lab (MIT)
- **Principal Investigators:** Tristan Bepler & Bonnie Berger.
- **Key Contributions:**
  - **PoET** (Truong & Bepler, NeurIPS 2023): Autoregressive retrieval language model conditioned on homolog prompt batches, achieving 0.4898 mean Spearman on ProteinGym v1.3.
  - **D-VELO**: Dynamic variant effect evaluation combining evolutionary dynamics with structural context.
  - Early foundational work on protein sequence embeddings (DeepBLAST, ESM-1b collaboration).
- **Relevance to kbrain:** Proves that retrieval-based language models conditioned on variable-depth homolog sets outperform static sequence-only PLMs.
- **Open Science Stance:** Open weights and inference scripts available.

### 2.7 AI for Science Lab (Westlake University / Zhejiang University)
- **Principal Investigators:** Stan Z. Li, Fajie Yuan (Key researchers: Jin Su, Sheng Wang).
- **Key Contributions:**
  - **SaProt** (Su et al., ICLR 2024): Structure-aware PLM trained on Foldseek 3Di structural tokens combined with amino acid residues. SaProt-35M achieves 0.4130 Spearman on ProteinGym; SaProt-650M achieves 0.4728.
  - **ProSST** (Wang et al., 2023): Quantized structural alphabet transformer (K=2048) achieving 0.5225 mean Spearman.
  - **VenusREM** (2024): Top-2 model on ProteinGym v1.3 (0.5357 mean Spearman) by fusing ProSST structural representations with MSA retrieval logits.
- **Relevance to kbrain:** Demonstrates that structural tokenization (Foldseek 3Di) provides massive efficiency gains over pure sequence models. A 35M SaProt model matches a 5x650M ESM-1v ensemble on ProteinGym.
- **Open Science Stance:** Open weights on Hugging Face; open GitHub repositories.

### 2.8 Fraser Lab & Kortemme Lab (UCSF)
- **Principal Investigators:** James Fraser & Tanja Kortemme.
- **Key Contributions:**
  - Biophysical deep mutational scanning characterizing enzyme catalytic active sites, allosteric networks, and conformational ensembles.
  - Rosetta Backrub protocols simulating backbone flexibility to predict mutational $\Delta\Delta G$.
- **Relevance to kbrain:** Demonstrates why static AlphaFold structures fail on allosteric and dynamic mutational effects; backbone ensemble sampling is often needed to recover subtle negative impacts.
- **Open Science Stance:** Open academic tools and Zenodo DMS repositories.

### 2.9 Wilke Lab & Ellington Lab (University of Texas at Austin)
- **Principal Investigators:** Claus O. Wilke (Integrative Biology) & Andrew D. Ellington (Molecular Biosciences).
- **Key Contributions:**
  - Biophysical determinants of protein evolution, structural tolerance, and deep mutational scanning landscape topology.
  - Foundational benchmarking critique: Woolley et al. (bioRxiv 2026, DOI: 10.64898/2026.06.04.730121), showing that broad zero-shot benchmark correlations mask local prediction collapse within viable/functional mutants, and exposing the fundamental divergence between natural evolutionary fitness and directed protein engineering goals.
- **Relevance to kbrain:** Vital reality check on benchmark interpretation. High global Spearman $\rho$ across an entire DMS assay does not imply that a model can prioritize top gain-of-function variants in directed evolution.
- **Open Science Stance:** Open source code, reproducible computational pipelines, open data sharing.

### 2.10 ai4protein Research Group (Shanghai Jiao Tong University / SIIS)
- **Key Researchers:** Liang Hong, Yafeng Liang, Nanqing Dong.
- **Key Contributions:**
  - Multi-agent collaboration frameworks for protein mutation-effect prediction: **VenusRAR** (arXiv:2602.00197, Feb 2026).
  - Integrates multimodal computational predictions (Rank stage) with automated Chain-of-Thought (CoT) structural auditing (Reason stage) to filter steric clashes and unphysical substitutions, boosting Top-5 Hit Rate in directed evolution campaigns by up to 367%.
- **Relevance to kbrain:** Demonstrates that post-inference structural auditing of candidate mutations removes unphysical false positives that deceive raw scalar log-odds models, dramatically boosting prospective hit rates.
- **Open Science Stance:** Open GitHub repositories (`ai4protein/VenusRAR`), reproducible benchmarking code.

### 2.11 Loschmidt Laboratories (Masaryk University) & DTU Biosustain
- **Principal Investigators:** Stanislav Mazurenko & Ditte Hededam Welner.
- **Key Contributions:**
  - **PRIZM** (Harding-Larsen et al., Bioinform Adv / bioRxiv Feb 2026): A two-phase framework demonstrating that $N \approx 20$ experimental measurements from an initial microplate are sufficient to select the optimal zero-shot model from ProteinGym candidate pools for subsequent directed evolution rounds.
  - Wet-lab validation on industrial biocatalysts (sucrose synthase thermostability +3°C, glycosyltransferase catalytic activity +20%).
  - Creators of widely used protein engineering computational tools (FireProt, HotSpot Wizard).
- **Relevance to kbrain:** Directly validates kbrain's label-efficient model routing findings. Demonstrates that low-N wet-lab budgets should prioritize zero-shot model selection over training fragile empirical regressors from scratch.
- **Open Science Stance:** Open source tools, Zenodo datasets, and open-access publications.

### 2.12 Green Lab (Harvard Medical School, Systems Biology)
- **Principal Investigator:** Anna G. Green.
- **Key Contributions:**
  - Mechanistic interpretability and causal feature attribution in protein language models (Mohanty et al., bioRxiv Aug/Sep 2026, DOI: 10.64898/2026.08.28.747907).
  - Deployed Sparse Autoencoders (SAEs) and activation patching on ESM-2, discovering that zero-shot variant effect predictions are mediated by sparse, reusable causal feature circuits that physically map to 3D contact residues in protein backbones.
- **Relevance to kbrain:** Provides the foundational biophysical explanation for why PLMs succeed or fail: zero-shot scores reflect internal spatial contact subgraphs, validating our hypotheses on 3D contact density gating.
- **Open Science Stance:** Open bioRxiv preprints, open GitHub code and SAE checkpoints.

### 2.13 Abbeel & Lu Groups (UC Berkeley)
- **Principal Investigators:** Pieter Abbeel, Amy X. Lu.
- **Key Contributions:**
  - Computational determinants of zero-shot fitness prediction and model preference dynamics (Gordon, Lu, & Abbeel, ICLR 2025 / bioRxiv 2024, DOI: 10.1101/2024.10.03.616542).
  - Demonstrated that a PLM's zero-shot mutation-effect accuracy is governed by the model's *implicit preference* (wild-type sequence likelihood / pseudo-perplexity), discovering an inverted-U "Goldilocks" effect where both under-represented and over-represented proteins experience degraded zero-shot accuracy.
- **Relevance to kbrain:** Provides an unsupervised, label-free ($N=0$) metric—wild-type sequence pseudo-perplexity under a small CPU PLM (ESM2-35M)—to detect out-of-distribution targets and guide zero-shot routing between sequence PLMs and MSA physics.
- **Open Science Stance:** Fully open code, OpenReview papers, bioRxiv preprints.

### 2.14 Structural Bioinformatics & Biophysics Hub (Univ. of Copenhagen / DTU)
- **Principal Investigators:** Kresten Lindorff-Larsen, Wouter Boomsma, Jes Frellsen.
- **Key Contributions:**
  - Grounding deep learning protein representations in rigorous statistical mechanics and thermodynamics.
  - Formal free-energy interpretation of inverse folding models (Frellsen et al., NeurIPS / arXiv:2506.05596), establishing the partition function links between inverse folding log-odds ratios and thermodynamic $\Delta\Delta G$ across folded backbones and unfolded ensembles.
- **Relevance to kbrain:** Grounds empirical zero-shot log-odds scoring heuristics in statistical mechanics, providing the theoretical justification for why single-structure log-odds succeed and defining where unfolded-state corrections are required.
- **Open Science Stance:** Fully open Python implementations (`MachineLearningLifeScience/inverse_folding_free_energies`), open preprints, and NeurIPS proceedings.

### 2.15 Gitter Lab (Univ. of Wisconsin-Madison & Morgridge Institute)
- **Principal Investigator:** Anthony Gitter.
- **Key Contributions:**
  - Methodological evaluation of structure-based machine learning for protein engineering and mutation effect prediction (Sharma & Gitter, arXiv:2504.16886, ICLR Workshop 2025).
  - Systematically evaluated the failure modes of inverse folding models (ProteinMPNN, ESM-IF1, MIF-ST) in intrinsically disordered regions (IDRs) and analyzed experimental PDB versus predicted AlphaFold coordinates.
- **Relevance to kbrain:** Explains the exact bottleneck encountered in kbrain's Task #255 GNM structural dynamics evaluation (where 130/217 assays failed due to pLDDT < 70 or disordered regions), motivating our disorder-aware masking filter (Candidate C29).
- **Open Science Stance:** Open source benchmark repositories on GitHub, OpenReview publications.

### 2.16 Peking University / Gao Lab & ChemBio Hub
- **Principal Investigator:** Yi Qin Gao (Key researchers: Zechen Chen, Tianyu Sun, Zun Wang).
- **Key Contributions:**
  - **JustEvo** (Chen et al., JCTC 2026, DOI: 10.1021/acs.jctc.6c01288): Prior-guided adaptive Mixture-of-Experts (MoE) framework for low-data and multifunctional directed evolution on ProteinGym.
  - **Prot2Chat** (Wang et al., Bioinformatics 2025): Multimodal protein large language model integrating early fusion of sequence, structure, and biochemical text instructions.
- **Relevance to kbrain:** Directly addresses our low-N directed evolution track: proves that dynamic ranking agreement weighting across heterogeneous surrogate experts outperforms single-architecture regressors on ProteinGym benchmarks while enabling multi-objective Pareto optimization.
- **Open Science Stance:** Peer-reviewed publications in JCTC and Bioinformatics with reproducible evaluation benchmarks.

### 2.17 Computational Precision Medicine Lab (TIGEM / Gambardella Lab)
- **Principal Investigators:** Gennaro Gambardella & Roberto Arnese (Telethon Institute of Genetics and Medicine / TIGEM).
- **Key Contributions:**
  - **ESMRank** (Arnese & Gambardella, Nature / npj Systems Biology and Applications 2026, DOI: 10.1038/s44320-026-00252-3): Learning-to-rank variant effect prediction from >1,100 MAVEs and 2M missense mutations.
  - **Variant Soundness:** Overlap-aware rank-fusion algorithm that harmonizes cross-assay experimental redundancy into a consensus landscape enriched for biophysical folding and stability constraints.
- **Relevance to kbrain:** Provides a rigorous method to extract consensus signal from multi-assay protein targets in ProteinGym (e.g. beta-lactamase, PTEN, TP53, SARS-CoV-2 RBD), proving that pairwise ranking loss isolates structural stability better than noisy scalar regression.
- **Open Science Stance:** Open access Nature Portfolio publication, openly accessible variant constraint scores and Python implementations.

### 2.18 Frontier Synthetic Biology & Biocatalysis Hub (Tianjin Univ. / Yuan Lab)
- **Principal Investigators:** Yingjin Yuan & Zhenglin Yuchi (Key researcher: Jianing Xu).
- **Key Contributions:**
  - **REAP & RankReg** (Xu et al., Nature Communications 2026, DOI: 10.1038/s41467-026-76264-2): Automated closed-loop enzyme engineering driven by **RankReg**, a hybrid loss function jointly optimizing ranking fidelity and quantitative MSE accuracy.
  - Demonstrated automated discovery of distal and catalytic hotspots yielding 57-fold activity increases on P450 BM3 and 104-fold on Sortase A in five experimental cycles.
- **Relevance to kbrain:** Solves the core statistical flaw in low-N surrogate modeling: standard MSE regression overfits assay scale noise, while RankReg preserves the rank ordering essential for directed evolution candidate nomination.
- **Open Science Stance:** Nature Communications open access, open software routines for ranking-guided exploration.

### 2.19 Fleishman Lab (Weizmann Institute of Science)
- **Principal Investigators:** Sarel J. Fleishman & Itay Talpir (Department of Biomolecular Sciences, Weizmann Institute).
- **Key Contributions:**
  - Automated structure-based design of stable, functional proteins (PROSS for stability, FuncLib for active-site multi-point diversity).
  - Critical evaluation of protein language models in mutation-dense functional landscapes (Talpir & Fleishman, bioRxiv 2026, DOI: 10.64898/2026.05.01.722313), proving that PLMs perform indistinguishably across parameter scales and do not outperform simple homology baselines on multi-mutant designs without biophysical priors.
- **Relevance to kbrain:** Directly validates kbrain's zero-shot epistasis findings: confirms that scaling sequence PLMs does not solve higher-order mutational design and that structural and biophysical constraints are indispensable.
- **Open Science Stance:** Open access preprints, publicly accessible web servers (PROSS, FuncLib) and GitHub evaluation pipelines.

### 2.20 Viral Genomics & Evolution Hub (MRC-University of Glasgow CVR / Robertson Lab)
- **Principal Investigators:** David L. Robertson & Oscar A. MacLean (MRC-University of Glasgow Centre for Virus Research).
- **Key Contributions:**
  - Disentangling nucleotide mutational supply from biophysical protein fitness in PLMs (MacLean et al., bioRxiv 2026, DOI: 10.64898/2026.07.06.736753).
  - Demonstrated that base PLM pseudo-probabilities are confounded by codon distance and transition/transversion biases learned from natural sequence databases, and established methods to isolate pure protein fitness for protein engineering while retaining forecasting power for pathogen emergence.
- **Relevance to kbrain:** Provides the theoretical and empirical mechanism for why PLMs underperform on unbiased saturation mutagenesis (DMS) libraries: natural sequences under-sample multi-nucleotide changes, which PLMs penalize as "unfit" despite biophysical stability.
- **Open Science Stance:** Open science bioRxiv preprints, open data pipelines for viral lineage analysis.

### 2.21 3Bio / Interuniversity Institute of Bioinformatics in Brussels (ULB / Pucci & Rooman)
- **Principal Investigators:** Fabrizio Pucci & Marianne Rooman (Université Libre de Bruxelles / ULB).
- **Key Contributions:**
  - **RSALOR** (Tsishyn, Hermans, Rooman, & Pucci, Bioinformatics 2025, DOI: 10.1093/bioinformatics/btaf322): Parameter-free mutational effect predictor multiplying Relative Solvent Accessibility (RSA) by evolutionary Log-Odds Ratios (LOR), achieving 0.4848 Spearman across ProteinGym.
  - **PoPMuSiC & BeAtMuSiC**: Classical, fast biophysical predictors for folding and binding free-energy changes ($\Delta\Delta G$).
- **Relevance to kbrain:** Proves that transparent, parameter-free structural biophysics runs in milliseconds on CPU and matches or beats multi-billion parameter neural networks on ProteinGym.
- **Open Science Stance:** Open source Python package (`pip install rsalor`) and GitHub repository at `3BioCompBio/RSALOR`.

---

## 3. AI Foundation Model Consortia & Tech Giants

### 3.1 EvolutionaryScale
- **Founders:** Alex Rives, Tom Sercu, Sal Candido (former core leads of Meta FAIR Protein Team).
- **Capitalization:** >$142M Seed round (Lux Capital, Nat Friedman, Daniel Gross, Amazon).
- **Flagship Model:** **ESM3** (Hayes et al., 2024; bioRxiv:2024.07.02.601708). Multimodal generative foundation model (sequence, structure, function tokens) across 1.4B, 7B, and 98B parameter scales.
- **ProteinGym Standing:** ESM3-open (1.4B) achieves 0.4827 mean Spearman (#9 on v1.3). Small standalone variants (ESM-C 300M and 600M) score 0.4325 and 0.4340.
- **Business Model:** Proprietary commercial API ("Forge Platform") for pharmaceutical design; open weights released for the small 1.4B model under a restrictive non-commercial research license.
- **Evaluation:** Outstanding engineering, but ESM3-1.4B (0.4827) only slightly exceeds GEMME (0.4743), an analytical CPU model with zero parameters.

### 3.2 Meta FAIR (Fundamental AI Research)
- **Key Contributors:** Zeming Lin, Halil Akin, Roshan Rao, Brian Hie, Alex Rives.
- **Key Models:** ESM-1b (2021), ESM-1v (2021), ESM-2 (2023, 8M to 15B), ESM-IF1 (inverse folding), MSA Transformer (2021).
- **ProteinGym Standing:** ESM-2 (650M) sits at 0.4382 mean Spearman; ESM-2 (15B) drops to 0.4253. MSA Transformer scores 0.4526.
- **Business Model:** Fully open-source public scientific research (MIT / Apache licenses). While the original protein team departed to found EvolutionaryScale, Meta's open weights remain the universal benchmark standard.

### 3.3 Google DeepMind & Isomorphic Labs
- **Key Contributors:** Demis Hassabis, John Jumper, Pushmeet Kohli, Jun Cheng.
- **Key Models:**
  - **AlphaFold 2 & AlphaFold 3** (Jumper et al., Nature 2021; Abramson et al., Nature 2024): Transformed structural biology.
  - **AlphaMissense** (Cheng et al., Science 2023): Fine-tuned AlphaFold variant classifier predicting pathogenicity for 71 million human missense mutations (89% classified at 90% precision).
- **ProteinGym Standing:** AlphaMissense is primarily a clinical pathogenicity predictor. When evaluated against DMS functional fitness, it achieves strong correlations on human proteins but lacks coverage for viral/prokaryotic directed evolution.
- **Business Model:** DeepMind maintains open scientific releases for AlphaFold/AlphaMissense databases; Isomorphic Labs operates commercially for partnered drug discovery (Lilly, Novartis).

### 3.4 GenBio.ai / BioMap
- **Origins:** Founded by Robin Li (Baidu) and Wei Liu.
- **Flagship Model:** **AIDO Protein-RAG** (16B). Currently holds the **#1 ranking on ProteinGym v1.3** (0.5419 mean Spearman, 0.5182 aggregate).
- **Architecture:** Integrates pre-trained protein language models with homologous sequence retrieval (RAG) and structural conditioning.
- **Business Model:** Enterprise biotechnology partnerships and bio-computing cloud platforms.

### 3.5 Multiverse Computing
- **Team / Authors:** Alberto Martínez, Natalia Flechas Manrique, Llorenç Espinosa-Portalés, Luc Andrea.
- **Key Model:** **ProtModernBERT** (arXiv:2610.19738, Oct 2026).
- **Architecture:** Replaces legacy BERT components with modern encoder refinements (unpadding, rotary position embeddings [RoPE], GeGLU activations, sequence packing) trained on the UR100P corpus.
- **ProteinGym Standing:** Matches ProtBert and Amplify-120M zero-shot and representation benchmarks while achieving an 80% to 90% reduction in pre-training FLOPs.
- **Relevance to kbrain:** Demonstrates high-throughput, low-memory PLM inference architectures optimized for standard commodity CPUs, highly aligned with edge deployment.
- **Business Model:** Efficient AI architectures, quantum-inspired algorithms, and enterprise edge computing solutions.

### 3.6 InstaDeep (BioNTech BioAI)
- **Key Contributors:** Jacob Beck, Shikha Surana, Manus McAuliffe, Oliver Bent, Thomas D. Barrett, Juan Jose Garau Luis, Paul Duckworth.
- **Key Contributions:**
  - **Metalic** (ICLR 2025 / arXiv:2410.08355): Formulated low-data fitness prediction as meta-in-context learning across ProteinGym landscapes, setting SOTA low-N prediction with 18x fewer parameters than full-model fine-tuning.
  - Biological sequence foundation models and active learning workflows for therapeutic antibody and mRNA vaccine design.
- **Relevance to kbrain:** Confirms that meta-learning across protein fitness landscapes transfers prior adaptation knowledge, providing a sample-efficient alternative to parameter-heavy fine-tuning.
- **Business Model:** BioAI subsidiary of BioNTech, deploying proprietary models for therapeutic discovery and enterprise collaborations.

---

## 4. Commercial Startups & Applied Protein Platforms

| Company | HQ / Capital | Technical Focus | Method / Tech Stack | Relevance to Mutation Effects |
|---|---|---|---|---|
| **Cradle Bio** | Zurich / Amsterdam ($30M+) | ML-guided enzyme & antibody engineering SaaS | Low-N active learning, sequence generation, Bayesian optimization | Optimizes target phenotypes in 2-3 wet-lab rounds (24-96 variants per round) |
| **Generate:Biomedicines** | Somerville, MA ($700M+) | Generative de novo protein therapeutics | Chroma structural diffusion, hierarchical generative models | High-throughput internal DMS pipelines generate continuous fitness data |
| **Nabla Bio** | Boston, MA ($26M+) | Next-generation antibody design | Multiplexed wet-lab characterization + UniRep/PLM fitness heads | Targets antibody developability, expression, and cross-reactivity profiling |
| **Adaptyv Bio** | Lausanne, Switzerland ($15M+) | Robotic protein synthesis & screening foundry | Automated cell-free synthesis, microfluidics, biosensors | Generates empirical DMS landscapes on demand via robotic biofoundries |
| **Basecamp Research** | London, UK ($60M+) | Environmental biodiversity & novel enzymes | Base-PLM trained on proprietary global metagenomic data | Solves the MSA depth bottleneck ($N_{eff}/L \approx 0$) for orphan enzymes |
| **Tamarind Bio / Neurosnap** | Boston, MA (Seed) | Cloud bioinformatics & model hosting | Containerized inference for SaProt, ESM-2, AlphaFold, ColabFold | Democratizes access to high-GPU models for academic wet-labs |

---

## 5. Comparative Capabilities Matrix

The table below contrasts how major entities approach protein mutation-effect prediction across compute, algorithms, and open science:

| Entity | Primary Representative Model | Core Algorithmic Thesis | ProteinGym v1.3 Mean $\bar{\rho}$ | Compute Profile | Open Source / Weights? | Primary Commercial Objective |
|---|---|---|---|---|---|---|
| **LCQB (Carbone/Laine)** | GEMME | MSA co-variation & conservation spectral physics | **0.4743** | **CPU (minutes)** | Yes (Fully open C++/Python) | None (Pure academic research) |
| **TUM (Rost Lab)** | VespaG / VESPA | GNN + PLM embeddings + conservation | 0.4818 / 0.4630 | CPU / Low GPU | Yes (Open GitHub/HuggingFace) | Academic tools & benchmarks |
| **Westlake Univ.** | VenusREM / SaProt | 3D structural tokens (Foldseek) + MSA retrieval | **0.5357** / 0.4728 | GPU (AF2 backbone required) | Yes (Hugging Face open weights) | Academic research |
| **GenBio.ai** | AIDO Protein-RAG | 16B PLM + Homolog retrieval RAG | **0.5419** | Multi-A100 Cluster | Partial (Paper open, API-driven) | Enterprise biopharma contracts |
| **EvolutionaryScale** | ESM3-open (1.4B) | Multimodal sequence-structure-function generation | 0.4827 | High-end GPU cluster | Restrictive research license | Forge API, therapeutic licensing |
| **Meta FAIR** | ESM-2 (650M) | Unsupervised masked language modeling on UniRef | 0.4382 | 1x GPU (16 GB) / Slow CPU | Yes (MIT open source) | Foundational open AI research |
| **Marks / OATML** | TranceptEVE L | Autoregressive retrieval + Bayesian VAE | 0.4745 | GPU (Per-family training) | Yes (Fully open science) | Clinical genetics & benchmark creation |
| **DeepMind** | AlphaMissense | Structural residue environments + conservation | Clinical SOTA | High GPU training; precomputed DB | Yes (Predictions open for 71M muts) | Isomorphic Labs drug pipeline |
| **Cradle Bio** | Proprietary Active Learner | Low-N Bayesian optimization + fine-tuned PLMs | Supervised focus | Cloud platform | No (Proprietary SaaS) | Software subscriptions & milestone bio-bucks |

---

## 6. Hype vs. Evidence: Field Analysis of Commercial Claims

### Claim 1: "Scaling foundation models to billions of parameters makes variant effect prediction trivial."
- **The Hype:** Marketing materials from foundation model startups imply that increasing sequence parameters from 650M to 15B or 100B yields monotonic gains in fitness prediction.
- **The Evidence:** Falsified by ProteinGym v1.3 empirical benchmarks.
  - ESM-2 (650M) achieves 0.4382. ESM-2 (3B) drops to 0.4321. ESM-2 (15B) drops to 0.4253.
  - xTrimoPGLM-100B drops to 0.3643.
  - Scaling a pure sequence model without alignment retrieval or structural constraints causes severe overfitting to common natural sequence patterns, blinding the model to non-canonical stabilizing mutations.

### Claim 2: "Proprietary wet-lab data moats grant commercial platforms an insurmountable edge."
- **The Hype:** Venture-backed biotechs claim their internal private DMS data yields proprietary zero-shot predictors that vastly outperform open academic methods.
- **The Evidence:** Open academic and community models consistently dominate public leaderboards.
  - GEMME (an open-source academic model from 2019 running on CPU) matches or beats multi-million-dollar commercial foundation models on public DMS benchmarks.
  - Fusing open AlphaFold structures with open retrieval algorithms (e.g. VenusREM, SaProt) delivers top-tier performance (>0.53 Spearman) without requiring private training sets.

### Claim 3: "Low-N machine learning can navigate complex fitness landscapes in 24 to 48 variants without prior evolutionary models."
- **The Hype:** Commercial platform sales pitches frequently claim that proprietary neural networks can learn to optimize proteins from just 24 or 48 experimental measurements from a single microplate.
- **The Evidence:** Refuted by low-N supervised literature (Hsu et al., Nat Biotechnol 2022; ProteinGym CV benchmarks).
  - Unregularized supervised models trained on $N \le 48$ mutants suffer catastrophic overfitting, often yielding negative correlation on test mutants.
  - Reliable performance in low-N regimes is achievable *only* when the model is heavily regularized and augmented with an evolutionary zero-shot prior (e.g., GEMME, EVmutation, or ESM-2). The value comes from the evolutionary prior, not the complex neural head.

### Claim 4: "Structural inverse folding (e.g., ProteinMPNN) is the best choice for scoring mutational fitness."
- **The Hype:** Due to ProteinMPNN's success in de novo sequence design, many wet-labs mistakenly use its log-odds scores to rank DMS mutant libraries.
- **The Evidence:** ProteinMPNN achieves a poor 0.2950 mean Spearman across ProteinGym v1.3 substitution assays.
  - ProteinMPNN was trained to solve sequence recovery given fixed backbone coordinates; its loss function does not penalize minor loss-of-function phenotypes or subtle destabilizations. Structure-aware models must incorporate evolutionary conservation or structural alphabets (like SaProt or ProSST) to succeed on fitness ranking.

---

## 7. Strategic Implications for kbrain (The CPU-Only Edge)

Understanding the strengths and weaknesses of the major players clarifies kbrain's research mandate:

1. **Where we cannot compete:**
   - Training 10B+ parameter multimodal foundation models (EvolutionaryScale, GenBio.ai, Meta).
   - Operating automated wet-lab biofoundries with robotic liquid handlers (Adaptyv, Generate).

2. **Where kbrain wins (Our Asymmetric Edge):**
   - **Zero-GPU High Performance:** Academic work from LCQB (GEMME) and TUM (VESPA) proves that analytical evolutionary physics and lightweight CPU-runnable architectures compete with or beat massive GPU models.
   - **Model Synthesis and Calibration:** Precomputed scores for 95 published models exist on disk in our lab. We can discover optimal, lightweight ensembles, depth-gated blends, and temperature calibrations in seconds on an 8-core CPU.
   - **Rigorously Audited Low-N Guidance:** While commercial platforms make aggressive marketing claims about low-N active learning, kbrain can empirically benchmark augmented ridge regressors and empirical Bayes shrinkage estimators under strict position-disjoint splits (`fold_contiguous_5`), establishing honest statistical limits.
   - **Public Benchmark Integrity:** kbrain publishes reproducible, leak-free evaluations and documented null results that expose cherry-picked evaluation metrics.
