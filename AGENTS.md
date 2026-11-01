# AGENTS.md: start here

kbrain is a trading research firm run by agents on this machine. Humans: see [README.md](README.md).

## How you are run
The daemon (`core/bin/kb serve`, systemd `kb-runner`) gives each task its own workspace under
`core/state/workspaces/task-N/`. Everything you need is staged into it:
`spec.json`, `digest.md` (chief), `priors.md` (private prior findings), `inputs/`, `data/` (datasets).
Read those first. Write `result.json` when done. Your role file in `core/roles/` is the contract.

## Where things are (repo)
| Need | Go to |
|---|---|
| Goal and success test | `core/GOAL.md` |
| Rules a result must pass | `METHODOLOGY.md`, `lessons/preregistration.md` |
| Already rejected or closed | `priors.md` (staged), `core/knowledge/dead-ends.md`, `lessons/negative-results.md` |
| Firm knowledge index (curator) | `core/knowledge/index.md` |
| Durable public findings | `research/`, `lessons/` |
| Older research programmes | `PROJECTS.md` then `projects/` |
| Engine, roles, routing | `core/README.md`, `core/roles/`, `core/config/routing.toml` |

## Hard rules
1. Live trading is never started by an agent.
2. No credentials, tokens, runtime state or transcripts in this repo (it is public).
3. `priors.md` is private. Never copy its numbers, our fills, P&L or positioning into a page.
4. Never re-propose a closed branch unless the instrument or mechanism is genuinely new.
5. One subject, one canonical page. Update it; do not add a near-duplicate.
6. Distinguish measured result, inference, conclusion. Keep retractions next to what they replace.
