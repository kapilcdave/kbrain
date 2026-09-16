---
title: Agent Skills
type: project
status: active
started: 2026-09
updated: 2026-09-16
tags: [ai-agents, skills, procedures, knowledge-management, hermes]
source_repositories: []
---

# Agent Skills

## Summary

The procedural memory of my [Hermes agent](hermes-agent.md): versioned Markdown
files, each describing how to do one recurring class of task, loaded on demand
when the task appears. The published subset lives in [`agent/skills/`](../agent/skills).

## Why They Exist

A conversational agent starts every session with no memory of what went wrong
last time. Anything learned during a hard debugging session evaporates unless it
is written somewhere the agent will reliably re-read. Skills are that place. The
test of a good one is narrow: does it stop a specific mistake from recurring?

## Structure

Each skill is a directory:

```text
skill-name/
  SKILL.md          # frontmatter (name, description, tags) + the procedure
  references/       # deep material loaded only when relevant
  scripts/          # executable helpers
```

The description field is a trigger, not a summary. It states the situation in
which the skill should be loaded, because that is the only text visible when the
agent decides whether to open the file.

## What I Learned Writing Them

**Write lessons, not logs.** The first drafts were incident narratives: what
happened, in order, with dates. They were unusable. What works is an imperative
rule plus the reason it exists — "sort by RSS, not VSZ, because a VSZ figure can
overstate real usage by four orders of magnitude." One rule per lesson.

**The trigger is the hard part.** A correct procedure that never loads is dead
weight. Most of the editing effort goes into the first line, so the skill fires
on the situation rather than on a keyword I happened to use once.

**Split by depth, not by topic.** Everything in the main file is context the
agent pays for on every load. Long material belongs in `references/` behind an
explicit pointer, so the common case stays cheap and the rare case stays
available.

**Prefer a script over a prose instruction for anything exact.** A described
procedure drifts under paraphrase. A checked-in script does not. This matters
most where paraphrase is dangerous, such as credential handling.

**Skills decay and must be edited in place.** When a documented command turns
out to be wrong or incomplete, the fix belongs in the skill immediately, in the
same session. A skill library that is only ever appended to becomes a
collection of plausible-sounding stale advice.

## Published Skills

Nine are published here. They are self-contained, generally useful, and free of
private operational detail.

| Skill | What it covers |
| --- | --- |
| [`cloud-vm-maintenance`](../agent/skills/cloud-vm-maintenance) | Keeping a small VM lean: memory triage by RSS, disk reclamation, orphaned processes, self-reinstalling cloud agents, API latency measurement |
| [`evidence-first-research`](../agent/skills/evidence-first-research) | Testing research claims against explicit baselines, falsification criteria, and evidence gates |
| [`hermes-provider-diagnosis`](../agent/skills/hermes-provider-diagnosis) | Classifying model/provider failures: hard incompatibility vs transient capacity vs credentials, and why a health ping can pass on a broken route |
| [`kbrain-curation`](../agent/skills/kbrain-curation) | Turning private working context into durable public Markdown without mirroring raw state |
| [`multi-agent-chat-topologies`](../agent/skills/multi-agent-chat-topologies) | Wiring several agents into one shared channel without feedback loops |
| [`safe-agent-handoff`](../agent/skills/safe-agent-handoff) | Transferring work with explicit state, permissions, risks, and verification |
| [`secret-config-operations`](../agent/skills/secret-config-operations) | Editing credential files without leaking values into diffs, logs, or transcripts |
| [`trading-strategy-validation`](../agent/skills/trading-strategy-validation) | Falsifying a strategy or backtest before believing it — the largest skill, drawn from the research recorded elsewhere in this repository |
| [`verified-delivery`](../agent/skills/verified-delivery) | Carrying requested work through implementation, execution, and final-state verification |

`trading-strategy-validation` is the direct encoding of the methodology in
[METHODOLOGY.md](../METHODOLOGY.md) and the lessons under
[`lessons/`](../lessons). It exists because the same failure modes — accounting
bugs, weighting artifacts, self-credited spread, non-causal features — kept
reappearing in new markets wearing new clothes.

## Not Published

Skills that encode private deployment detail are excluded: repository-specific
operations, credential search paths, service layouts, and anything naming a
private host or account. The methodological content of those skills is
published; the operational content is not. This follows the
[publication boundary](../decisions/publication-boundary.md).

## Current Status

Active and growing. The library is edited more often than it is extended, which
I take as a sign it is being used rather than accumulated.
