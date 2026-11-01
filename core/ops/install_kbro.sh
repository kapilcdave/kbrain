#!/usr/bin/env bash
# Operator-run: give kbrain agents a full shell on every box in ~/.config/kbrain/ops.toml, through
# core/ops/kbro_gate.py (audit log + tripwire on live arming and key dumping; policy: everything but arming).
# 1. creates ~/.ssh/kbro_ed25519 (agents' key) if missing
# 2. copies kbro_gate.py to ~/.kbro/ on each box
# 3. puts the agents' key in authorized_keys as a FORCED command (restrict + kbro_gate.py), replacing any
#    older kbro line, after backing the file up to authorized_keys.bak-kbro. Your own key line is untouched.
# Audit on a box: ~/.kbro/audit.log. Undo: remove the line ending in "kbro-agent" (or "kbro-readonly").
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -f ~/.ssh/kbro_ed25519 ] || ssh-keygen -q -t ed25519 -N '' -C kbro-agent -f ~/.ssh/kbro_ed25519
PUB="$(cat ~/.ssh/kbro_ed25519.pub)"
python3 - <<'EOF' > /tmp/kbro_boxes.$$
import tomllib, os
for b in tomllib.load(open(os.path.expanduser("~/.config/kbrain/ops.toml"), "rb"))["box"]:
    print(b["name"], os.path.expanduser(b["key"]), f"{b['user']}@{b['host']}", b["user"])
EOF
while read -r name key dest user; do
  echo "== $name ($dest)"
  LINE="restrict,command=\"/usr/bin/python3 -I /home/$user/.kbro/kbro_gate.py\" $PUB"
  ssh -n -i "$key" -o BatchMode=yes -o LogLevel=ERROR "$dest" 'mkdir -p ~/.kbro && chmod 700 ~/.kbro && rm -f ~/.kbro/kbro_ro.py ~/.kbro/kbro_gate.py'
  ssh -i "$key" -o BatchMode=yes -o LogLevel=ERROR "$dest" 'cat > ~/.kbro/kbro_gate.py && chmod 500 ~/.kbro/kbro_gate.py' < "$HERE/kbro_gate.py"
  printf '%s\n' "$LINE" | ssh -i "$key" -o BatchMode=yes -o LogLevel=ERROR "$dest" \
    'L=$(cat); cp -p ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak-kbro; grep -v -e "kbro-readonly" -e "kbro-agent" ~/.ssh/authorized_keys.bak-kbro > ~/.ssh/authorized_keys.new; printf "%s\n" "$L" >> ~/.ssh/authorized_keys.new; chmod 600 ~/.ssh/authorized_keys.new; if [ "$(grep -vc kbro-agent ~/.ssh/authorized_keys.new)" -ge 1 ] && grep -q kbro-agent ~/.ssh/authorized_keys.new; then mv ~/.ssh/authorized_keys.new ~/.ssh/authorized_keys; echo "  installed"; else rm -f ~/.ssh/authorized_keys.new; echo "  ABORTED: new file would drop your own key; nothing changed"; fi'
  echo -n "  test (should print the hostname): "; "$HERE/../bin/kbssh" "$name" 'hostname | cut -d. -f1' < /dev/null
  echo -n "  test (should be refused):         "; "$HERE/../bin/kbssh" "$name" 'echo --armed' < /dev/null 2>&1 || true
done < /tmp/kbro_boxes.$$
rm -f /tmp/kbro_boxes.$$
