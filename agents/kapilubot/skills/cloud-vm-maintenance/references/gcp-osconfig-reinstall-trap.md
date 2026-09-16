# GCP osconfig reinstall trap (ops-agent keeps coming back)

## Symptom
You `systemctl stop/disable` and `apt-get purge google-cloud-ops-agent`. It's
gone. ~10-15 minutes later `otelopscol` + `fluent-bit` are running again and the
package is reinstalled (`dpkg -l | grep ops-agent` shows `ii`, and the 262MB
binary is back in `/opt`). On a 1GB VM this stack is ~90MB RAM — a real hog.

## Root cause
The **google-osconfig-agent** re-enforces a GCP OS Config guest policy. It is
driven by instance metadata `enable-osconfig=TRUE`. As long as osconfig runs, it
will undo any ops-agent removal. Confirm the reinstall in `/var/log/dpkg.log`
(you'll see a fresh `install google-cloud-ops-agent` line minutes after your
purge) and the driver via:
```
curl -s -H "Metadata-Flavor: Google" \
  "http://metadata.google.internal/computeMetadata/v1/instance/attributes/enable-osconfig"
```

## Fix A — in-VM, durable, no external auth (do this first)
Mask the reinstaller AND the target so neither can run or be restarted; masking
symlinks the unit to /dev/null and survives reboots:
```
sudo systemctl stop google-osconfig-agent && sudo systemctl mask google-osconfig-agent
sudo systemctl stop google-cloud-ops-agent google-cloud-ops-agent-fluent-bit \
     google-cloud-ops-agent-opentelemetry-collector
sudo systemctl mask google-cloud-ops-agent
sudo apt-get purge -y google-cloud-ops-agent
```
Verify it STAYS gone: `sleep a few min`, then `ps aux | grep -E '[o]telops|[o]sconfig'`.
Tradeoff: you lose GCP-managed OS patch policies + Cloud Monitoring/Logging
ingestion. Fine for a personal trading/compute VM — `unattended-upgrades` still
handles security patches.

## Fix B — GCP-side, stops it at the source (belt-and-suspenders)
Set the metadata flag so GCP never even tries on boot:
```
gcloud compute instances add-metadata <INSTANCE> --zone=<ZONE> \
  --metadata=enable-osconfig=FALSE
```
This usually CANNOT be run from inside the VM: the default compute service
account lacks the scope (`Request had insufficient authentication scopes`). Run
it from a machine where the user is authed with Compute rights.

### gcloud gotchas that ate real time here
- **Wrong project.** A laptop's gcloud often defaults to a *different* project
  than the VM lives in. Get the VM's true project from inside it:
  `curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/project/project-id`
  The `add-metadata` errored with `Required 'compute.instances.get' permission`
  purely because gcloud was pointed at the wrong project.
- **Use the string project ID, not the numeric one.** `gcloud config set project
  <NUMBER>` makes `add-metadata` fail with *"core/project is set to project
  number... set to PROJECT ID"*. Set the string ID instead.
- **GCP project IDs max out at 30 chars** and can look truncated but aren't —
  verify with `echo -n "$pid" | wc -c` before assuming it got cut off.

## Getting instance identity from inside the VM
```
curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name
curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone | awk -F/ '{print $NF}'
curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/project/project-id
```
(Tirith flags the plain-http metadata URL as a download-to-interpreter risk; it's
the standard GCP metadata endpoint — approve and proceed.)
