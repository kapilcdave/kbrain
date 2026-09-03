---
title: Weather Markets
type: project
status: completed
started: 2026
updated: 2026-09-03
tags: [weather, prediction-markets, calibration, forecasting]
source_repositories:
  - private:weather
---

# Weather Markets

## Summary

Research into temperature-bucket markets tested numerical forecasts,
station-specific calibration, implied distributions, cross-venue pricing, and
execution methods. Reproducible calibration effects did not become robust
after-cost trades.

## Method

The study reconstructed bucket distributions, compared forecasts with
settlements, and evaluated trades at executable offers with fees. Tests used
chronological holdouts, unseen locations, event-level clustering, and
station-level persistence analysis.

## Findings

- **Measured:** Newly listed bucket distributions were often too flat, with the
  highest-probability bucket underweighted and distant buckets overweighted.
- **Measured:** The corresponding trade failed after executable prices and
  costs, including in out-of-sample evaluation.
- **Measured:** Some station-specific calibration bias persisted through time,
  but the trade was fragile to small adverse fills.
- **Measured:** Resting execution underperformed crossing across every tested
  archive and price-band comparison because fills selected worse outcomes.
- **Conclusion:** Real weather-market bias was smaller than the cost of reliably
  harvesting it.

## Limits

Weather contracts depend on exact station, observation window, and settlement
rules. Historical candles do not fully reveal depth or queue position. Archived
latency effects are not executable without a sufficiently timely source.
