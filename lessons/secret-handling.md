---
title: Secret Handling for Agents
type: lesson
status: maintained
started: 2026-09
updated: 2026-09-16
tags: [security, secrets, ai-agents, credentials, operations]
source_repositories: []
---

# Secret Handling for Agents

An agent with shell access and a credential store has a disclosure surface that
a human at a terminal does not: every command, every diff, and every tool result
is written into a transcript that persists, gets replayed, and may be reviewed
by systems outside the original session. The mitigation is not care. It is
refusing to let values enter that channel at all.

## Never Read the File

Do not open a credential file to see what is in it. Inspect it instead, and
report only key names, set-or-empty status, value length, malformed line
numbers, and file permissions. That is enough to diagnose essentially every
configuration fault without a value ever existing in the transcript.

There is no safe preview. A prefix or suffix is still sensitive, and worse, a
partial value makes later rotation ambiguous — you can no longer tell which key
was exposed.

## Never Diff a Secret File

A unified diff includes surrounding context lines, so editing one key exposes
its neighbours. Writing the whole file back is worse: the complete credential
set enters the tool call. For a key rename, use a helper that performs the
operation atomically, preserves the value, forces restrictive permissions, and
prints only key names. For a new or rotated value, the value should be entered
locally or through a secret manager — never through the conversation, never as a
command argument.

## Validate Capability, Not Contents

The question worth answering is "does this credential work," and that is
answered by calling the cheapest read-only identity or health endpoint and
printing a status code plus a non-sensitive result. Avoid verbose HTTP modes,
shell tracing, and exception bodies, all of which can carry request headers.

A syntactically present key is not a working credential. Presence and function
must be checked separately.

## Separate Identifiers From Authority

A public address, an account identifier, and a signing key are three different
things and only the first is safely displayed. Presence of a private key is not
authorization to move anything: that requires an explicit instruction naming
source, network, asset, amount, destination, and worst-case fee.

Research API keys and signing keys belong in separate stores. A primary wallet
seed never belongs in an unattended process.

## When Disclosure Happens

Say so immediately, without repeating the value. Name the affected service and
key, stop any state-changing use of it, and treat rotation as required before
anything resumes. An internal-only diff is not harmless — transcripts,
approval records, and tool logs all extend the exposure boundary beyond the
session.

## A Note on Guardrails

Blocked commands around credential files are the guard working, not a failure to
route around. When a scanner refuses a command that names a secret path, the
answer is to reference the variable rather than the file, or to run a checked-in
script. It is not to find a phrasing that gets through.

## Related

- [`secret-config-operations`](../agents/kapilubot/skills/secret-config-operations)
  — the operational procedure and its inspection helper.
- [Production Safety](production-safety.md) — the same fail-closed reasoning
  applied to order flow.
