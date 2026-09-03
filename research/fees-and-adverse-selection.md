---
title: Fees and Adverse Selection
type: research
status: completed
started: 2026
updated: 2026-09-03
tags: [fees, adverse-selection, execution, market-making]
source_repositories: ["private:weather", "private:sport", "private:kalshi-scalp"]
---

# Fees and Adverse Selection

## Summary

Execution costs repeatedly dominated small predictive effects. Crossing paid
explicit fees and spreads; resting avoided those costs but selected fills more
likely to move against the order.

## Findings

- **Measured:** In one large short-duration sample, apparent spread capture was
  smaller than subsequent adverse price movement.
- **Measured:** Crossing beat resting in every weather archive and price-band
  comparison tested.
- **Measured:** A positive sports maker reconstruction reversed when realistic
  queue selection was modeled.
- **Measured:** Fees were largest near balanced probabilities, where many
  calibration effects were easiest to express.
- **Inference:** Wide spreads often compensate makers for informed or one-sided
  flow rather than offering free revenue.
- **Conclusion:** Passive execution is a separate empirical hypothesis, not a
  cost-free implementation detail.

## Limits

Historical tape does not always recover exact queue position. Fee schedules and
incentives can change. Markout measures execution quality, not total strategy
profitability.
