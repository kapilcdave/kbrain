---
title: Fake Edges From Data Bugs
type: lesson
status: maintained
started: 2026
updated: 2026-09-03
tags: [data-quality, leakage, backtesting]
source_repositories: []
---

# Fake Edges From Data Bugs

The largest apparent opportunities were often created by data handling rather
than markets. Many survived ordinary significance tests because the same bug
affected thousands of rows consistently.

| Failure | How it creates an edge | Defense |
|---|---|---|
| Look-ahead bars | Includes information published after the decision | Require source time strictly before decision time |
| Settlement as price | Treats the outcome as a historical quote | Use point-in-time pre-event quotes |
| Rolling-label leakage | Includes the observation being predicted | Pin window endpoints with fixtures |
| Wrong time semantics | Confuses nominal and actual cutoffs | Verify fields against observed behavior |
| Truncated history | Omits the execution period silently | Assert timestamped coverage |
| Loose joins | Combines different contracts | Join on canonical identity and settlement |
| Non-chronological fills | Counts a later state as an earlier fill | Replay in event order |
| Row weighting | Lets frequently updated markets dominate | Weight by the independent event |
| Grid-searched exits | Selects and scores on one sample | Freeze and evaluate once on unseen time |
| Schema fallback | Turns missing fields into zero | Fail loudly on required fields |
| Unit or sign error | Produces plausible totals in the wrong direction | Test identities and dimensions |
| Degenerate clustering | Labels row bootstrap as clustered | Report cluster counts and sizes |

## Warning Signs

- Enforcing causality destroys most of the result.
- Profit improves when execution assumptions get worse.
- One join, field, or fee sign explains the entire result.
- A confidence interval excludes its own point estimate.
- Near-perfect prediction appears in a noisy market.
- A narrow row-level interval accompanies extreme time concentration.

When fixing the data destroys the alpha, the alpha was the bug.
