---
name: verified-delivery
description: Deliver working changes with end-to-end verification.
version: 0.1.0
author: Kapil Dave (kapilcdave), Hermes Agent
license: CC-BY-4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delivery, testing, git, verification]
    related_skills: []
---

# Verified Delivery Skill

Carry requested work through implementation, execution, and remote verification.
A plan or plausible output is not a substitute for a working artifact.

## When to Use

- Building or changing code, documents, repositories, or external records
- Running migrations, deployments, or publication workflows
- Any task where the user asked to verify the result

## Procedure

1. Discover prerequisites, repository state, and acceptance criteria. Completion
   criterion: every requested outcome maps to a concrete check.
2. Make the smallest complete change. Completion criterion: all intended files or
   records are accounted for and unrelated state is untouched.
3. Run the real artifact and relevant tests. Completion criterion: outputs come
   from execution, not fabricated examples.
4. Inspect the final diff or target record. Completion criterion: no accidental
   changes, secrets, or unresolved placeholders remain.
5. Apply the external change and read the exact target back. Completion criterion:
   remote state matches the intended payload.
6. Report what changed, what passed, and what remains. Completion criterion: every
   completion claim points to observed evidence.

## Pitfalls

- A successful command exit does not prove the system reached the intended state.
- Passing a narrow test does not validate untested acceptance criteria.
- Do not call a task done while a material verification step is still available.

## Verification

Use task-specific tests plus a final state read: repository SHA, deployed health
check, fetched record, rendered document, or equivalent authoritative evidence.
