# Every bro reads this first

kbrain is the operator's research brain for **bio x AI**: genomics, DNA and regulatory sequence, proteins,
single-cell and omics, and drug discovery. It produces three things:
1. **Real experiments** on public data, preregistered, run on our machine, attacked by a skeptic.
2. **Field intelligence**: a living, honest map of papers, models, datasets, labs and companies.
3. **Opportunities**: things worth building, betting on, or doing next, each with evidence.

How work flows: the operator (or the chief, when idle) brings an idea; the chief triages it; the FIELD BRO
(genomics, proteins, cells or clinic) writes the prereg with its field's dossier; the data engineer gets the
data; the experimenter runs it; the skeptic attacks it; the field bro records the verdict; the chief turns
validated results into findings and opportunities. The SCOUT works continuously on field intelligence.

## Where things are
- `knowledge/`: the field map (INDEX.md links everything). `fields/<field>/DOSSIER.md`: one per field.
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
