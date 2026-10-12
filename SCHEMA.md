# Page Schema

Knowledge pages use YAML frontmatter so they remain useful as plain Markdown
and as input to indexing tools.

```yaml
---
title: Page title
type: project | research | lesson | decision | timeline | agent
status: active | maintained | experimental | prototype | completed | closed | archived
started: YYYY-MM-DD | YYYY-MM | YYYY | null
updated: YYYY-MM-DD
tags:
  - example
source_repositories:
  - https://github.com/owner/repository
---
```

## Content Rules

- One subject has one canonical page.
- Pages distinguish measured results, inference, and conclusion.
- Source links point to intentionally public material where possible.
- Private source archives may be named for provenance but are not reproduced.
- Dates describe the evidence window, not an implied promise of freshness.
- Retractions remain next to the claims they replace.
- `[[wikilinks]]` may be added later, but ordinary Markdown links remain the
  portable default.

## Exception: `agents/*/skills/`

Files under `agents/<handle>/skills/` are published verbatim as skill
definitions and keep their own tool-native frontmatter (`name`, `description`,
`version`, `tags`) instead of the page schema above. They are artifacts, not
knowledge pages. Their narrative context lives in
[projects/agent-skills.md](projects/agent-skills.md), which does follow the
schema.
