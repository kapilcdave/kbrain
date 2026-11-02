# Position-adaptive zero-shot fusion: qualified reproduction note

## What was validated

On the frozen ProteinGym v1.3 backtest across all 217 deep mutational scanning substitution assays (186 independent `UniProt_ID` protein holdouts), a cross-fitted monotone sigmoid gate combining published GEMME and ESM2-35M scores based on Site-Independent evolutionary constraint ($w(c) = \sigma(a + b \cdot c)$) arithmetically outperformed a fixed 50/50 rank blend by **+0.029754 Spearman per protein** (95% protein-cluster bootstrap CI **[+0.020487, +0.038899]**; $n=186$, cluster seed=7). The top-5%-trimmed mean improvement was **+0.022295**, and 119 of 186 proteins (64.0%) favored the gated fusion over the 50/50 blend. The secondary endpoint against GEMME alone showed a modest positive improvement of **+0.006262 per protein** (95% CI **[+0.001993, +0.010460]**; top-5%-trimmed mean $+0.002843$). Mean per-assay Spearman correlations were **0.479676** (gated), **0.447925** (static 50/50 blend), and **0.474261** (GEMME alone).

All metrics were independently reproduced bit-for-bit with zero label leakage, strict protein-disjoint outer/inner splits, and 100% paired mutant coverage. Under the strict decision rule of the frozen preregistration (`ci_low > 0`), the experiment arithmetically passed.

## Critical Refutation of Position-Adaptivity Mechanism

Although the backtest arithmetically passes its primary comparison against the equal 50/50 blend, the claimed scientific mechanism—that residue-level evolutionary constraint adaptively routes predictions between epistatic and language models—was conclusively refuted by the prespecified controls and ablations:

1. **Constant-Gate Control ($b=0$) Spans Zero**:
   Restricting the gate to a global scalar weight ($b=0$, no position adaptivity) yielded mean Spearman **0.478384**. The paired difference between the position-adaptive gate and this constant gate was $+0.000877$ with a 95% bootstrap CI of **$[-0.000319, +0.002093]$** (spanning zero) and an ex-top 5% trimmed mean of **$-0.000044$**. The win rate was 97 / 186 (52.2%), indistinguishable from random chance ($p = 0.596$).
2. **Shuffled-Confidence Control Refutes Conservation Routing**:
   Randomly permuting the position-confidence vector within each assay destroys residue identity while preserving the marginal distribution. The shuffled gate achieved mean Spearman **0.479787**—numerically *higher* than the unshuffled gate ($0.479676$). Its improvement over the static blend was $+0.029980$ (95% CI $[+0.020650, +0.038993]$). In all 5 cross-validation folds, shuffled data achieved higher inner validation scores than unshuffled data.
3. **Strawman Baseline Asymmetry**:
   ESM2-35M (mean Spearman 0.3188) is substantially weaker than GEMME (0.4743). An unweighted 50/50 blend severely degrades GEMME, dragging mean Spearman down to 0.4479. The gate's grid ($a=1$) merely discovered that GEMME requires $\sim 73\text{--}80\%$ global weight. A simple, position-blind scalar blend of 80% GEMME + 20% ESM2-35M achieves mean Spearman **0.480458**, outperforming the adaptive gate benchmark-wide.
4. **Regional Degradation**:
   On Stability assays (66 proteins, $-0.003075$), High MSA-depth assays (63 proteins, $-0.002600$), Eukaryotes ($-0.001751$), and Human targets ($-0.000394$), the position-adaptive gate performed worse than the constant gate.

## Reproduce

1. Use staged ProteinGym v1.3 substitutions data (`data/proteingym/`), `DMS_substitutions_reference.csv`, and the frozen preregistration `inputs/position-adaptive-zero-shot-fusion.md` (Task #231).
2. Load published scores via `lab/proteingym.py` using `pg.published_scores(aid, "GEMME")`, `pg.published_scores(aid, "ESM2 (35M)")`, and `pg.published_scores(aid, "Site-Independent")`.
3. Require $\ge 95\%$ paired mutant coverage per assay (all 217 assays pass at 100.0% coverage).
4. Define outer 5-fold protein holdouts using `int.from_bytes(sha256("task-231-outer|" + UniProt_ID).digest()[:8], "big") % 5`.
5. For each outer fold, select gate parameters $(a,b)$ from $a \in \{-1, 0, 1\}$ and $b \in \{0, 0.5, 1.5\}$ using 4-fold inner cross-fitting with prefix `"task-231-inner|"`.
6. Compute residue confidence $c$ from single-mutant Site-Independent scores, convert to within-assay percentile ranks, and evaluate $w(c) = \sigma(a + b \cdot c)$ on within-assay percentile ranks $r_{\text{GEMME}}$ and $r_{\text{ESM2-35M}}$.
7. Score predictions with `lab/proteingym.py` `pg.spearman_by_assay`, cluster paired improvements by `UniProt_ID` with `pg.improvement_units(..., by="protein")`, and run `kbstats.evaluate(units, n_boot=2000, alpha=0.05, seed=7)`.
8. The observed results match exactly: `net_mean = +0.029754`, `ci_low = +0.020487`, `ci_high = +0.038899`, `trimmed_mean = +0.022295`.

## Caveats and Practical Recommendations

- **Do Not Deploy Residue-Level Gating**: Position adaptivity via Site-Independent profile log-odds does not provide genuine routing signal. Do not implement complex residue-level gating functions based on this mechanism.
- **Prefer Asymmetric Scalar Ensembling**: When combining GEMME with smaller PLMs like ESM2-35M, an asymmetric scalar blend (80% GEMME + 20% ESM2-35M) provides a simple, robust $+0.0062$ gain over GEMME alone without requiring auxiliary Site-Independent calculations or learned gating parameters.

## Next Decisions and Forward Evaluation

1. **Forward Paper Test (Requires Operator Approval)**:
   Evaluate whether the asymmetric 80% GEMME + 20% ESM2-35M scalar blend retains its edge over GEMME alone on an unseen forward DMS publication held out from ProteinGym v1.3. As always, model weights, score orientations, coverage rules, and bootstrap parameters must remain frozen prior to seeing experimental labels.
2. **Alternative Local Structural/Epistatic Features**:
   Investigate whether biophysical structural metrics (such as AlphaFold2 residue pLDDT, relative solvent accessibility, or contact density) provide causal position routing, where evolutionary profile conservation failed.
