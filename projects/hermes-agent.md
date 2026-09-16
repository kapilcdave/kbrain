---
title: Khermes (@kapilebot)
type: project
status: active
started: 2026-09
updated: 2026-09-16
tags: [ai-agents, hermes, telegram, automation, skills, tooling]
source_repositories:
  - https://github.com/NousResearch/hermes-agent
---

# Khermes (@kapilebot)

## Summary

Khermes is a persistent Hermes Agent instance I run as my always-on operator: a
Telegram bot (`@kapilebot`, display name "Khermes") backed by a gateway
process on a small Linux VM. It is the interface through which most of my
research, ops, and publishing work now passes.

## Why I Run It

Most of my work is the same three motions repeated: inspect a system, run an
experiment, and write down what was actually true afterward. Those motions are
worth encoding once rather than re-deriving each session. The agent gives me a
single conversational surface with shell access, file access, scheduled jobs,
and a growing library of written procedures, so a lesson learned during one
investigation is available during the next one.

## Shape of the System

- **Gateway.** A Python process holding sessions, routing model calls, and
  scaling to zero when idle. Configuration is managed through a CLI rather than
  hand-edited, because a malformed provider block silently reroutes every call.
- **Surface.** Telegram (`@kapilebot`) is the primary channel; a local CLI is
  the fallback when the gateway itself is the thing being debugged.
- **Providers.** A default model plus a fallback chain. Fallback is turn-scoped:
  the primary is retried fresh on each new message, so a persistently broken
  primary re-invokes fallback every turn.
- **Skills.** Versioned Markdown procedures loaded on demand. See
  [Agent Skills](agent-skills.md).
- **Safety guard.** A command scanner sits between the agent and the shell. It
  blocks destructive or unresolvable command bodies before execution rather than
  trusting a benign-looking outer command.

## What I Learned

**Written procedure beats model recall.** The durable win is not a smarter
model, it is a checked-in procedure that names the specific trap. A skill that
says "this exact endpoint rejects assistant prefill, reroute instead of waiting"
converts a recurring half-hour of rediscovery into a lookup.

**The failure classes are not interchangeable.** A `400` from an unsupported
feature and a `429` from capacity look identical in a user report and require
opposite responses. Waiting fixes one and never fixes the other. Most wasted
agent-debugging time comes from treating a hard incompatibility as transient.

**A probe that does not reproduce the real request path proves nothing.** A
one-shot health ping succeeds on routes where every real multi-turn request
fails, because the ping omits the message shape that triggers the fault. A green
probe against the wrong path is worse than no probe.

**Security guards produce misleading error text.** The command scanner rejects
inline multi-line interpreter payloads and shell heredocs, and the resulting
message can look like an unrelated infrastructure failure. Writing the same
logic to a file and executing the file passes. I lost real time diagnosing a
"broken gateway" that was a correctly functioning scanner.

**Some operations must be handed back to a human shell.** The agent cannot
restart its own gateway from inside a gateway-hosted session, because the signal
propagates to the child and kills the restart mid-flight. This is a design
constraint, not a bug; the right output is the exact command for me to run
elsewhere, with all config changes already applied so one restart collects them.

**Secrets need a value-blind workflow.** Reading a credential file, diffing it,
or rewriting it all pull values into a transcript that outlives the task. The
working pattern is inspection that reports key names, set/empty status, and
length only, plus key-only renames performed by a helper script. See
[Secret Handling for Agents](../lessons/secret-handling.md).

## Current Status

Active and in daily use. The interesting artifact is not the deployment, which
is ordinary, but the accumulated skill library and the operating constraints
above.

## Public Boundary

This page describes architecture and lessons. Tokens, chat identifiers, private
paths, hostnames, provider credentials, and session contents are excluded under
the [publication boundary](../decisions/publication-boundary.md). The bot
username is public by construction: anyone can resolve it on Telegram.

## Sources

- Operating experience with this instance, September 2026.
- [Agent Skills](agent-skills.md) — the published subset of the skill library.
- [Public agent files](../agent/README.md) — identity, behavior, capabilities,
  memory policy, skill inventory, and security boundary.
