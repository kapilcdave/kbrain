# Khermes

Khermes is Kapil Dave's personal Hermes Agent. It is available on Telegram as
[@kapilebot](https://t.me/kapilebot) and acts as an execution agent, research
collaborator, coding agent, and continuity layer across projects.

## Public Agent Files

- [Identity](IDENTITY.md)
- [Voice and behavior](VOICE.md)
- [Operating principles](OPERATING-PRINCIPLES.md)
- [Capabilities](CAPABILITIES.md)
- [Installed skill inventory](SKILLS.md)
- [Memory policy](MEMORY.md)
- [Security boundary](SECURITY.md)
- [Synchronization policy](SYNC.md)

## Context

- [Hermes Agent](../projects/hermes-agent.md) — what the agent is, how it is
  shaped, and what running it has taught me.
- [Agent Skills](../projects/agent-skills.md) — how the procedural library is
  written and why.
- [`skills/`](skills) — the published skill files themselves.
- [Secret Handling for Agents](../lessons/secret-handling.md) — the disclosure
  rules that govern everything above.

## What Is Not Here

This is a curated public snapshot, not a deployable Hermes home directory. It
contains no tokens, chat identifiers, session transcripts, private paths,
hostnames, provider credentials, raw memories, logs, caches, or runtime state.
The bot name and username are public by construction; private deployment state
is not. The full rule is in the
[publication boundary](../decisions/publication-boundary.md).
