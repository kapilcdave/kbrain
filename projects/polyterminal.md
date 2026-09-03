---
title: Polyterminal
type: project
status: experimental
started: 2026
updated: 2026-09-03
tags: [prediction-markets, terminal-ui, market-data, python]
source_repositories:
  - https://github.com/kapilcdave/polyterminal
---

# Polyterminal

## Summary

A read-only terminal application for comparing active Kalshi and Polymarket
prediction markets.

## Why I Built It

Equivalent questions can trade on multiple venues, but matching them requires
more than similar titles. I wanted a compact view that remained conservative
about whether two contracts were genuinely comparable.

## What I Built

Polyterminal combines REST snapshots with live market-data streams in a Textual
interface. Its matcher checks entities, dates, numbers, and direction rather
than allowing text similarity to override incompatible contract structure.

The application supports visibly labeled mock data and never places orders.

## What I Learned

Cross-venue matching is primarily a contract-semantics problem. Threshold,
direction, entity, timing, and settlement-source differences create dangerous
false positives. Missing feeds should remain visibly unavailable instead of
being silently replaced.

## Current Status

Alpha software with packaging, CI, security guidance, and read-only boundaries.

## Sources

- [Repository](https://github.com/kapilcdave/polyterminal)
- [Security policy](https://github.com/kapilcdave/polyterminal/blob/master/SECURITY.md)
