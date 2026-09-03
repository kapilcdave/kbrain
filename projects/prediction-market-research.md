---
title: Prediction Market Research
type: project
status: completed
started: 2026
updated: 2026-09-03
tags: [prediction-markets, market-microstructure, calibration, quantitative-research]
source_repositories:
  - private:weather
  - private:sport
  - private:kalshi-scalp
---

# Prediction Market Research

## Summary

A multi-domain study of prediction-market pricing, execution, and capacity.
The work covered weather, sports, short-duration crypto, commodities, and
cross-venue relationships. Most apparent opportunities disappeared after
executable prices, fees, adverse selection, correlated observations, and data
leakage were handled.

## Question

Can public data identify repeatable prediction-market advantages that remain
positive after realistic execution costs?

## Method

The research used historical and forward observations, executable quotes,
venue-specific fees, clustered confidence intervals, chronological holdouts,
placebo tests, and preregistered decision rules. Models were evaluated against
market prices instead of weak constant baselines.

## Findings

- **Measured:** Short-duration crypto prices were strongly calibrated out of
  sample; directional models did not add enough value to clear costs.
- **Measured:** Weather markets contained small calibration effects, but their
  magnitude was generally below spread and fee costs.
- **Measured:** Maker simulations could look profitable until queue mechanics
  or actual fill selection were included.
- **Measured:** Several positives came from look-ahead data, settlement values
  mistaken for prices, loose joins, correlated samples, or post-hoc selection.
- **Inference:** Measurable inefficiency does not imply executable edge.
- **Conclusion:** Causal timing, execution realism, and falsification controls
  mattered more than model complexity.

## Limits

The conclusions apply to the venues, contracts, and periods tested. Market
structure can change. Private source archives are named for provenance but are
not copied into this repository.
