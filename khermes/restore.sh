#!/usr/bin/env bash
# Apply only portable, non-secret settings after a fresh Hermes setup.
set -euo pipefail
command -v hermes >/dev/null || { printf 'Install Hermes first: https://hermes-agent.nousresearch.com/docs/\n' >&2; exit 1; }

# Each value below was deliberately selected from the old default profile.
# Do not restore the old default model: it may not match the current session.
hermes config set memory.memory_enabled false
hermes config set memory.user_profile_enabled false
hermes config set memory.memory_char_limit 2200
hermes config set memory.user_char_limit 1375
hermes config set delegation.max_iterations 250
hermes config set streaming.enabled false
hermes config set telemetry.shared_metrics.enabled false
hermes config set telemetry.shared_metrics.send false
hermes config set smart_model_routing.enabled false
printf 'Portable settings applied. Check them with: hermes config show\n'
printf 'Configure provider, secrets and gateway separately; see khermes/HANDOFF.md.\n'
