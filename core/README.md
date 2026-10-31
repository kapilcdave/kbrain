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
refused for 14 days; max 5 open hypotheses (finish before starting); 8 tasks per hypothesis; if 40 runs pass
with no hypothesis changing state, the chief pauses and HQ shows a STALL alert until you `kb ack`.

## Roles
`chief` (chief of staff: wakes on a heartbeat when idle, reads a state digest, emits tasks) ·
`researcher` (hypotheses + preregistrations) · `backtester` (blocked without a complete prereg) ·
`skeptic` (different backend family than the backtester) · `curator` (compacts memory).
Hermes is not required; the chief role replaces it.

## Free / cheap models
Backends: `claude`, `codex`, `agy` (Antigravity; headless runs currently auto-deny shell commands, so it sits last in the chains), `opencode` (CLIs on your logins; `opencode models` lists the free ones), `api:<provider>/<model>` (tool-less call to any
OpenAI-compatible endpoint; define it under `[providers]` in `config/routing.toml`). Keys go in
`~/.config/kbrain/env` (chmod 600, never in the repo); the daemon loads them and strips them from every
agent's environment. `max_runs_per_day` is a global circuit breaker. Compare models with `bin/kb stats`.

## HQ (the LARP view)
`bin/kb web` -> http://127.0.0.1:7777. Default view is MINIMAL: a dark screen with the agents, their names, and white text saying what each is doing (click an agent for a card beside it; hover the top edge for the header and other layouts; press / to send a message). Other layouts: one pixel room per role; agents walk to their desks when they get a
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
