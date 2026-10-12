#!/usr/bin/env bash
# Install the Hermes gateway on a fresh always-free VM.
#
# Run it from your laptop: it copies this directory to the VM and re-executes
# itself there. Idempotent -- safe to re-run after fixing something.
#
#   bin/bootstrap.sh                      # default VM/zone, see below
#   NAME=hermes-iowa ZONE=us-central1-a bin/bootstrap.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="${NAME:-hermes-iowa}"
ZONE="${ZONE:-us-central1-a}"
SWAP_MB="${SWAP_MB:-1024}"

# ---------------------------------------------------------------- remote half
if [ "${HERMES_ON_VM:-0}" != "1" ]; then
  echo "==> staging to $NAME ($ZONE)"
  DIR="$(basename "$HERE")"
  tar -C "$(dirname "$HERE")" -czf /tmp/hermes-deploy.tgz "$DIR"
  gcloud compute scp /tmp/hermes-deploy.tgz "$NAME":/tmp/ --zone "$ZONE"
  gcloud compute ssh "$NAME" --zone "$ZONE" --command \
    "set -e; rm -rf /tmp/hermes-deploy && mkdir -p /tmp/hermes-deploy \
     && tar -C /tmp/hermes-deploy -xzf /tmp/hermes-deploy.tgz \
     && HERMES_ON_VM=1 SWAP_MB=$SWAP_MB bash /tmp/hermes-deploy/$DIR/bin/bootstrap.sh"
  exit $?
fi

# ----------------------------------------------------------------- local half
HERMES_USER="${HERMES_USER:-$(id -un)}"
HOME_DIR="$(getent passwd "$HERMES_USER" | cut -d: -f6)"
HERMES_HOME="${HERMES_HOME:-$HOME_DIR/.hermes}"
UID_N="$(id -u "$HERMES_USER")"
# shellcheck disable=SC1091
source "$HERE/config/UPSTREAM"

echo "==> host packages"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  git curl ca-certificates sqlite3 zstd jq >/dev/null

# An e2-micro has 964 MB of RAM and Hermes carries a Chromium. Without swap,
# one browser-tool invocation can OOM-kill the gateway mid-conversation.
if [ "$SWAP_MB" -gt 0 ] && ! sudo swapon --show | grep -q /swapfile; then
  echo "==> ${SWAP_MB}MB swapfile"
  sudo fallocate -l "${SWAP_MB}M" /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count="$SWAP_MB"
  sudo chmod 600 /swapfile && sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
  # 1 GB of RAM: lean on swap only under real pressure.
  echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-hermes-swap.conf >/dev/null
  sudo sysctl -q -p /etc/sysctl.d/99-hermes-swap.conf
fi

echo "==> hermes installer"
if [ ! -x "$HERMES_HOME/hermes-agent/.hermes/bin/hermes" ]; then
  curl -fsSL "$INSTALLER_URL" | bash
fi
[ -x "$HERMES_HOME/hermes-agent/.hermes/bin/hermes" ] \
  || { echo "FAIL: installer did not produce the hermes launcher" >&2; exit 1; }

echo "==> pin upstream to ${UPSTREAM_SHA:0:7}"
cd "$HERMES_HOME/hermes-agent"
if [ "$(git rev-parse HEAD)" != "$UPSTREAM_SHA" ]; then
  if ! git cat-file -e "$UPSTREAM_SHA^{commit}" 2>/dev/null; then
    git fetch --filter=blob:none origin "$UPSTREAM_SHA" \
      || git fetch --filter=blob:none --unshallow origin
  fi
  git -c advice.detachedHead=false checkout --force "$UPSTREAM_SHA"
fi

echo "==> config"
mkdir -p "$HERMES_HOME"
if [ ! -f "$HERMES_HOME/.env" ]; then
  install -m 600 /dev/null "$HERMES_HOME/.env"
  cat "$HERE/config/.env.example" >> "$HERMES_HOME/.env"
  NEEDS_SECRETS=1
fi
chmod 600 "$HERMES_HOME/.env"
[ -f "$HERMES_HOME/auth.json" ] && chmod 600 "$HERMES_HOME/auth.json"

echo "==> systemd user unit"
install -d -m 700 "$HOME_DIR/.config/systemd/user"
sed -e "s|__HERMES_HOME__|$HERMES_HOME|g" \
    -e "s|__HOME__|$HOME_DIR|g" \
    "$HERE/systemd/hermes-gateway.service" \
    > "$HOME_DIR/.config/systemd/user/hermes-gateway.service"

# Without lingering the user manager exits at logout and the agent dies at the
# next reboot with nothing in the system journal to explain it.
sudo loginctl enable-linger "$HERMES_USER"
export XDG_RUNTIME_DIR="/run/user/$UID_N"
systemctl --user daemon-reload
systemctl --user enable hermes-gateway.service

if [ "${NEEDS_SECRETS:-0}" = 1 ]; then
  cat <<EOF

================================================================
STOPPING: $HERMES_HOME/.env is a template. Fill it in, then start.

  \$EDITOR $HERMES_HOME/.env

Required: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS,
          TELEGRAM_HOME_CHANNEL, ANTHROPIC_API_KEY

TELEGRAM_ALLOWED_USERS is the only thing between this agent's shell
tools and anyone who finds the bot. Do not leave it blank.

Then:  XDG_RUNTIME_DIR=/run/user/$UID_N systemctl --user start hermes-gateway
Then:  bin/preflight.sh
================================================================
EOF
  exit 0
fi

systemctl --user restart hermes-gateway.service
echo "==> started; now run bin/preflight.sh"
