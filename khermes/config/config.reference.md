# config.yaml reference

The live `$HERMES_HOME/config.yaml` is not committed. It is not secret —
every value in it is a tuning knob — but it is machine state that the agent
rewrites itself, so a checked-in copy would be wrong within a week. The
installer writes a default; the snapshot restores the tuned one.

This is the shape of the tuned file on the Iowa VM as of 2026-10-12, so a
rebuilt agent can be compared against it.

## Keys present

```text
model.default              model.provider            model.base_url
database.journal_mode
runtime.nofile_soft_limit
agent.max_turns            agent.service_tier        agent.fast_auto_seconds
agent.disabled_toolsets[]  agent.verbose             agent.reasoning_effort
terminal.backend           terminal.cwd              terminal.timeout
terminal.home_mode         terminal.lifetime_seconds
terminal.container_cpu     terminal.container_memory terminal.container_disk
terminal.container_persistent
terminal.docker_mount_cwd_to_workspace
web.backend
browser.inactivity_timeout browser.extension_control.enabled
tool_loop_guardrails.warnings_enabled
tool_loop_guardrails.hard_stop_enabled
tool_loop_guardrails.non_interactive_hard_stop_enabled
tool_loop_guardrails.warn_after.{exact_failure,same_tool_failure,idempotent_no_progress}
tool_loop_guardrails.hard_stop_after.{exact_failure,same_tool_failure,idempotent_no_progress}
compression.*              (threshold, target_ratio, protect_last_n, protect_first_n,
                            proactive_prune_*, idle_compact_after_seconds, ...)
prompt_caching.cache_ttl
display.*                  (compact, show_reasoning, streaming, skin, bell_*, ...)
```

## The ones that matter on a 1 GB VM

- `terminal.container_memory` / `terminal.container_cpu` — the agent's
  sandboxed terminal competes with the gateway for 964 MB. Raising these is
  the fastest way to OOM the box.
- `agent.disabled_toolsets` — the cheapest lever for memory. The browser
  toolset pulls in Chromium.
- `compression.*` and `prompt_caching.cache_ttl` — these drive token spend,
  not memory. Unrelated to the free tier, but the actual monthly bill.
- `database.journal_mode` — WAL. Relevant to
  [`restore-brain.sh`](../bin/restore-brain.sh): a `.db` copied without its
  `-wal`, or with a mismatched one, is why that script checkpoints and drops
  the sidecars rather than copying them.
