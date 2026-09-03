---
title: Options Research
type: project
status: active
started: 2026
updated: 2026-09-03
tags: [options, quantitative-research, backtesting, python]
source_repositories:
  - https://github.com/kapilcdave/floor-insurance-bot
---

# Options Research

## Summary

A collection of options experiments, paper-execution tools, and risk controls
built to reject weak ideas before live deployment.

## Why I Built It

Simple options rules often hide unrealistic assumptions about fills, contract
sizing, data quality, and maximum loss. I wanted a process that measured those
assumptions directly and preserved failed results.

## What I Built

The repository contains chronologically split studies of directional spreads,
volatility structures, option flow, relative-value butterflies, constituent
signals, conformal forecasts, and dynamic hedging. It also includes
broker-reconciled paper workflows, conservative quote handling, atomic
multi-leg construction, risk limits, and append-only research records.

## What I Learned

Most tested strategies failed after realistic costs or validation. A recurring
failure was using the same option print for signal selection and assumed entry;
holding the signal fixed while delaying execution could reverse the result.

Options are indivisible contracts, calibrated forecasts do not guarantee a
tradeable pricing edge, and small accounts can create concentrated risk even
with nominally defined-loss structures.

## Current Status

Research and paper operation remain the defaults. The public evidence does not
establish a validated live strategy.

## Sources

- [Repository](https://github.com/kapilcdave/floor-insurance-bot)
- [Research documentation](https://github.com/kapilcdave/floor-insurance-bot/tree/main/docs)
