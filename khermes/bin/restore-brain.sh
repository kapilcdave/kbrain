#!/usr/bin/env bash
# Restore the agent's brain and credentials from a GCE disk snapshot.
#
#   bin/restore-brain.sh <snapshot-name>
#
# The brain is deliberately not in this repo: state.db holds private
# transcripts and credential-shaped strings, and .env/auth.json hold the live
# Telegram bot token and provider keys. They live in a snapshot inside the
# project -- encrypted at rest, never on GitHub. This is the path back.
#
# What it does: creates a disk from the snapshot, attaches it read-only as a
# second disk, copies the brain over the fresh install, detaches and deletes
# the temporary disk. The gateway is stopped for the copy, because sqlite
# files copied out from under a live writer come back corrupt.
set -euo pipefail

SNAPSHOT="${1:?usage: restore-brain.sh <snapshot-name>}"
NAME="${NAME:-hermes-iowa}"
ZONE="${ZONE:-us-central1-a}"
TMPDISK="restore-$SNAPSHOT-$$"

gcloud compute snapshots describe "$SNAPSHOT" >/dev/null

echo "==> creating $TMPDISK from $SNAPSHOT"
gcloud compute disks create "$TMPDISK" \
  --source-snapshot="$SNAPSHOT" --zone="$ZONE" --type=pd-standard >/dev/null

cleanup() {
  echo "==> cleaning up $TMPDISK"
  gcloud compute instances detach-disk "$NAME" --disk "$TMPDISK" --zone "$ZONE" 2>/dev/null || true
  gcloud compute disks delete "$TMPDISK" --zone "$ZONE" --quiet 2>/dev/null || true
}
trap cleanup EXIT

echo "==> attaching read-only"
gcloud compute instances attach-disk "$NAME" \
  --disk "$TMPDISK" --device-name restoresrc --mode ro --zone "$ZONE" >/dev/null

gcloud compute ssh "$NAME" --zone "$ZONE" --command '
set -euo pipefail
U="${HERMES_USER:-$(id -un)}"
HOME_DIR="$(getent passwd "$U" | cut -d: -f6)"
H="$HOME_DIR/.hermes"
export XDG_RUNTIME_DIR="/run/user/$(id -u "$U")"

DEV=/dev/disk/by-id/google-restoresrc
for i in $(seq 20); do [ -e "$DEV" ] && break; sleep 1; done
[ -e "$DEV" ] || { echo "FAIL: $DEV never appeared" >&2; exit 1; }

# The snapshot is of a whole boot disk, so mount its root partition.
PART="${DEV}-part1"; [ -e "$PART" ] || PART="$DEV"
sudo mkdir -p /mnt/restore
# nouuid/norecovery: the snapshot root has the same FS UUID as the live root.
sudo mount -o ro,norecovery "$PART" /mnt/restore 2>/dev/null \
  || sudo mount -o ro,norecovery,nouuid "$PART" /mnt/restore

SRC=$(sudo find /mnt/restore/home -maxdepth 2 -type d -name .hermes | head -1)
[ -n "$SRC" ] || { echo "FAIL: no .hermes on the snapshot" >&2; exit 1; }
echo "    source: $SRC"

echo "==> stopping gateway (sqlite must not be copied live)"
systemctl --user stop hermes-gateway.service || true

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$H/../.hermes-pre-restore-$STAMP"
BK="$H/../.hermes-pre-restore-$STAMP"

# Credentials and the brain. WAL/SHM are intentionally NOT copied: a
# checkpointed .db plus a stale -wal from a different moment is worse than
# the .db alone, and sqlite will rebuild them.
for f in .env auth.json config.yaml install_id gateway_state.json \
         channel_directory.json state.db kanban.db shared-state.db \
         verification_evidence.db; do
  if sudo test -e "$SRC/$f"; then
    [ -e "$H/$f" ] && mv "$H/$f" "$BK/$f" 2>/dev/null || true
    sudo cp -p "$SRC/$f" "$H/$f"
    sudo chown "$U:$U" "$H/$f"
  fi
done
sudo rm -f "$H"/state.db-wal "$H"/state.db-shm "$H"/kanban.db-wal "$H"/kanban.db-shm
sudo cp -p "$SRC"/telegram_update_receipts_*.json "$H/" 2>/dev/null || true
sudo chown "$U:$U" "$H"/telegram_update_receipts_*.json 2>/dev/null || true

for d in memories sessions pastes shared kanban platforms plugins; do
  if sudo test -d "$SRC/$d"; then
    [ -d "$H/$d" ] && mv "$H/$d" "$BK/$d" 2>/dev/null || true
    sudo cp -a "$SRC/$d" "$H/$d"
    sudo chown -R "$U:$U" "$H/$d"
  fi
done

chmod 600 "$H/.env" "$H/auth.json" 2>/dev/null || true

echo "==> integrity check"
for db in state.db kanban.db; do
  [ -f "$H/$db" ] || continue
  r=$(sqlite3 "$H/$db" "PRAGMA integrity_check;" 2>&1 | head -1)
  echo "    $db: $r"
  [ "$r" = ok ] || { echo "FAIL: $db did not survive the copy; previous files are in $BK" >&2; exit 1; }
done

sudo umount /mnt/restore
systemctl --user start hermes-gateway.service
echo "==> restored; pre-restore files kept in $BK"
'

echo "==> now run bin/preflight.sh"
