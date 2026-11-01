# core — the kbrain engine

The engine that runs kbrain's autonomous research agents. The rest of this repo is the knowledge
layer (methodology, lessons, negative results) that the agents read. Code is public; **runtime state
(`core/state/`: database, transcripts, workspaces) and provider keys are gitignored and must never be committed.**

    chief of staff --new_tasks--> queue (SQLite) --> runner --> role + model chain --> result.json
                                          ^                              |
                                      events log  <----------------------+   (the future GUI just tails this)

Design rules: workers never spawn workers (only `chief` has `can_spawn`; depth/queue capped);
shared state is files + SQLite, not conversation context; gates are deterministic code
(`kb/gates.py` encodes METHODOLOGY.md's preregistration requirements); the skeptic runs on a
different backend family than the backtester; agents get a scrubbed environment (no KEY/TOKEN/SECRET);
rate limits requeue with backoff instead of burning attempts; a crash re-queues running tasks.

## The pipeline (deterministic, in `kb/lifecycle.py`)
LLMs propose and do the work; code decides what happens next, so the system finishes things instead of looping.

    chief proposes idea (new slug) -> researcher writes prereg.md -> gate checks sections -> FROZEN + sha256
      -> backtester (blocked if prereg missing/modified) -> metrics graded by code (kb/stats.py)
         ci_low <= 0 or fails without top units -> REJECTED (appended to state/dead-ends.md)
         too few units / no metrics / blocked    -> PARKED with reason
         pass -> skeptic on another model family -> SURVIVES = VALIDATED (human decides on paper trading)

Anti-spiral: the chief may only spawn researcher/curator tasks; new slugs only; near-duplicate tasks
refused for 14 days; max 6 open hypotheses and no new ones while 3+ are waiting on data (finish before starting); 8 tasks per hypothesis; if 40 runs pass
with no hypothesis changing state, the chief pauses and HQ shows a STALL alert until you `kb ack`.

## Fleet (the VMs)
The harness checks the trading VMs over ssh every 15 min (`kb fleet` runs it now).
The map of boxes, runners (live/dry/tape, end time, the question each one answers) and bets (decision date,
kill rule) lives in `~/.config/kbrain/ops.toml` (machine config next to the keys it names). The result is
staged at the top of the chief's digest; a runner that dies before its `until`, or an unreachable box, raises
`alert.fleet` in HQ. Update ops.toml whenever you start or stop something on a box.
Roles with `with_fleet` get `./kbssh <box> '<cmd>'`: a separate agents' key whose forced command is
`ops/kbro_gate.py` (full shell incl. sudo, every command logged to `~/.kbro/audit.log`, tripwire on live arming
and key dumping; policy: everything except arming). Desks declare runners they start in
`desks/<desk>/runners.toml` and the fleet monitor picks them up. Install or refresh the key with
`core/ops/install_kbro.sh` (operator-run). Agents get no MCP servers.

## Roles
`chief` (chief of staff: wakes on a heartbeat when idle, reads a state digest, emits tasks) ·
`researcher` (hypotheses + preregistrations) · `backtester` (blocked without a complete prereg) ·
`skeptic` (different backend family than the backtester) · `curator` (compacts memory).

## Free / cheap models
The default chains start with OpenCode free models. Claude is absent from every chain, so a running
daemon cannot use its five-hour quota unless you add it to `config/routing.toml`. Codex is a fallback
for code tasks and the independent skeptic. Rate limits cool a model down across all tasks for
`rate_limit_backoff_s`; other free models can pick up the work. The global `max_runs_per_day` cap is
120. Use `bin/kb stats` to see successes, blocked tasks, invalid runs, and rate limits separately.

Backends: `claude`, `codex`, `agy` (Antigravity; headless permissions are unresolved), `opencode`
(run `opencode models` to check the current free catalog), `api:<provider>/<model>` (tool-less call to
an OpenAI-compatible endpoint, configured under `[providers]`). API models cannot write files, so
they only fit text-only roles without artifacts. Keys go in `~/.config/kbrain/env` (chmod 600, never
in the repo); the daemon strips them from agent subprocesses.

## HQ (the LARP view)
`bin/kb web` -> http://127.0.0.1:7777. Default view is the OFFICE: the classic pixel rooms under a gold KBRAIN header, with no panels or controls (click an agent for its card). Other layouts via ?theme=classic|lamplight|blueprint|pipeline|minimal (classic adds the side panel, command bar and STOP/ACK): one pixel room per role; agents walk to their desks when they get a
task, show the task and model in a speech bubble, nap on rate limits; envelopes fly to the mailroom (queue)
and out to desks. Side panel: hypothesis board, live feed, queue, model stats. Click an agent or event to
inspect a task (result, runs, log tail). The command bar sends instructions to the chief, a new idea to a
researcher, or work to the curator. STOP/RESUME and ACK buttons. Local only (127.0.0.1, host-checked,
POSTs need a custom header).

## Use
    core/bin/kb add researcher "Draft prereg for X" --hypothesis x --spec '{"idea":"..."}'
    core/bin/kb              # banner + status;  also: top | stats | tail -f | stop | resume | ack | web
    core/bin/kb serve                # the daemon (idle -> chief heartbeat every `heartbeat_s`)
    python3 -m unittest discover -s core/tests

## Run 24/7
    mkdir -p ~/.config/systemd/user && cp core/systemd/kb-*.service ~/.config/systemd/user/
    systemctl --user daemon-reload && systemctl --user enable --now kb-runner kb-web
Lid-close suspends by default: set `HandleLidSwitchExternalPower=ignore` in /etc/systemd/logind.conf.
Linger is already on.

## Not built yet
A data layer (agents can only use public data they can fetch themselves; most real ideas will park as
"blocked: data"), paper-trading handoff to the VM, notifications (Telegram) for validated/stall alerts,
login-expiry health checks, workspace cleanup, skeptic evals with planted bugs, parallel workers.
