# AGENTS.md: start here

kbrain is the operator's trading firm, run by agents ("pixel bros") on this machine as one continuous run.
It is our working brain: findings, numbers, fills and P&L belong here. Humans: see [README.md](README.md).

## How you are run
The daemon (`core/bin/kb serve`, systemd `kb-runner`) runs standing desks continuously (chief, kalshi,
hyperliquid, predx, data, review) plus pipeline roles that lifecycle code spawns. Each task gets a workspace
under `core/state/workspaces/task-N/` with: `spec.json`, `repo/` (your own git worktree), `board.md` (every
desk's notebook and requests), `fleet.md` (VMs, runners, bets), `corpus/` (~650 trading findings),
`projects/` (trading code and handoffs), `priors.md`, `data/`, and `./kbssh` (full shell on the VMs, logged).
Write `result.json` when done. `core/roles/_common.md` is the shared brief; your role file is your contract.

## Where things are
| Need | Go to |
|---|---|
| Shared brief: focus, corpus, machines, git | `core/roles/_common.md` |
| What each desk is doing | `desks/<desk>/NOTEBOOK.md`, requests in `desks/<desk>/OUTBOX.md` |
| VMs, runners, bets and decision dates | `fleet.md` (staged); source `~/.config/kbrain/ops.toml`; `core/bin/kb fleet` |
| Trading corpus | `corpus/MEMORY.md`, `corpus/topics-*.md` (~/repos/claude-code-memory/proj-trading) |
| Rules a result must pass | `METHODOLOGY.md`, `lessons/preregistration.md` |
| Closed or rejected | `priors.md`, `corpus/topics-closed-branches.md`, `core/knowledge/dead-ends.md` |
| Engine, roles, routing | `core/README.md`, `core/roles/`, `core/config/routing.toml` |

## Hard rules
1. Everything except arming: agents run the VMs (deploy, collectors, tapes, dry runs) but never place real
   orders or touch a live runner; they ask `[to:operator]`. Keys live only on the VMs and are never printed.
2. Never commit credentials, keys or tokens, or raw tape data. The harness scans every merge.
3. Commit in your worktree; never push. The harness tests, rebases and merges to main.
4. Engine code (`core/kb`, `core/config`, `core/roles`, `core/bin`, `core/ops`, `core/tests`) changes only
   through the operator. Propose engine changes on the board.
5. Never re-propose a closed branch unless the instrument or mechanism is genuinely new.
6. One subject, one canonical page. Measured result vs inference vs conclusion. Retractions stay visible.
