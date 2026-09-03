---
title: Narrative Momentum
type: project
status: experimental
started: 2026
updated: 2026-09-03
tags: [financial-data, llm, edgar, rss, python]
source_repositories:
  - https://github.com/kapilcdave/effective-octo-barnacle
---

# Narrative Momentum

## Summary

An experimental pipeline that turns filings and selected news feeds into
structured catalyst signals and research reports.

## What I Built

The pipeline collects SEC filings and RSS stories, deduplicates them, and stores
them in SQLite. A language model extracts constrained fields such as ticker,
sector, sentiment, catalyst type, urgency, and a short thesis. The scorer groups
related mentions, applies time decay, and records candidates. A generated digest
tracks subsequent outcomes.

Separate modules support manual previews and paper workflows with quote,
liquidity, sizing, and exit checks.

## What I Learned

Document pipelines need strict schemas and validation around model output.
Source attribution is easy to corrupt, and ticker-like words create false
matches. Narrative scores remain hypotheses until evaluated on unseen data with
realistic execution assumptions.

## Current Status

Working experimental pipeline without established predictive performance.

## Sources

- [Repository](https://github.com/kapilcdave/effective-octo-barnacle)
