---
title: DEX and Crypto Research
type: project
status: active
started: 2026
updated: 2026-09-03
tags: [crypto, dex, arbitrage, derivatives, market-structure]
source_repositories:
  - private:crypto-grid-research
---

# DEX and Crypto Research

## Summary

Research covering decentralized-exchange arbitrage, liquid-staking-token
redemption, funding carry, liquidity provision, crypto prediction markets, and
options. The tested price-gap arbitrage families were closed. Persistent returns
were compensation for funding, liquidity, credit, or tail risk, while some
options questions remain open.

## Method

The analysis used executable quotes, same-block comparisons, canonical on-chain
state, depth-matched centralized-exchange books, long funding histories, and
explicit transaction-cost models.

## Findings

- **Measured:** Synchronized cross-DEX and CEX-to-DEX scans found no positive
  arbitrage after fees.
- **Measured:** Liquid-staking-token discounts closely tracked their governing
  redemption costs.
- **Measured:** Funding premia were highly sensitive to regime, collateral,
  capacity, and the cost of sourcing the hedge.
- **Measured:** Deep major-asset carry approached cash alternatives, while
  higher premia appeared where capacity or hedging was harder.
- **Conclusion:** The viable object was compensated risk-bearing, not riskless
  arbitrage.

## Limits

Measurements cover selected venues, chains, pairs, and windows. Funding can
reverse, historical options data may underrepresent future tails, and displayed
depth can disappear. The arbitrage conclusions are complete for their frozen
scope; the broader crypto research program is not.
