# AGENTS.md: start here

kbrain is the operator's bio x AI research brain, run by agents ("pixel bros") on this machine.
Humans: see [README.md](README.md). The shared brief is `core/roles/_common.md`; your role file is your contract.

## How you are run
The daemon (`core/bin/kb serve`, systemd `kb-runner`) routes each idea:
idea (operator via `kb idea "..."`/HQ, or the chief when slots are free) -> chief (triage, field) -> field bro
(genomics | proteins | cells | clinic: prereg with its dossier) -> data engineer (if data is missing) ->
experimenter -> skeptic -> field bro (verdict into `fields/<field>/DOSSIER.md`, write-up if validated) ->
chief (finding in `knowledge/findings/`, entry in `knowledge/OPPORTUNITIES.md`).
The scout runs continuously: field intelligence into `knowledge/`, experiments into `knowledge/CANDIDATES.md`.
Each task gets a workspace under `core/state/workspaces/task-N/` with `spec.json`, `dossier.md`, `repo/`
(git worktree, for roles that commit), `data/` and `inputs/`. Write `result.json` when done.

## Where things are
| Need | Go to |
|---|---|
| Shared brief: focus, compute, money, rigor, git | `core/roles/_common.md` |
| A field's state of the art, datasets, baselines, verdicts | `fields/<field>/DOSSIER.md` |
| Field map | `knowledge/INDEX.md` |
| Rules a result must pass | `METHODOLOGY.md`, `lessons/preregistration.md`, `lessons/fake-edges-from-data-bugs.md` |
| Engine, roles, routing | `core/README.md`, `core/roles/`, `core/config/routing.toml` |
| Old trading work (not the focus) | `archive/trading/` |

## Hard rules
1. Anything that spends money (cloud GPUs, paid data or APIs) needs the operator's approval. Never create cloud resources.
2. Public, open-access data only. Never controlled-access human data.
3. Never commit credentials or raw data. Commit in your worktree; never push. The harness tests and merges.
4. Engine code (`core/kb`, `core/config`, `core/roles`, `core/bin`, `core/ops`, `core/tests`) changes only through the operator.
5. Beat a stated baseline on a held-out split fixed in advance; grade per independent unit with kbstats.
6. One subject, one canonical page. Measured result vs inference vs conclusion. Retractions stay visible.
