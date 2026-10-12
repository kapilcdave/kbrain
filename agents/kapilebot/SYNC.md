# Synchronization Policy

Kbrain stores a curated public projection of Khermes, not a bidirectional mirror
of the live agent.

## Source of Truth

- Live runtime state stays in Hermes Agent.
- Durable public knowledge stays in kbrain.
- Reusable public procedures live as skill files under this directory.
- Upstream Hermes implementation and bundled skills remain in the
  [Hermes Agent repository](https://github.com/NousResearch/hermes-agent).

## Update Procedure

1. Inventory the live agent's public identity, SOUL, and skill names.
2. Rewrite durable changes into these Markdown files.
3. Exclude credentials, sessions, raw memories, logs, and machine state.
4. Validate every skill file and Markdown link.
5. Scan the staged tree for secrets.
6. Commit, push, and verify the remote commit.

## Why This Is Not a Full Copy

A full Hermes home directory contains sensitive and ephemeral data. Copying it
would violate kbrain's publication boundary and make the knowledge base harder
to use. This projection keeps the parts that are portable, reviewable, and
useful over time.
