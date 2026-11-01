# kbrain

The brain of my trading: what I have built, tested, learned, rejected, and what is running now.

A team of agents (the pixel bros) works here continuously: standing desks for Kalshi recurring
markets, Hyperliquid, Gemini/Polymarket US, data and review, coordinated by a chief of staff. They
commit their notebooks, scripts and findings to this repo; the harness tests and merges to main.
Numbers, fills and P&L live here. Credentials, keys and raw tape data never do.

## Start Here

- **AI agents: read [AGENTS.md](AGENTS.md) first.**

- [About](ABOUT.md)
- [What I am focused on now](NOW.md)
- [Project index](PROJECTS.md)
- [Research methodology](METHODOLOGY.md)
- [2026 timeline](timeline/2026.md)

## Main Threads

### Research

- [Options Research](projects/options-research.md)
- [Prediction Market Research](projects/prediction-market-research.md)
- [Weather Markets](projects/weather-markets.md)
- [Sports Markets](projects/sports-markets.md)
- [DEX and Crypto Research](projects/dex-and-crypto-research.md)
- [Perpetual Maker Study](projects/perpetual-maker-study.md)

### Durable Findings

- [Market Efficiency](research/market-efficiency.md)
- [Fees and Adverse Selection](research/fees-and-adverse-selection.md)
- [Capacity Versus Edge](research/capacity-versus-edge.md)
- [Weather Station Proximity and the Tarmac Effect](research/weather-station-proximity.md)
- [Fake Edges From Data Bugs](lessons/fake-edges-from-data-bugs.md)
- [Preregistration](lessons/preregistration.md)
- [Production Safety](lessons/production-safety.md)
- [Secret Handling for Agents](lessons/secret-handling.md)
- [Negative Results](lessons/negative-results.md)

## Principles

1. The market price is a baseline to beat, not just another feature.
2. A backtest is a hypothesis generator until causal timing is established.
3. Executable prices, fees, fill selection, and capacity are part of the model.
4. Holdouts are consumable. Once viewed, they are no longer independent.
5. Nulls and retractions stay visible.
6. Credentials and raw data never enter git; everything else we learn does.

## Status Labels

- `active`: current work or a question still collecting evidence.
- `maintained`: usable project receiving occasional care.
- `experimental`: working system without validated outcome claims.
- `prototype`: proof of concept, not production infrastructure.
- `completed`: question answered for the tested scope.
- `closed`: frozen after a predefined failure condition.
- `archived`: retained for provenance rather than active development.

## Desks

Each desk keeps `desks/<desk>/NOTEBOOK.md` (state, findings, queue) and `desks/<desk>/OUTBOX.md`
(requests to other desks or to me). The office view (`core/bin/kb web`) shows them working.

## License

Unless a page says otherwise, original prose in this repository is licensed
under [CC BY 4.0](LICENSE.md). Linked source repositories retain their own
licenses.

Nothing here is financial advice.
