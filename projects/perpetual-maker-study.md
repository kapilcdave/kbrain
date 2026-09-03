---
title: Perpetual Maker Study
type: project
status: closed
started: 2026
updated: 2026-09-03
tags: [perpetual-futures, market-making, preregistration, adverse-selection]
source_repositories:
  - private:kalshi-perps
---

# Perpetual Maker Study

## Summary

A frozen, preregistered test of passive market making on six perpetual-futures
markets with flat maker fees.

## Method

Seven days of raw market data were rebuilt into a clean evaluation set. The
registered analysis compared optimistic front-of-queue and pessimistic
back-of-queue bounds, checked chronological halves, and required every gate to
pass before a canary could be armed.

## Result

All six assets failed. Even the optimistic queue bound was negative after maker
fees, both time halves were negative, and the anti-control supported adverse
selection rather than a measurement inversion.

The canary was never activated. No capital was deployed by the study.

## Lesson

Wide spreads were compensation for toxic flow, not unclaimed revenue. Because
the rules were frozen before evaluation, the correct outcome was closure rather
than retuning the same sample.

## Reopening Rule

A future test would require a materially changed venue mechanism, a new
preregistration, and an untouched data window.
