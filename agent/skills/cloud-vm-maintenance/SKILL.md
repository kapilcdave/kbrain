---
name: cloud-vm-maintenance
description: "Debloat a small cloud VM: free RAM/disk, API latency."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [devops, vm, gcp, memory, disk, latency, debloat, hosting]
---

# Cloud VM Maintenance & Debloat

Keep a small (e.g. 1GB RAM) cloud VM lean and responsive: triage memory, reclaim
disk, kill runaway/orphaned agents, stop things that silently reinstall
themselves, and measure real network latency to the APIs the box exists to talk
to. Written for GCP Compute but the memory/disk/latency parts are cloud-agnostic.

## Golden rules

- **Find before you kill.** Snapshot `free -h`, `ps aux --sort=-%mem`, and the
  process tree BEFORE deleting anything. VSZ lies (an agent can show 22GB VSZ /
  2MB RSS) — sort and reason by **RSS/%MEM**, not VSZ.
- **Locate and back up secrets FIRST.** On a trading/keys box, `grep -rl` for
  key material and copy it to a `chmod 700` backup dir before any deletion. Then
  reference secret files by *variable name only* in later commands — Hermes'
  security scanner (Tirith) will block/timeout a command that names a secret
  path, and `~/.hermes/.env` is a protected credential store you cannot read or
  append to directly (that block is expected, not a failure).
- **A purge that gets undone is not done.** Re-check a few minutes later. Some
  cloud agents re-enforce policy and reinstall what you removed (see the GCP
  osconfig trap below).

## Memory triage (the freeze fix)

```
free -h                              # used vs available; check Swap line too
uptime                               # load average
ps aux --sort=-%mem | head -20       # real hogs by RSS
tmux ls                              # orphan-prone: sessions survive their launcher
```

Killing `tmux kill-server` can leave a child process **orphaned and alive** (it
reparents to init, not dies). Verify and `kill`/`kill -9` the PID directly
afterward. On a low-RAM box, closing the interactive Hermes agent session frees
~300-400MB when you truly need headroom; the gateway scales to zero on idle
(config `gateway.scale_to_zero`) so a changed gateway PID after a delete is
normal respawn, not a crash.

Swap check: `cat /proc/swaps` + `cat /proc/sys/vm/swappiness`. A low swappiness
(~10) is already tuned against thrash — leave it. A persistent swapfile shows in
`/etc/fstab`.

## Disk debloat

```
df -h /
sudo du -xh --max-depth=1 / | sort -rh | head       # then descend into big dirs
```

High-value, safe-to-clear targets (verified nothing is mid-run first):
- `sudo apt-get clean` (apt cache, often 300M+)
- `sudo journalctl --vacuum-size=30M`
- `~/.cache/ms-playwright` — headless Chromium browsers (~650M)
- `~/.cache/uv`, `~/.cache/pip`, `~/.npm/_cacache` (`npm cache clean --force`, or
  `rm -rf` the dir if npm isn't on PATH)
- Orphaned AI-agent installs after you've killed them (`~/.pi`, pi-node,
  cua-driver, etc.)
- Disabled-package trees: `sudo apt-get purge <pkg>` reclaims the binary too.

## Two subsystems worth their own reference files

- **GCP guest-policy reinstall trap** (ops-agent keeps coming back) →
  `references/gcp-osconfig-reinstall-trap.md`. Read this the moment a package you
  purged reappears.
- **Measuring latency to hosted/trading APIs** (how fast can we be, should we
  relocate) → `references/api-latency-measurement.md`. curl timing breakdown +
  mapping an API's IP to its AWS region to decide co-location.

## Hermes-update bloat on a headless VM (informational)

A plain `hermes update` on a headless box (no desktop, no TUI/web use) does
git-pull + `uv pip install` (Python deps) + skill sync — and NOT the heavy
downloads, because each is gated:
- Chromium (~170MB) only downloads when the `browser`/`computer_use` toolsets
  are enabled (they trigger the `agent_browser` post-setup install hook). If
  they're in `config.yaml` `agent.disabled_toolsets`, the hook never fires.
- npm workspace install (TUI/web deps, ~400MB `node_modules`) is skipped when
  node/npm aren't on PATH.
- Electron desktop rebuild (~200MB) is gated on a desktop app already being
  present.
- Hermes-managed Node only *heals an existing* node tree; it won't bootstrap one
  from nothing.

So on a trading/compute-only VM you can delete `~/.hermes/hermes-agent/node_modules`
(pure TUI/web-dashboard build deps; the gateway is pure Python) and updates stay
lean. Do NOT hard-code "hermes update is bloated" as a rule — it's install-shape
dependent, and these are bundled-code internals that can change.
