---
title: Publication Boundary
type: decision
status: maintained
started: 2026-09-03
updated: 2026-09-03
tags: [privacy, security, publishing]
source_repositories: []
---

# Publication Boundary

Public release is allowlist-first. Material remains private unless it belongs to
an approved category and passes a separate safety review.

## Allowed

- General research questions and falsification criteria
- Methodology and data-quality lessons
- High-level project chronology
- Aggregate results derived from public data
- Negative results, corrections, and retractions
- Public rules, fee formulas, and settlement mechanics
- Architecture without private deployment details
- Synthetic examples and links to primary public documentation

## Excluded

- Credentials, tokens, keys, cookies, signatures, or environment contents
- Private paths, hostnames, device details, or network topology
- Account identifiers, balances, positions, orders, fills, or operating status
- Raw journals, authenticated responses, and browser sessions
- Private deployment configuration and unresolved vulnerabilities
- Personal information not already intentionally public
- Third-party material without redistribution rights
- Internal handoffs copied verbatim
- Claims based only on indicative prices or unreconciled state

## Review

1. Select from the allowlist instead of redacting a private document.
2. Rewrite the finding rather than copying operational notes.
3. Remove paths, commands, identifiers, and current-state information.
4. Verify source rights and attribution.
5. Scan the exact staged tree and resulting Git history.
6. Keep retractions next to superseded claims.
7. Review rendered output and attachments.
8. Publish only explicitly reviewed files.

When uncertain, publish the methodological lesson and exclude the sensitive
evidence.
