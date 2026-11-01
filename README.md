# kbrain

A small research firm run by agents (the pixel bros), committed to **one niche: predicting what a single
amino-acid mutation does to a protein**, scored on [ProteinGym](https://proteingym.org) (217 deep mutational
scanning assays). We run on 8 CPU cores and no GPU, so our edge is cheap, clever methods and honest evaluation:

1. **Experiments.** Preregistered, scored only by the trusted lab ([`lab/proteingym.py`](lab/proteingym.py)),
   compared with the published leaderboard on the same assays, then attacked by a skeptic.
2. **Field intelligence.** What is real in mutation-effect prediction and protein engineering right now.
3. **Opportunities.** Where this matters: protein engineering with few measurements, tools worth building.

## Start here

- **AI agents: read [AGENTS.md](AGENTS.md) first.**
- [What I am focused on now](NOW.md)
- [Knowledge index](knowledge/INDEX.md): the niche dossier, models, datasets, candidates, opportunities, findings
- [The lab](lab/proteingym.py): the only evaluator results may use
- [Methodology](METHODOLOGY.md) and [lessons](lessons/)

## How it runs

```
idea (me: core/bin/kb idea "...", or the chief when idle)
  -> chief triage -> the mutation-effects lead writes the prereg with its dossier
  -> data engineer -> experimenter -> skeptic -> field bro records the verdict
  -> chief writes the finding and the opportunity; anything that costs money comes to me
scout: works continuously on the niche's literature and candidate experiments
```

Engine, roles and routing live in [`core/`](core/README.md). `core/bin/kb web` shows the bros at work.
The machine is 8 CPU cores, ~7 GB RAM and no GPU, so experiments are sized for that until I approve cloud runs.

## Archive

My earlier trading research (Kalshi, Hyperliquid, Gemini, Polymarket US) is kept in
[`archive/trading/`](archive/trading/).

## License

Unless a page says otherwise, original prose in this repository is licensed
under [CC BY 4.0](LICENSE.md). Linked source repositories retain their own
licenses.

Nothing here is medical advice.
