#!/usr/bin/env bash
# Assert the gateway is actually live -- not merely "active (running)".
#
# A unit can sit in active(running) while the agent is failing every poll:
# bad token, no allowed users, a dependency that throws on import. The unit
# state tells you systemd started a process, not that Telegram round-trips.
# So this checks the facts that would have caught that, and exits non-zero.
set -uo pipefail

NAME="${NAME:-hermes-iowa}"
ZONE="${ZONE:-us-central1-a}"

if [ "${HERMES_ON_VM:-0}" != "1" ]; then
  exec gcloud compute ssh "$NAME" --zone "$ZONE" --command \
    "HERMES_ON_VM=1 bash -s" < "${BASH_SOURCE[0]}"
fi

HERMES_USER="${HERMES_USER:-$(id -un)}"
HOME_DIR="$(getent passwd "$HERMES_USER" | cut -d: -f6)"
HERMES_HOME="${HERMES_HOME:-$HOME_DIR/.hermes}"
export XDG_RUNTIME_DIR="/run/user/$(id -u "$HERMES_USER")"

fail=0
chk() { # chk <label> <0|1> <detail>
  if [ "$2" = 0 ]; then printf '  ok    %s\n' "$1"
  else printf '  FAIL  %s -- %s\n' "$1" "$3"; fail=1; fi
}

echo "preflight: hermes-gateway on $(hostname)"

systemctl --user is-active --quiet hermes-gateway.service
chk "unit active" $? "systemctl --user status hermes-gateway"

systemctl --user is-enabled --quiet hermes-gateway.service
chk "unit enabled at boot" $? "systemctl --user enable hermes-gateway"

[ -f "/var/lib/systemd/linger/$HERMES_USER" ]
chk "lingering enabled" $? "agent would die on reboot; loginctl enable-linger $HERMES_USER"

# 0600 or tighter, nothing group/world readable
perm=$(stat -c '%a' "$HERMES_HOME/.env" 2>/dev/null || echo missing)
[ "$perm" = 600 ]
chk ".env mode 0600" $? "mode is $perm"

# A blank allowlist means anyone who finds the bot gets shell tools.
allow=$(grep -c '^TELEGRAM_ALLOWED_USERS=[0-9]' "$HERMES_HOME/.env" 2>/dev/null || echo 0)
[ "$allow" -ge 1 ]
chk "TELEGRAM_ALLOWED_USERS set" $? "blank or placeholder allowlist -- bot is open to strangers"

# The real test: has the gateway processed a Telegram update? The receipts file
# is written per bot id as updates are acknowledged.
shopt -s nullglob
receipts=("$HERMES_HOME"/telegram_update_receipts_*.json)
[ ${#receipts[@]} -ge 1 ]
chk "telegram receipts present" $? "gateway has never acknowledged an update; token or network wrong"

# ... and did it do so recently? Stale receipts mean it polled once and stopped.
if [ ${#receipts[@]} -ge 1 ]; then
  age=$(( $(date +%s) - $(stat -c %Y "${receipts[0]}") ))
  [ "$age" -lt 86400 ]
  chk "receipts fresh (<24h)" $? "last update was ${age}s ago"
fi

hb="$HERMES_HOME/state/gateway.heartbeat"
if [ -f "$hb" ]; then
  hage=$(( $(date +%s) - $(stat -c %Y "$hb") ))
  [ "$hage" -lt 600 ]
  chk "heartbeat fresh (<10m)" $? "heartbeat ${hage}s old; loop is wedged"
else
  chk "heartbeat present" 1 "$hb missing"
fi

# Errors systemd will not surface, because the process stays up through them.
errs=$(journalctl --user -u hermes-gateway --since "-10 min" -p err --no-pager 2>/dev/null | grep -cvE 'logs begin|No entries' || true)
[ "${errs:-0}" -eq 0 ]
chk "no errors in last 10m" $? "$errs error lines; journalctl --user -u hermes-gateway -p err"

avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
[ "$avail" -gt 120 ]
chk "memory headroom >120MB" $? "only ${avail}MB available; an OOM kill is likely"

dfpct=$(df --output=pcent / | tail -1 | tr -dc 0-9)
[ "$dfpct" -lt 90 ]
chk "disk under 90%" $? "root is ${dfpct}% full; 30GB is the free-tier ceiling"

echo
if [ "$fail" = 0 ]; then echo "PREFLIGHT PASS"; else echo "PREFLIGHT FAIL -- do not trust the agent"; fi
exit "$fail"
