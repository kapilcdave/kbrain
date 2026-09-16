---
name: safe-agent-handoff
description: Transfer agent work with explicit state and safety gates.
version: 0.1.0
author: Kapil Dave (kapilcdave), Hermes Agent
license: CC-BY-4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, handoff, coordination, safety]
    related_skills: []
---

# Safe Agent Handoff Skill

Transfer work between agents without confusing hypotheses, completed work, and
authorization. The handoff is a state summary, not a dump of hidden context.

## When to Use

- Moving a project or experiment to another agent
- Delegating an independent workstream
- Resuming work after a long interruption

## Procedure

1. Name the owner, objective, repository, branch, and evidence window. Completion
   criterion: the recipient can locate the intended public artifacts.
2. Separate completed work, open questions, failed paths, and proposed next steps.
   Completion criterion: no proposal is presented as executed work.
3. State permissions and prohibitions explicitly. Completion criterion: financial,
   destructive, production, and publishing authority cannot be inferred.
4. Include reproducible verification commands or checks without credentials.
   Completion criterion: the recipient can independently confirm current state.
5. Record dependencies, risks, and stop conditions. Completion criterion: the
   recipient knows when not to proceed.
6. Ask the receiving agent to verify the handoff before acting. Completion
   criterion: mismatches are resolved against the source of truth.

## Pitfalls

- Commit messages alone are too hidden for operational handoffs.
- Raw transcripts contain noise and private material; summarize instead.
- Ownership transfer does not grant deployment, trading, spending, or publishing
  authority unless the handoff says so explicitly.

## Verification

Confirm that referenced artifacts exist, the stated branch and commit match the
repository, and permissions are explicit.
