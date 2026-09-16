# Installed Skill Inventory

_Snapshot: September 16, 2026._

Khermes currently has 62 installed skill definitions. This page stores
only names and short capability descriptions. The skill bodies remain with their
upstream distributions unless they were written specifically for kbrain.

## Apple

- **apple-notes** — Manage Apple Notes via memo CLI: create, search, edit.
- **apple-reminders** — Apple Reminders via remindctl: add, list, complete.
- **findmy** — Track Apple devices/AirTags via FindMy.app on macOS.
- **imessage** — Send and receive iMessages/SMS via the imsg CLI on macOS.

## Autonomous Ai Agents

- **claude-code** — Delegate coding to Claude Code CLI (features, PRs).
- **codex** — Delegate coding to OpenAI Codex CLI (features, PRs).
- **computer-use** — Drive the desktop background-first; escalate on signal.
- **hermes-agent** — Use, configure, theme, extend, and orchestrate Hermes
  Agent.
- **opencode** — Delegate coding to OpenCode CLI (features, PR review).

## Creative

- **architecture-diagram** — Dark-themed SVG architecture/cloud/infra diagrams
  as HTML.
- **ascii-video** — ASCII video: convert video/audio to colored ASCII MP4/GIF.
- **baoyu-infographic** — Infographics: 21 layouts x 21 styles (信息图, 可视化).
- **claude-design** — Design one-off HTML artifacts (landing, deck, prototype).
- **design-md** — Author/validate/export Google's DESIGN.md token spec files.
- **humanizer** — Humanize text: strip AI-isms and add real voice.
- **manim-video** — Manim CE animations: 3Blue1Brown math/algo videos.
- **p5js** — p5.js sketches: gen art, shaders, interactive, 3D.
- **popular-web-designs** — 54 real design systems (Stripe, Linear, Vercel) as
  HTML/CSS.
- **songwriting-and-ai-music** — Songwriting craft and Suno AI music prompts.

## Devops

- **sdlc-review** — Review Kanban handoffs and route verified outcomes.

## Email

- **email-inbox-triage** — Triage an inbox: prioritize threads, draft replies
  safely.
- **himalaya** — Himalaya CLI: IMAP/SMTP email from terminal.

## Media

- **gif-search** — Search/download GIFs from Tenor via curl + jq.
- **songsee** — Audio spectrograms/features (mel, chroma, MFCC) via CLI.
- **youtube-content** — YouTube transcripts to summaries, threads, blogs.

## Note Taking

- **obsidian** — Read, search, create, and edit notes in the Obsidian vault.

## Productivity

- **airtable** — Airtable REST API via curl. Records CRUD, filters, upserts.
- **box** — Box manages cloud files, sharing, search, and metadata.
- **document-to-action-items** — Extract cited obligations, deadlines, tasks
  from documents.
- **docx** — Create, read, edit, template, and review Word .docx files.
- **google-workspace** — Gmail, Calendar, Drive, Docs, Sheets via gws CLI or
  Python.
- **maps** — Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.
- **meeting-action-items** — Turn meeting notes into cited decisions, owners,
  tickets.
- **notion** — Notion API + ntn CLI: pages, databases, markdown, Workers.
- **pdf** — PDF files: create, read, merge, fill, OCR, edit text.
- **powerpoint** — Create, read, edit .pptx decks with python-pptx.
- **product-price-monitor** — Watch product, flight, or listing prices; alert on
  target.
- **teams-meeting-pipeline** — Teams meeting summaries, job replay, Graph
  subscriptions.
- **weekly-review-planning** — Weekly reset: commitments, stalled work,
  next-week plan.
- **xlsx** — Create, read, edit Excel .xlsx workbooks and CSVs.

## Research

- **arxiv** — Search arXiv papers by keyword, author, category, or ID.
- **competitor-news-monitor** — Watch named companies for material news; cited
  digests.
- **grounded-citations** — Ground answers and documents in cited, verifiable
  sources.
- **llm-wiki** — Karpathy's LLM Wiki: build/query interlinked markdown KB.
- **prediction-market-edge-validation** — Use when validating a trading edge
  pre-capital.
- **prediction-market-trading** — Use when researching Kalshi/Polymarket US
  edges.

## Social Media

- **xurl** — X/Twitter via xurl CLI: raw post search, posting, DM, media.

## Software Development

- **codebase-inspection** — Inspect codebases w/ pygount: LOC, languages,
  ratios.
- **dogfood** — Exploratory QA of web apps: find bugs, evidence, reports.
- **github** — GitHub via gh CLI: PRs, issues, reviews, repos, auth.
- **hermes-agent-skill-authoring** — Author in-repo SKILL.md files: frontmatter
  and structure.
- **inspecting-hermes-desktop-dom** — Read the live Hermes desktop DOM/CSS over
  CDP.
- **node-inspect-debugger** — Debug Node.js via --inspect + Chrome DevTools
  Protocol CLI.
- **python-debugpy** — Debug Python: pdb REPL + debugpy remote (DAP).
- **requesting-code-review** — Pre-commit review: security scan, quality gates,
  auto-fix.
- **safe-workspace-teardown** — Park a project: push every repo, then reclaim
  disk safely.
- **simplify-code** — Parallel 4-agent cleanup of recent code changes.
- **spike** — Throwaway experiments to validate an idea before build.
- **systematic-debugging** — 4-phase root cause debugging: understand bugs
  before fixing.
- **test-driven-development** — TDD: enforce RED-GREEN-REFACTOR, tests before
  code.

## Trading

- **trading-bot-ops** — Set up, verify, and vet trading bots on a VM.

## Web

- **blocked-page-recovery** — Use when a fetch fails: 403/429, paywall, WAF, bot
  wall.

## Published Kbrain Skills

- [Cloud VM maintenance](skills/cloud-vm-maintenance/SKILL.md)
- [Evidence-first research](skills/evidence-first-research/SKILL.md)
- [Hermes provider diagnosis](skills/hermes-provider-diagnosis/SKILL.md)
- [Kbrain curation](skills/kbrain-curation/SKILL.md)
- [Multi-agent chat topologies](skills/multi-agent-chat-topologies/SKILL.md)
- [Safe agent handoff](skills/safe-agent-handoff/SKILL.md)
- [Secret config operations](skills/secret-config-operations/SKILL.md)
- [Trading strategy validation](skills/trading-strategy-validation/SKILL.md)
- [Verified delivery](skills/verified-delivery/SKILL.md)

## Redistribution Boundary

The live installation contains bundled and third-party skill material. Kbrain
does not vendor those bodies without a separate license and provenance review.
Use the public
[Hermes Agent repository](https://github.com/NousResearch/hermes-agent) for
upstream skill source and installation instructions.
