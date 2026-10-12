#!/usr/bin/env bash
# Create a GCP always-free e2-micro shaped to stay inside the free tier.
#
# Every default here is a free-tier constraint, not a preference:
#   e2-micro        the only always-free machine type
#   us-central1     Iowa; only us-west1 / us-central1 / us-east1 qualify
#   30 GB           the free standard-PD allowance, exactly
#   pd-standard     balanced/SSD are not in the free tier
#   non-preemptible the free instance must not be Spot
#
# See ALWAYS-FREE.md. Changing any of these starts a bill.
set -euo pipefail

NAME="${NAME:-hermes-iowa}"
ZONE="${ZONE:-us-central1-a}"
MACHINE="${MACHINE:-e2-micro}"
DISK_GB="${DISK_GB:-30}"
DISK_TYPE="${DISK_TYPE:-pd-standard}"
IMAGE_FAMILY="${IMAGE_FAMILY:-debian-13}"
IMAGE_PROJECT="${IMAGE_PROJECT:-debian-cloud}"

case "$ZONE" in
  us-west1-*|us-central1-*|us-east1-*) ;;
  *) echo "REFUSING: $ZONE is not an always-free region." >&2
     echo "Only us-west1, us-central1 (Iowa), us-east1 qualify." >&2
     exit 1 ;;
esac
[ "$MACHINE" = "e2-micro" ] || { echo "REFUSING: $MACHINE is not always-free." >&2; exit 1; }
[ "$DISK_TYPE" = "pd-standard" ] || { echo "REFUSING: $DISK_TYPE is not always-free." >&2; exit 1; }
[ "$DISK_GB" -le 30 ] || { echo "REFUSING: ${DISK_GB}GB exceeds the 30GB free allowance." >&2; exit 1; }

# You get ONE free e2-micro per billing account per month. A second one bills
# in full, so refuse rather than quietly double the cost.
existing=$(gcloud compute instances list \
  --filter="machineType~e2-micro AND (zone~us-west1 OR zone~us-central1 OR zone~us-east1)" \
  --format="value(name)" | grep -vx "$NAME" || true)
if [ -n "$existing" ]; then
  echo "WARNING: an always-free-eligible e2-micro already exists:" >&2
  printf '  %s\n' $existing >&2
  echo "Only one is free per month; this new VM will be billed." >&2
  read -rp "Create anyway? [y/N] " a; [ "$a" = y ] || exit 1
fi

gcloud compute instances create "$NAME" \
  --zone="$ZONE" \
  --machine-type="$MACHINE" \
  --image-family="$IMAGE_FAMILY" \
  --image-project="$IMAGE_PROJECT" \
  --boot-disk-size="${DISK_GB}GB" \
  --boot-disk-type="$DISK_TYPE" \
  --boot-disk-device-name="$NAME" \
  --provisioning-model=STANDARD \
  --no-restart-on-failure \
  --metadata=enable-oslogin=TRUE \
  --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write \
  --labels=app=hermes,tier=always-free

cat <<EOF

Created $NAME in $ZONE.

The instance has an ephemeral external IPv4. That address is billed hourly and
is the one line item the always-free tier does not cover (see ALWAYS-FREE.md).
Do not reserve a static IP -- an unattached reserved address costs more, and
Telegram long-polling needs no stable inbound address.

Next: bin/bootstrap.sh
EOF
