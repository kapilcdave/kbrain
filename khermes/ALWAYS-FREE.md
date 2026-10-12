# Staying on GCP's always-free tier

What the free tier covers, how this deployment is shaped to fit it, and the
charges that remain. Verified against Google's
[free tier documentation](https://cloud.google.com/free/docs/free-cloud-features)
on 2026-10-12.

## The one thing that is not automatic

> "If you don't upgrade to a paid account within 90 days, your Free Trial
> billing account will be closed and all of its associated projects and
> resources will be stopped."

The always-free tier is **not** what you fall back to when a trial expires. A
trial that ends without being upgraded closes the billing account and stops
every VM, with a 30-day grace period before permanent deletion.

So the required action is to **upgrade to a paid (self-serve) billing
account** *before* the trial ends, and then stay inside the free limits. On a
paid account the always-free allowances apply as a monthly discount and a
compliant `e2-micro` costs nothing to run. Letting the trial lapse is the one
path that loses the agent.

## What always-free covers

| Allowance | Limit |
|---|---|
| VM instance | 1 non-preemptible `e2-micro` per month |
| Region | `us-west1`, `us-central1` (Iowa), `us-east1` only |
| Persistent disk | 30 GB-months, `pd-standard` |
| Egress | 1 GB/month outbound from North America |
| GPU / TPU | never free |

[`provision-vm.sh`](bin/provision-vm.sh) encodes every one of these as a
refusal rather than a default, so a rebuild cannot drift out of the tier by
accident.

The allowance is one free `e2-micro` per **billing account**, not per project.
A second eligible `e2-micro` anywhere bills in full, which is why the script
checks for an existing one before creating another.

## What still costs money

**External IPv4.** Since 2024 Google bills every external IPv4 address
attached to a VM, ephemeral ones included, at roughly $0.005/hour — call it
**$3–4/month**. The free tier does not cover it. Confirm the current rate on
the [VPC pricing page](https://cloud.google.com/vpc/network-pricing) rather
than trusting this figure.

There is no cheaper way out for this workload. The agent needs outbound
internet for Telegram long-polling and model APIs, and a VM with no external
address needs Cloud NAT to get it — which starts around $32/month. Keep the
ephemeral address and accept a few dollars. Do **not** reserve a static IP:
the same charge applies while it is attached, a higher one while it is not,
and long-polling never needs a stable inbound address.

**Snapshot storage.** Snapshots are not in the free tier; they run around
$0.026/GB/month, so a snapshot of a mostly-empty 30 GB disk lands near
$0.25/month. That is the deliberate price of keeping credentials and agent
state off GitHub, and it is the cheapest line item involved. Delete
superseded snapshots instead of accumulating them.

**Realistic floor: roughly $3–5/month**, nearly all of it the IPv4 address.
"Always free" means the compute and the disk are free, not that the bill is
zero.

## The two standing risks

**Disk.** 30 GB is simultaneously the disk size and the entire free
allowance, so there is no headroom to grow into — resizing starts billing the
whole disk. The agent's own footprint is stable; the thing that fills a shared
box is whatever else writes to it on a schedule. If another project shares the
VM, prune or offload its output rather than resizing.
[`preflight.sh`](bin/preflight.sh) fails at 90% so this surfaces before the
agent starts failing writes.

Roughly how an installed agent occupies disk, worth knowing before assuming
state is large: the upstream checkout and the installer-fetched toolchain
dominate at several GB, caches and per-install environments add about a GB,
and the agent's actual state is tens of MB. Almost nothing on the disk is
irreplaceable, which is the whole argument in
[the deployment README](README.md#what-is-not-here).

**Egress.** 1 GB/month outbound from North America is a low ceiling and
nothing meters it by default. Telegram text is negligible; a browser toolset
uploading screenshots, or any bulk transfer off the box, is not. Inbound and
in-region traffic do not count. A billing alert at $1 is a cheap tripwire
that catches both an egress surprise and an IPv4 rate change.

## Resources that can never be free

Only `e2-micro` qualifies, and only in the three US regions above. An
instance that is the wrong size, or the right size in the wrong region, bills
from the moment a trial converts to a paid account — there is no partial
credit. Audit for those before the conversion rather than after the first
invoice, and decide deliberately whether each one is worth its charge.

## Checking compliance

```sh
# the free instance: must be e2-micro / STANDARD / us-central1|us-east1|us-west1
gcloud compute instances list \
  --format="table(name,zone,machineType.basename(),scheduling.provisioningModel)"

# the free disk: must be 30GB pd-standard
gcloud compute disks list --format="table(name,zone,sizeGb,type)"

# anything reserved or stored is a charge you may not have meant to take on
gcloud compute addresses list
gcloud compute snapshots list --format="table(name,storageBytes)"
```
