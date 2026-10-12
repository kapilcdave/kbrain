# Khermes: public bootstrap

The **publication-safe** portion of the Hermes Agent installation: enough to
rebuild the VM and the gateway from nothing, and nothing that the
[publication boundary](../decisions/publication-boundary.md) excludes. This
repository is public, so that boundary takes precedence over a verbatim
export of private state.

This is not a disk image and not a complete agent backup. Read
[HANDOFF.md](HANDOFF.md) before retiring a source machine.

## Rebuild a VM

With `gcloud` authenticated:

```sh
git clone https://github.com/kapilcdave/kbrain.git
cd kbrain/khermes

bin/provision-vm.sh     # always-free e2-micro in us-central1, correctly shaped
bin/bootstrap.sh        # pinned upstream, gateway unit, swap, lingering
bin/preflight.sh        # proves Telegram round-trips before you trust it
```

`bootstrap.sh` stops once for the secrets in
[`config/.env.example`](config/.env.example). Those are the only manual step,
and they are deliberately not in Git.

All three scripts take `NAME`, `ZONE` and `HERMES_USER` from the environment.
Set `HERMES_USER` whenever the agent runs as a different account than the one
you SSH in as, or the checks inspect the wrong account and report a confident
total failure for a healthy agent:

```sh
NAME=<vm> HERMES_USER=<agent-user> bin/preflight.sh
```

Then, optionally:

```sh
bash restore.sh                      # portable config settings, no secrets
bin/restore-brain.sh <snapshot-name> # prior state, from a private GCE snapshot
```

`hermes setup` remains the interactive alternative to hand-writing `.env` —
use whichever you prefer, but configure the model and Telegram connection on
the **new** machine rather than copying credentials out of Git.

## What is here

| File | Purpose |
|---|---|
| `bin/provision-vm.sh` | Creates the VM. Encodes every free-tier limit as a refusal, not a default. |
| `bin/bootstrap.sh` | Installs the pinned upstream, the user systemd unit, a swapfile, lingering. Idempotent. |
| `bin/preflight.sh` | Asserts the gateway is *live*, not merely `active (running)`. Exits non-zero. |
| `bin/restore-brain.sh` | Restores state and credentials from a GCE snapshot, with an integrity check. |
| `restore.sh` | Applies a short list of portable, non-secret config settings after setup. |
| `config/UPSTREAM` | The pinned upstream repo and commit. Bump deliberately. |
| `config/.env.example` | Required secrets, as placeholders. |
| `config/config.reference.md` | Which `config.yaml` keys are tuned away from default, and which matter on 1 GB. |
| `systemd/` | The user unit, templated. |
| `ALWAYS-FREE.md` | Free-tier compliance and the real monthly cost. |
| `HANDOFF.md` | The private material that is **not** here, and the migration checklist. |

## Why the source tree is not duplicated here

The upstream checkout and installer-fetched toolchain are several GB of
third-party bytes; caches and per-install environments add about a GB; the
agent's own state is tens of MB — and that small remainder is exactly the part
that must never be public. So the export is a pinned SHA plus a credential
template: roughly 99% smaller than the disk, and the only shape compatible
with a public repository.

Published research, principles and agent skills stay in their canonical
locations under [`agents/`](../agents/), [`projects/`](../projects/),
[`lessons/`](../lessons/) and [`research/`](../research/).

## How plug-and-play this actually is

- **Infrastructure: yes.** Three commands produce a running, reboot-surviving
  gateway on a correctly-shaped free VM.
- **Secrets: no, by design.** You paste them once, or re-authorize on the new
  host. Tokens, OAuth grants and keys are never in this repo.
- **History and personality: only via the private path.** Chat history, the
  session store, private skills, `SOUL.md`, cron jobs and machine-specific
  state come from a snapshot or a secure private channel —
  `bin/restore-brain.sh` or the [handoff checklist](HANDOFF.md), not Git.

Do not deactivate an old VM until `bin/preflight.sh` passes on the new one and
anything in HANDOFF.md that matters has actually been transferred.
