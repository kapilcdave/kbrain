---
title: Hedge Router
type: project
status: experimental
started: 2026
updated: 2026-09-03
tags: [ai-infrastructure, telemetry, forecasting, privacy, nodejs]
source_repositories:
  - https://github.com/kapilcdave/hedge-router
---

# Hedge Router

## Summary

A gateway-neutral research tool that converts model-usage telemetry into
compute-exposure measurements and evaluates paper hedges against compute-price
markets.

## Why I Built It

Model gateways expose tokens, provider mix, cost, latency, errors, and
failovers. I wanted to explore whether those operational measurements could
also describe an organization's exposure to changing compute prices.

## What I Built

Hedge Router normalizes supported gateway and OpenTelemetry exports into a
local ledger, produces daily demand features, and runs walk-forward forecasts
against public compute-price data. It includes paper accounting, settlement,
evaluation, a resumable pilot, a dashboard, and editor status integrations.

Its normalization boundary deliberately excludes prompts, completions, code,
paths, credentials, and direct user identifiers.

## What I Learned

A compute-price contract is not automatically a useful hedge. Customer cost
must move with the contract's settlement index, making basis risk central.
Evaluation also needs horizon alignment, independent settlements, realistic
costs, and an explicit insufficient-data outcome.

## Current Status

Experimental and paper-only. The repository contains no live order path.

## Sources

- [Repository](https://github.com/kapilcdave/hedge-router)
- [README](https://github.com/kapilcdave/hedge-router/blob/main/README.md)
