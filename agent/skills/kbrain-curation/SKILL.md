---
name: kbrain-curation
description: Curate durable public knowledge into kbrain safely.
version: 0.1.0
author: Kapil Dave (kapilcdave), Hermes Agent
license: CC-BY-4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-base, markdown, publishing, privacy]
    related_skills: []
---

# Kbrain Curation Skill

Turn private working context into durable public Markdown without mirroring raw
workspaces or agent state.

## When to Use

- Adding a project, research result, lesson, decision, or agent update to kbrain
- Consolidating repeated findings into one canonical page
- Publishing a correction or retraction

Do not use this skill to copy raw logs, transcripts, account data, or private
configuration.

## Procedure

1. Read `README.md`, `SCHEMA.md`, and `decisions/publication-boundary.md`.
   Completion criterion: the target page type and allowed evidence are clear.
2. Inspect the relevant canonical page and public sources. Completion criterion:
   every factual claim has a public source or is labeled as inference.
3. Rewrite the material as a standalone page with schema-compliant frontmatter.
   Completion criterion: no private source text is copied verbatim.
4. Link the page from the nearest index and remove duplicate claims elsewhere.
   Completion criterion: one subject has one canonical page.
5. Check Markdown, links, staged files, and secret-scan results. Completion
   criterion: all checks pass on the exact staged tree.
6. Commit, push, and verify the remote commit. Completion criterion: the remote
   default branch contains the expected commit and files.

## Pitfalls

- Redacting a private document is weaker than writing from an allowlist.
- Agent memory and conversation history are evidence inputs, not publishable pages.
- A successful push does not prove that the intended files reached the remote.

## Verification

Confirm schema fields, index links, clean secret scans, a clean working tree, and
the remote commit SHA.
