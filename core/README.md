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

## Roles
`chief` (chief of staff: wakes on a heartbeat when idle, reads a state digest, emits tasks) ·
`researcher` (hypotheses + preregistrations) · `backtester` (blocked without a complete prereg) ·
`skeptic` (different backend family than the backtester) · `curator` (compacts memory).
Hermes is not required; the chief role replaces it.

## Free / cheap models
Backends: `claude`, `codex`, `gemini`, `opencode` (CLIs on your logins; `opencode models` lists the free ones), `api:<provider>/<model>` (tool-less call to any
OpenAI-compatible endpoint; define it under `[providers]` in `config/routing.toml`). Keys go in
`~/.config/kbrain/env` (chmod 600, never in the repo); the daemon loads them and strips them from every
agent's environment. `max_runs_per_day` is a global circuit breaker. Compare models with `bin/kb stats`.

## Use
    core/bin/kb add researcher "Draft prereg for X" --hypothesis x --spec '{"idea":"..."}'
    core/bin/kb status | stats | tail -f | stop | resume
    core/bin/kb serve                # the daemon (idle -> chief heartbeat every `heartbeat_s`)
    python3 -m unittest discover -s core/tests

## Run 24/7
    mkdir -p ~/.config/systemd/user && cp core/systemd/kb-runner.service ~/.config/systemd/user/
    systemctl --user daemon-reload && systemctl --user enable --now kb-runner
Lid-close suspends by default: set `HandleLidSwitchExternalPower=ignore` in /etc/systemd/logind.conf.
Linger is already on.

## Not built yet
Promotion gates beyond prereg, paper-trading handoff to the VM, reviewed sync of findings into the public
pages, the GUI.
