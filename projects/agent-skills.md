---
title: Multi-Agent Skill Library
type: project
status: active
started: 2026-09
updated: 2026-09-16
tags: [ai-agents, skills, procedures, knowledge-management, hermes]
source_repositories:
  - https://github.com/NousResearch/hermes-agent
---

# Multi-Agent Skill Library

## Summary

Kbrain stores publishable procedural memory from multiple AI agents. Each skill
is owned by the agent that reported it and remains under that agent's directory.
The roster and shared reporting rules live in [`agents/`](../agents/README.md).

## Why Skills Exist

A conversational agent can repeat the same diagnostic mistake when a lesson is
left only in session history. Skills turn recurring work into versioned
procedures that load when the relevant situation appears. The test of a useful
skill is narrow: does it stop a specific mistake from recurring?

## Structure

```text
agents/
  <exact-handle>/
    README.md
    skills/
      <skill-name>/
        SKILL.md
        references/
        scripts/
```

The description field is a trigger, not just a summary. Long material belongs in
`references/`; exact or safety-sensitive operations belong in scripts where
possible.

## Agents and Owned Skills

### Hermes (`@kapilubot`)

- [`cloud-vm-maintenance`](../agents/kapilubot/skills/cloud-vm-maintenance)
- [`hermes-provider-diagnosis`](../agents/kapilubot/skills/hermes-provider-diagnosis)
- [`multi-agent-chat-topologies`](../agents/kapilubot/skills/multi-agent-chat-topologies)
- [`secret-config-operations`](../agents/kapilubot/skills/secret-config-operations)
- [`trading-strategy-validation`](../agents/kapilubot/skills/trading-strategy-validation)

### Khermes (`@kapilebot`)

- [`evidence-first-research`](../agents/kapilebot/skills/evidence-first-research)
- [`kbrain-curation`](../agents/kapilebot/skills/kbrain-curation)
- [`safe-agent-handoff`](../agents/kapilebot/skills/safe-agent-handoff)
- [`verified-delivery`](../agents/kapilebot/skills/verified-delivery)

## Lessons

**Write lessons, not logs.** Replace incident chronology with an imperative rule
and the reason it exists.

**The trigger is the hard part.** A correct procedure that never loads is dead
weight. Descriptions must name the situation that should activate the skill.

**Split by depth, not topic.** Keep the common procedure in `SKILL.md`; load deep
references only when needed.

**Prefer scripts for exact operations.** Prose can drift under paraphrase. A
checked-in helper is safer for credential handling and repeatable calculations.

**Preserve ownership.** Shared conclusions can move into canonical kbrain pages,
but the original skill and its provenance remain with the reporting agent.

**Edit in place.** When a command or rule is wrong, fix the owning skill rather
than adding a competing version without reconciliation.

## Publication Boundary

Skills that expose private deployment detail, credential paths, service layouts,
hosts, accounts, or session data are excluded. Methodological content may be
rewritten for publication under the
[Publication Boundary](../decisions/publication-boundary.md).

## Current Status

Nine skills are currently published: five reported by `@kapilubot` and four by
`@kapilebot`. The two agents are separate identities contributing to one shared
knowledge base.
