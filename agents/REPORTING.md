# Agent Reporting Protocol

Kbrain accepts reports from multiple agents. A report must preserve who did the
work, what actually happened, and what authority remains with Kapil.

## Report for Duty

Use this header when an agent begins or resumes a workstream:

```text
Agent: <display name> (@exact_handle)
Assignment: <bounded objective>
Status: active | blocked | handed-off | completed
Owned artifacts: <paths or public URLs>
Authority: <what the agent may and may not do>
```

## Completion Report

A completed report states:

- **Agent:** exact identity and handle
- **Changed:** files, records, or external targets changed
- **Verified:** commands, tests, checks, and remote state actually observed
- **Open:** unresolved questions or known limitations
- **Handoff:** next owner, permissions, prohibitions, and stop conditions

## Shared-Repository Discipline

1. Fetch before editing and again before pushing.
2. Keep agent-specific material under `agents/<handle>/`.
3. Put shared findings in canonical kbrain pages and cite the reporting agent
   where provenance matters.
4. Never rewrite another agent's identity to match the current speaker.
5. Reconcile concurrent commits rather than deleting the other agent's work.
6. Verify the exact remote commit after pushing.

## Safety Boundary

A report never includes credentials, Telegram IDs, private paths, session
transcripts, raw memory, account activity, or deployment secrets. Publication is
allowlist-first under the [Publication Boundary](../decisions/publication-boundary.md).
