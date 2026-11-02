# Position-adaptive zero-shot fusion passes arithmetically, but conservation routing is refuted

_2026-11-01. Validated experiment (Tasks #231, #233, #249, and #250); deployed in dry mode by Task #253._

## Claim

On the frozen ProteinGym v1.3 substitution benchmark across all 217 assays (186 independent UniProt targets),
a cross-fitted monotone sigmoid gate combining GEMME and ESM2-35M using Site-Independent profile conservation
confidence arithmetically outperformed a fixed 50/50 rank blend and GEMME alone. However, the proposed
scientific mechanism—that residue-level evolutionary conservation adaptively routes predictions between
epistatic MSA models and protein language models—was conclusively refuted by prespecified controls: a
constant gate performed identically, permuted confidence vectors performed equally well, and an unweighted
50/50 baseline was a strawman because ESM2-35M is much weaker than GEMME. Complex position-level conservation
gating should not be deployed; simple asymmetric scalar ensembling (80% GEMME + 20% ESM2-35M) achieves superior
performance across the benchmark without residue-level features.

## Measured result

The preregistered primary endpoint passed with complete score coverage across all 217 assays and 186
independent UniProt protein holdouts (100.0% paired mutant coverage). Mean per-assay Spearman was
**0.479676** for the position-adaptive gate, **0.447925** for the static 50/50 blend, and **0.474261** for
GEMME alone.

- **Primary endpoint vs static 50/50 blend:** Paired per-protein improvement was **+0.029754 mean Spearman
  per protein** (95% protein-cluster bootstrap CI **[+0.020487, +0.038899]**; top-5%-trimmed mean
  **+0.022295**; **186 proteins**; seed 7). 119 of 186 proteins (64.0%) favored the gated fusion.
- **Secondary endpoint vs GEMME alone:** Paired per-protein improvement was **+0.006262 mean Spearman
  per protein** (95% CI **[+0.001993, +0.010460]**; top-5%-trimmed mean **+0.002843**).

The prespecified negative controls and ablations conclusively refuted the position-adaptivity mechanism:

1. **Constant-Gate Control ($b=0$) Spans Zero:**
   Restricting the gate to a global scalar weight ($b=0$, no position adaptivity; $a=1, w \approx 0.731$)
   achieved mean Spearman **0.478384**. The paired difference between the adaptive gate and this constant
   gate was **+0.000877** with a 95% bootstrap CI of **[-0.000319, +0.002093]** (spanning zero) and a
   top-5%-trimmed mean of **-0.000044**. The win rate was 97 / 186 (52.2%, sign test $p = 0.596$),
   indistinguishable from random chance.
2. **Shuffled-Confidence Control Refutes Conservation Routing:**
   Randomly permuting the residue-confidence vector within each assay destroys position identity while
   preserving the marginal distribution. The shuffled gate reached mean Spearman **0.479787**—numerically
   higher than the unshuffled gate ($0.479676$)—and beat the static blend by **+0.029980**
   (95% CI **[+0.020650, +0.038993]**). In all 5 cross-validation folds, shuffled data achieved higher inner
   validation scores than unshuffled data.
3. **Strawman Baseline Asymmetry:**
   ESM2-35M (mean Spearman 0.3188) is substantially weaker than GEMME (0.4743). An equal 50/50 blend severely
   penalizes GEMME, creating an artificially easy hurdle. The adaptive gate merely discovered that GEMME
   requires $\sim 73\text{--}80\%$ global weight. A static, position-blind scalar blend of 80% GEMME + 20%
   ESM2-35M achieves mean Spearman **0.480458**, outperforming the adaptive gate benchmark-wide without any
   residue features.
4. **Regional Degradation:**
   On Stability assays (66 proteins, $-0.003075$), High MSA-depth assays (63 proteins, $-0.002600$),
   Eukaryotes ($-0.001751$), and Human targets ($-0.000394$), the position-adaptive gate performed worse
   than the constant gate.

## Inference and conclusion

The experiment arithmetically passes its preregistered primary gate against the static 50/50 baseline, but
the scientific mechanism fails. Residue-level Site-Independent conservation profile log-odds do not provide
meaningful local routing signal between evolutionary and language models. The empirical gain observed in the
adaptive gate is driven entirely by global asymmetric re-weighting towards GEMME, not local position sensitivity.

Keep the result in dry mode. Do not deploy residue-level conservation gating for prospective targets.
Practitioners seeking a lightweight zero-shot boost over GEMME should use a simple, position-blind scalar
blend (e.g. 80% GEMME + 20% ESM2-35M), which provides a robust $+0.0062$ improvement over GEMME alone without
auxiliary profile computations or learned gating parameters. Any forward evaluation on unseen DMS papers
requires human operator approval. Future routing investigations should focus on 3D structural features
(e.g. AlphaFold2 residue pLDDT, relative solvent accessibility, contact density) rather than 1D sequence
conservation.

## Data, procedure, and audit trail

- **Data:** ProteinGym v1.3 DMS substitutions, published zero-shot scores, and reference metadata; 217 assays
  grouped into 186 UniProt targets. Zenodo accessions
  [10.5281/zenodo.7352500](https://doi.org/10.5281/zenodo.7352500) and
  [10.5281/zenodo.10052327](https://doi.org/10.5281/zenodo.10052327). Benchmark reference: Notin et al.,
  ProteinGym, [arXiv:2306.12204](https://arxiv.org/abs/2306.12204).
- **Models:** GEMME is described by Laine et al., 2019,
  [DOI:10.1093/molbev/msz179](https://doi.org/10.1093/molbev/msz179); ESM2 by Lin et al., 2023,
  [DOI:10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574); Site-Independent profile model from
  Hopf et al., 2017, [DOI:10.1038/nbt.3769](https://doi.org/10.1038/nbt.3769).
- **Procedure:** Load published scores for GEMME, ESM2-35M, and Site-Independent via `lab/proteingym.py`.
  Compute residue confidence $c$ from single-mutant Site-Independent scores, convert to within-assay percentile
  ranks, and define gate $w(c) = \sigma(a + b \cdot c)$. Align outer 5-fold protein holdouts using
  `int.from_bytes(sha256("task-231-outer|" + UniProt_ID).digest()[:8], "big") % 5`. For each fold, select
  $(a, b) \in \{-1, 0, 1\} \times \{0, 0.5, 1.5\}$ via 4-fold inner cross-fitting. Blend within-assay percentile
  ranks $r_{\text{GEMME}}$ and $r_{\text{ESM2-35M}}$ by $w(c)$. Score with `pg.spearman_by_assay`, cluster paired
  improvements by `UniProt_ID` with `pg.improvement_units(..., by="protein")`, and evaluate 2,000 bootstrap
  resamples with seed 7.
- **Code pointer:** trusted scoring code in [`lab/proteingym.py`](../../lab/proteingym.py); frozen reproduction
  steps and deployment constraints in the
  [deployment brief](../../fields/proteins/deploy-position-adaptive-zero-shot-fusion.md). Task #231 holds the
  frozen preregistration, Task #233 is the experiment run, Task #249 is the skeptic audit, and Task #250 records
  the field verdict.

## Caveats

- The positive primary endpoint establishes arithmetic superiority over a crippled 50/50 blend, not a valid
  mechanism for position-adaptive routing.
- The paired difference over a constant scalar gate ($b=0$) spans zero ($[-0.000319, +0.002093]$) and the
  sign test is non-significant ($p = 0.596$).
- Shuffled confidence vectors produced equal or better performance, proving that Site-Independent conservation
  profiles do not route variant predictions effectively.
- A fixed 80/20 scalar blend outperforms the adaptive gate across the benchmark (0.4805 vs 0.4797) without
  requiring auxiliary features or parameter fitting.
- Retrospective benchmark results on ProteinGym v1.3 must not be deployed prospectively without an
  operator-approved forward test on unseen targets.
