# Hermes Gateway — Deployment

The Telegram-facing [Hermes agent](https://github.com/NousResearch/hermes-agent)
running continuously on a GCP always-free `e2-micro` in Iowa
(`us-central1`). This directory is everything needed to rebuild that
deployment from nothing.

It is deliberately **not** a copy of the VM's disk. See
[What is not here](#what-is-not-here) for why, and
[ALWAYS-FREE.md](ALWAYS-FREE.md) for the cost envelope.

## Plug and play

On any machine with `gcloud` authenticated:

```sh
git clone https://github.com/kapilcdave/kbrain.git
cd kbrain/hermes

bin/provision-vm.sh          # creates the always-free e2-micro in us-central1
bin/bootstrap.sh             # installs hermes + the gateway unit on it
bin/preflight.sh             # proves Telegram round-trips before you trust it
```

`bootstrap.sh` stops once to have you paste the secrets listed in
[`config/.env.example`](config/.env.example). Nothing else is interactive.

To bring back an existing brain — conversation history, memories, provider
credentials — instead of starting clean:

```sh
bin/restore-brain.sh <snapshot-name>
```

## What runs

| Component | Detail |
|---|---|
| Upstream | `NousResearch/hermes-agent` pinned at [`1fd1827`](https://github.com/NousResearch/hermes-agent/commit/1fd18277267152893a8a24792b79213e7ca3f899) |
| Process | `hermes gateway run`, as a **user** systemd unit, not a system one |
| Unit | [`systemd/hermes-gateway.service`](systemd/hermes-gateway.service) |
| Environment | `HERMES_HOME=~/.hermes`, linger enabled so it survives reboot |
| Host | Debian 13 (trixie), cloud-amd64, x86_64 |
| Interface | Telegram, long-poll; no inbound ports, no webhook, no public listener |
| Restart | `Restart=always`, `RestartSec=5`; exit 78 means "do not restart" |

Running under `systemd --user` with lingering is what makes a reboot
survivable without root. Two consequences worth remembering:

- `sudo systemctl status hermes-gateway` will report that the unit does not
  exist, which sends you looking in the wrong place. You need the user
  manager, which needs `XDG_RUNTIME_DIR` pointed at the right uid:

  ```sh
  U=<hermes-user>
  sudo -u "$U" XDG_RUNTIME_DIR=/run/user/$(id -u "$U") \
    systemctl --user status hermes-gateway
  ```

- If lingering is ever lost, the agent dies at the next reboot and nothing in
  the system journal explains why. `loginctl enable-linger <user>` restores
  it; `preflight.sh` asserts it.

## What is not here

Committing the disk would be committing almost nothing of ours. Proportions
from a working install:

| Component | Scale | Why it is not in git |
|---|---|---|
| Upstream checkout | ~2.5 G | Clean tree at a known SHA. Pinned, not vendored. |
| Toolchain (`tools/`) | ~1.6 G | Chromium, ffmpeg, node, uv — the installer re-fetches these. |
| Cache | ~800 M | Regenerable by definition. |
| Per-install environments | ~300 M | Rebuilt by bootstrap. |
| Agent state (`state.db`) | ~45 M | **The brain.** Private transcripts, and it contains credential-shaped strings. |
| Session dumps | ~8 M | Raw request payloads — full prompts and responses. |
| `.env`, `auth.json` | ~45 K | Live bot token and provider API keys. |
| Co-tenant projects | varies | Other work that happens to share the box. |

So nearly all of it is third-party bytes or regenerable cache, and the small
remainder is exactly the part that must never be public. A pinned upstream SHA
plus a credential template is both ~99% smaller than the disk *and* the only
safe shape.

State and credentials live in a **GCE disk snapshot** in the project instead:
in-project, encrypted at rest, never transiting GitHub.
[`bin/restore-brain.sh`](bin/restore-brain.sh) is the path back. Take one
before any risky change:

```sh
gcloud compute disks snapshot <disk> --zone <zone> --snapshot-names <name>
```

## Operating it

```sh
U=<hermes-user>; export XDG_RUNTIME_DIR=/run/user/$(id -u "$U")

sudo -u "$U" journalctl --user -u hermes-gateway -f   # follow
sudo -u "$U" systemctl --user reload hermes-gateway   # reload config
```

`ExecReload` sends `SIGUSR1`, which the agent handles as a config reload.
Prefer it over a restart, which drops in-flight turns.

## Memory headroom

An `e2-micro` has 964 MB of RAM and Hermes carries a Chromium for its browser
tools. Enabling a browser-heavy skill, or raising
`terminal.container_memory`, is the most likely way to OOM it — check
`free -m` first. `bootstrap.sh` adds a 1 GB swapfile with
`vm.swappiness=10` because the realistic failure is an OOM kill mid-turn, not
a slow turn. If the box is shared, moving the co-tenant off it buys more than
trimming Hermes does.

## Layout

```text
hermes/
  bin/provision-vm.sh     create the always-free VM, correctly shaped
  bin/bootstrap.sh        install hermes + unit on a fresh VM
  bin/restore-brain.sh    recover state/credentials from a snapshot
  bin/preflight.sh        assert the gateway is actually live
  config/.env.example     the required secrets, as placeholders
  config/UPSTREAM         pinned upstream repo + SHA
  config/config.reference.md  which config.yaml keys are tuned
  config/toolchain.txt    expected toolchain versions
  config/skills.txt       expected skill packs
  systemd/                the user unit, templated
  ALWAYS-FREE.md          free-tier compliance and the real monthly cost
```
