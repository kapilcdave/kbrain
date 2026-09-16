# agent

Material about the AI agent I operate, `@kapilubot` — a Hermes Agent instance
running as a Telegram bot on a small Linux VM.

- [Hermes Agent](../projects/hermes-agent.md) — what it is, how it is shaped,
  and what running it has taught me.
- [Agent Skills](../projects/agent-skills.md) — how the procedural library is
  written and why.
- [`skills/`](skills) — the published skill files themselves.
- [Secret Handling for Agents](../lessons/secret-handling.md) — the disclosure
  rules that govern everything above.

## What Is Not Here

No tokens, chat identifiers, session transcripts, private paths, hostnames, or
provider credentials. The bot username is public by construction; nothing else
about the deployment is. The full rule is in the
[publication boundary](../decisions/publication-boundary.md).
