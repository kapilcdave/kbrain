#!/usr/bin/env bash
# Operator-run: give kbrain agents READ-ONLY ssh to every box in ~/.config/kbrain/ops.toml.
# 1. creates ~/.ssh/kbro_ed25519 (agents' key) if missing
# 2. copies core/ops/kbro_ro.py to ~/.kbro/ on each box
# 3. appends the agents' key to the box's authorized_keys as a FORCED command (restrict + kbro_ro.py),
#    after backing the file up to authorized_keys.bak-kbro. Your own key line is not touched.
# Undo on a box: remove the line ending in "kbro-readonly" from ~/.ssh/authorized_keys.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -f ~/.ssh/kbro_ed25519 ] || ssh-keygen -q -t ed25519 -N '' -C kbro-readonly -f ~/.ssh/kbro_ed25519
PUB="$(cat ~/.ssh/kbro_ed25519.pub)"
python3 - <<'EOF' > /tmp/kbro_boxes.$$
import tomllib, os
for b in tomllib.load(open(os.path.expanduser("~/.config/kbrain/ops.toml"), "rb"))["box"]:
    print(b["name"], os.path.expanduser(b["key"]), f"{b['user']}@{b['host']}", b["user"])
EOF
while read -r name key dest user; do
  echo "== $name ($dest)"
  LINE="restrict,command=\"/usr/bin/python3 -I /home/$user/.kbro/kbro_ro.py\" $PUB"
  ssh -n -i "$key" -o BatchMode=yes -o LogLevel=ERROR "$dest" 'mkdir -p ~/.kbro && chmod 700 ~/.kbro && rm -f ~/.kbro/kbro_ro.py'
  ssh -i "$key" -o BatchMode=yes -o LogLevel=ERROR "$dest" 'cat > ~/.kbro/kbro_ro.py && chmod 500 ~/.kbro/kbro_ro.py' < "$HERE/kbro_ro.py"
  printf '%s\n' "$LINE" | ssh -i "$key" -o BatchMode=yes -o LogLevel=ERROR "$dest" \
    'L=$(cat); cp -p ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak-kbro; grep -q "kbro-readonly" ~/.ssh/authorized_keys || printf "%s\n" "$L" >> ~/.ssh/authorized_keys; echo "  installed"'
  echo -n "  test (should print uptime): "; "$HERE/../bin/kbssh" "$name" uptime
  echo -n "  test (should be refused):   "; "$HERE/../bin/kbssh" "$name" systemctl stop nothing 2>&1 || true
done < /tmp/kbro_boxes.$$
rm -f /tmp/kbro_boxes.$$
