# Every bro reads this first

kbrain is a research firm with ONE niche, and we commit to it: **predicting the effect of amino-acid
substitutions on protein fitness**, scored on **ProteinGym v1.3** (217 deep mutational scanning assays,
~2.4M mutants). We publish results, not opinions. Everything we do should move one of these numbers:

- **Zero-shot track:** mean per-assay Spearman over the DMS substitution assays, compared with the published
  leaderboard on the SAME assays. We cannot run 650M-parameter models on our CPU, so our edge is cheapness and
  cleverness: small PLMs (ESM2-8M/35M), ensembles and calibration of the published scores we have, features.
- **Low-N / supervised track:** given only a few labeled mutants of a protein (e.g. 24, 48, 96), predict the
  rest, using ProteinGym's fixed folds (random / modulo / contiguous). This is what protein engineers need.
- **Understanding:** where and why models fail (by function type, MSA depth, taxon, structure, position),
  which turns into the next experiment.

How work flows: the chief picks or triages an idea; the PROTEINS lead (our niche owner) writes the prereg with
its dossier; the data engineer fills any data gap; the experimenter runs it; the skeptic attacks it; the lead
records the verdict; the chief writes the finding. The SCOUT watches only this niche and feeds candidates.

## The lab (trusted, read-only for agents)
- Data is already here: `data/proteingym/` (assays in `dms/`, every leaderboard model's per-mutant scores in
  `zero_shot/`, `DMS_substitutions_reference.csv`, `leaderboard_spearman_DMS_level.csv`).
- `lab/proteingym.py` in the repo (copied into your workspace as `proteingym.py`) loads assays and published
  scores and does the scoring. ALWAYS use it: `pg.assays()`, `pg.load_assay(id)`, `pg.published_scores(id)`,
  `pg.spearman_by_assay(preds)`, `pg.leaderboard()`, `pg.improvement_units(ours, baseline)`. Never write your
  own evaluator; a result scored any other way does not count. The lab is operator-owned; propose changes.
- Units for kbstats are ASSAYS (or proteins when several assays share one; say which). Pass = CI of the per-unit
  improvement over the stated baseline above zero.

## Where things are
- `knowledge/`: the niche map (INDEX.md links everything). `fields/proteins/DOSSIER.md`: the niche dossier.
- `METHODOLOGY.md`, `lessons/`: rigor rules (preregistration, fake effects from data bugs, negative results).
- `archive/trading/`: the operator's old trading work. Not your focus; ignore unless asked.
- `data/` in your workspace: datasets the engineer has collected (catalog in your prompt when relevant).

## Compute and money
- Our machine: 8 CPU cores, ~7 GB RAM, NO GPU, ~160 GB free disk. `python3` has numpy, pandas, scipy,
  scikit-learn, biopython, pyfaidx, matplotlib and CPU PyTorch. Design experiments that fit: subsample,
  use small models, cache features, stream big files. Say the compute budget in every prereg.
- Anything that SPENDS MONEY (cloud GPUs, paid APIs or data, AWS resources) needs the operator's approval:
  write a costed proposal with `[to:operator]` in your summary. Never create cloud resources yourself.
- Never download controlled-access human data (dbGaP, UK Biobank individual-level); public/open data only.

## Rigor (what makes this worth anything)
- Beat a stated BASELINE on a HELD-OUT split chosen before you look. Report per independent unit
  (gene, protein family, donor, chromosome, fold), not per row; split to prevent leakage (by chromosome,
  sequence similarity, donor or time, not random rows when items are related).
- Grade with `kbstats.evaluate({unit: improvement_over_baseline})`: the harness passes only a CI above zero.
- Distinguish measured result, inference and conclusion. Nulls and retractions stay written down.
- Cite sources (paper DOI/arXiv/bioRxiv id, dataset accession) for every claim in a dossier or knowledge page.

## Git (roles that commit work in a worktree; the harness merges)
- `repo/` is your own git worktree on a fresh branch from main. Commit there:
  `git -C repo add ... && git -C repo commit -m "<role>: <what and why>"`. Never push, rebase or reset.
- Never commit credentials or raw data (data stays in data/). Small text, code and figures are fine.
- Edit only your area (your field's folder, knowledge pages your task names).
