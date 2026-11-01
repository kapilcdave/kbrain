---
title: Production Safety
type: lesson
status: maintained
started: 2026
updated: 2026-09-03
tags: [production, safety, trading-systems, operations]
source_repositories: []
---

# Production Safety

A statistically promising strategy is not ready for production. Deployment
introduces state, concurrency, stale responses, partial fills, restarts, and
ambiguous network outcomes that a backtest does not contain.

## Default to Inert

Research tools should be read-only or paper-only. Live capability belongs in a
small isolated surface requiring explicit arming. Without that action, no
mutating request should be possible.

## Bound Aggregate Exposure

Limits must include accepted and resting orders, unreflected fills, in-flight
placements, repeated requotes, correlated events, total exposure, and losses
across restarts. A per-request cap can still fail when decisions overlap.

## Fail Closed

Stop on corrupt state, uncertain order status, failed reconciliation, active
kill switches, missing risk fields, breached floors, or rejected order
constraints. Unknown is not the same as rejected.

## Preserve Evidence

Write append-only decisions before submission, use idempotent client identifiers,
and reconcile against venue records. Shutdown should cancel outstanding orders,
and supervisors must not restart through strategy-level circuit breakers.

## Promote in Stages

1. Read-only collection
2. Historical replay
3. Frozen paper forward test
4. Dry-run integration
5. Small supervised canary
6. Venue reconciliation
7. Gradual changes only after predefined gates

A profitable canary does not authorize immediate scaling.
