---
title: Agent Memory Coordination
type: project
status: prototype
started: 2026
updated: 2026-09-03
tags: [ai-agents, coordination, mcp, redis, typescript]
source_repositories:
  - https://github.com/kapilcdave/agent-memory-coordination
---

# Agent Memory Coordination

## Summary

A prototype shared-memory and conflict-detection layer for AI agents working in
parallel.

## Why I Built It

Files and Git preserve completed work, but they do not provide real-time
awareness of what several agents intend to change. I wanted to test whether
agents could declare semantic scopes before acting and receive warnings when
their plans overlap.

## What I Built

The TypeScript service stores scoped state and expiring agent intents in Redis.
It detects direct file collisions, possible semantic overlap, and simple
dependency risks. It includes server-sent conflict notifications, a dashboard,
a parser for pre-tool-call intent, and an MCP-compatible wrapper.

## What I Learned

Exact file collisions are straightforward. Semantic conflicts are harder. The
prototype uses lightweight similarity and filename heuristics, so inferred
intent is an early warning rather than ground truth. Tool calls and resulting
changes still need reconciliation.

## Current Status

Version `0.1.0` is a proof of concept. The core flow exists, but predictive
accuracy and production-scale coordination are not established.

## Sources

- [Repository](https://github.com/kapilcdave/agent-memory-coordination)
- [README](https://github.com/kapilcdave/agent-memory-coordination/blob/main/README.md)
