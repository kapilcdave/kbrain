---
title: Sports Markets
type: project
status: active
started: 2026
updated: 2026-09-03
tags: [sports, prediction-markets, baseball, tennis, market-efficiency]
source_repositories:
  - private:sport
---

# Sports Markets

## Summary

Research across baseball, tennis, basketball, and cross-market consistency.
Standard models and public game information were usually already reflected in
prices, and several intuitive premises were rejected before trading logic was
considered.

## Method

Tests used settled outcomes, fixed pregame observation times, executable
quotes, game-level clustering, causal features, and model-free arbitrage
identities. Discovery and holdout periods were separated where possible.

## Findings

- **Measured:** Pregame baseball prices remained tightly quoted and showed no
  robust stale-line or calibration gradient after controls.
- **Measured:** Late baseball innings scored less, not more, in the season
  studied, reversing the motivating intuition.
- **Measured:** Baseball and tennis reference models could reproduce prices but
  did not improve on them enough to trade.
- **Measured:** Thousands of internal consistency relations were respected or
  missed profitability by at least the execution toll.
- **Inference:** The strongest sports books behave like jointly maintained
  probability surfaces, not independent opinions.

## Limits

Some series have short histories, and public score feeds can lag prices. A
small number of specialized products remain less studied than flagship books.
Some headline reports survive while their ignored raw inputs do not, so those
results are historical evidence rather than fully reproducible packages.
