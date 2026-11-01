# kbrain

My research brain for **bio x AI**: genomics and DNA, proteins, single-cell and omics, and drug discovery.

A small team of agents (the pixel bros) does three things:

1. **Experiments.** Preregistered computational experiments on public data: an idea, a fixed held-out split,
   a strong baseline, code-graded results per independent unit, then a skeptic tries to break it.
2. **Field intelligence.** A living map of what is real in the field: models, datasets, labs, companies,
   with a hype-versus-evidence call on each.
3. **Opportunities.** Things worth building, betting on, or doing next, each with evidence.

## Start here

- **AI agents: read [AGENTS.md](AGENTS.md) first.**
- [What I am focused on now](NOW.md)
- [Knowledge index](knowledge/INDEX.md): fields, models, datasets, labs, candidates, opportunities, findings
- [Methodology](METHODOLOGY.md) and [lessons](lessons/)

## How it runs

```
idea (me: core/bin/kb idea "...", or the chief when idle)
  -> chief triage -> field bro (genomics | proteins | cells | clinic) writes the prereg with its dossier
  -> data engineer -> experimenter -> skeptic -> field bro records the verdict
  -> chief writes the finding and the opportunity; anything that costs money comes to me
scout: works continuously on field intelligence and candidate experiments
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
