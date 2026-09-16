---
name: evidence-first-research
description: Test research claims against explicit evidence gates.
version: 0.1.0
author: Kapil Dave (kapilcdave), Hermes Agent
license: CC-BY-4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, evidence, falsification, citations]
    related_skills: []
---

# Evidence-First Research Skill

Investigate a claim with explicit baselines, falsification criteria, and
traceable sources. This skill produces a bounded conclusion, not advocacy.

## When to Use

- Evaluating a strategy, product thesis, model, or causal claim
- Reconciling conflicting findings
- Converting exploratory analysis into a durable conclusion

## Procedure

1. State the claim, decision it informs, baseline, and failure condition.
   Completion criterion: a negative result is possible before data is inspected.
2. Prefer primary sources and record the evidence window. Completion criterion:
   every material fact has a traceable source and date.
3. Separate observation, inference, and conclusion. Completion criterion: no
   inferred mechanism is written as a measurement.
4. Test timing, leakage, costs, selection effects, and alternative explanations.
   Completion criterion: each plausible invalidation is addressed or left open.
5. Report scope, uncertainty, and what evidence would change the conclusion.
   Completion criterion: the result cannot be mistaken for a universal claim.
6. Preserve negative results and corrections. Completion criterion: failed paths
   remain searchable and prevent repeated work.

## Pitfalls

- Statistical significance does not establish executable value or causality.
- A market price, benchmark, or simple heuristic may be the strongest baseline.
- Once a holdout is inspected, it is no longer independent.

## Verification

Check citations, evidence dates, baseline results, falsification criteria, and
the boundary between measured and inferred claims.
