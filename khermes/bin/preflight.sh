#!/usr/bin/env bash
# Assert the gateway is actually live -- not merely "active (running)".
#
# A unit can sit in active(running) while the agent is failing every poll:
# bad token, no allowed users, a dependency that throws on import. The unit
# state tells you systemd started a process, not that Telegram round-trips.
# So this checks the facts that would have caught that, and exits non-zero.
#
#   bin/preflight.sh
#   NAME=<vm> ZONE=<zone> HERMES_USER=<user> bin/preflight.sh
#
# HERMES_USER matters whenever the agent runs as a different account than the
# one you SSH in as. Checking the wrong account reports a confident, total
# failure for a perfectly healthy agent -- so it is passed explicitly over the
# SSH hop rather than defaulted on the far side.
set -uo pipefail

NAME="${NAME:-hermes-iowa}"
ZONE="${ZONE:-us-central1-a}"

if [ "${HERMES_ON_VM:-0}" != "1" ]; then
  exec gcloud compute ssh "$NAME" --zone "$ZONE" --command \
    "HERMES_ON_VM=1 HERMES_USER='${HERMES_USER:-}' bash -s" < "${BASH_SOURCE[0]}"
fi

U="${HERMES_USER:-}"; [ -n "$U" ] || U="$(id -un)"
id "$U" >/dev/null 2>&1 || { echo "no such user: $U" >&2; exit 2; }
HOME_DIR="$(getent passwd "$U" | cut -d: -f6)"
H="${HERMES_HOME:-$HOME_DIR/.hermes}"
RT="/run/user/$(id -u "$U")"

# The agent's home is 0700 and its units belong to its own user manager, so
# every check has to cross into that account. Run as it when we are not it.
if [ "$U" = "$(id -un)" ]; then
  asu() { XDG_RUNTIME_DIR="$RT" "$@"; }
  aroot() { sudo "$@"; }
else
  asu() { sudo -u "$U" XDG_RUNTIME_DIR="$RT" "$@"; }
  aroot() { sudo "$@"; }
fi

fail=0
chk() { # chk <label> <0|1> <detail> -- a real failure
  if [ "$2" = 0 ]; then printf '  ok    %s\n' "$1"
  else printf '  FAIL  %s -- %s\n' "$1" "$3"; fail=1; fi
}
warn() { # warn <label> <0|1> <detail> -- worth seeing, not a verdict
  if [ "$2" = 0 ]; then printf '  ok    %s\n' "$1"
  else printf '  warn  %s -- %s\n' "$1" "$3"; fi
}

echo "preflight: hermes-gateway as $U on $(hostname -s)"

asu systemctl --user is-active --quiet hermes-gateway.service
chk "unit active" $? "systemctl --user status hermes-gateway"

asu systemctl --user is-enabled --quiet hermes-gateway.service
chk "unit enabled at boot" $? "systemctl --user enable hermes-gateway"

aroot test -f "/var/lib/systemd/linger/$U"
chk "lingering enabled" $? "agent dies on reboot; loginctl enable-linger $U"

# 0600 or tighter. Never reads a value out of the file.
perm=$(aroot stat -c '%a' "$H/.env" 2>/dev/null || echo missing)
[ "$perm" = 600 ]
chk ".env mode 0600" $? "mode is $perm"

# Count only -- a blank allowlist means anyone who finds the bot gets shell.
allow=$(aroot grep -c '^TELEGRAM_ALLOWED_USERS=[0-9]' "$H/.env" 2>/dev/null || echo 0)
[ "${allow:-0}" -ge 1 ]
chk "TELEGRAM_ALLOWED_USERS set" $? "blank or placeholder allowlist -- bot is open to strangers"

# Has the gateway ever acknowledged a Telegram update? Receipts are written
# per bot id as updates are processed, so their existence proves the token and
# the network path both work. This one is fatal.
newest=$(aroot bash -c "ls -t '$H'/telegram_update_receipts_*.json 2>/dev/null | head -1")
[ -n "$newest" ]
chk "telegram path proven" $? "gateway has never acknowledged an update; token or network wrong"

# Their *age*, though, measures how recently a human messaged the bot -- not
# agent health. An idle week and a dead bot look identical here, which is why
# the heartbeat below is the liveness signal and this only warns. Treating it
# as fatal reports a broken agent every time you simply stop texting it.
if [ -n "$newest" ]; then
  age=$(( $(date +%s) - $(aroot stat -c %Y "$newest") ))
  [ "$age" -lt 86400 ]
  warn "update seen in last 24h" $? "last inbound message ${age}s ago ($((age/86400))d) -- idle, not necessarily broken"
fi

hb="$H/state/gateway.heartbeat"
if aroot test -f "$hb"; then
  hage=$(( $(date +%s) - $(aroot stat -c %Y "$hb") ))
  [ "$hage" -lt 600 ]
  chk "heartbeat fresh (<10m)" $? "heartbeat ${hage}s old; the loop is wedged"
else
  chk "heartbeat present" 1 "$hb missing"
fi

# Errors systemd never surfaces, because the process stays up through them.
errs=$(asu journalctl --user -u hermes-gateway --since "-10 min" -p err --no-pager -q 2>/dev/null | grep -c . || true)
[ "${errs:-0}" -eq 0 ]
chk "no errors in last 10m" $? "${errs:-?} error lines; journalctl --user -u hermes-gateway -p err"

avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
[ "$avail" -gt 120 ]
chk "memory headroom >120MB" $? "only ${avail}MB available; an OOM kill is likely"

dfpct=$(df --output=pcent / | tail -1 | tr -dc 0-9)
[ "$dfpct" -lt 90 ]
chk "disk under 90%" $? "root is ${dfpct}% full; 30GB is the free-tier ceiling"

echo
if [ "$fail" = 0 ]; then echo "PREFLIGHT PASS"; else echo "PREFLIGHT FAIL -- do not trust the agent"; fi
exit "$fail"
