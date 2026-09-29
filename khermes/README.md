# Khermes: public bootstrap

This is the **publication-safe** portion of the Hermes Agent installation. It is not a disk image or a complete agent backup. This repository is public, so the [publication boundary](../decisions/publication-boundary.md) takes precedence over a verbatim export of private state.

## Fresh VM

1. Install Hermes Agent using the [official installer](https://hermes-agent.nousresearch.com/docs/) and complete `hermes setup` on the new VM. Configure your model and Telegram connection there; do not copy credentials from Git.
2. Clone `https://github.com/kapilcdave/kbrain.git` and run `bash kbrain/khermes/restore.sh` from the directory containing the clone. The script applies only a short list of portable settings. It does **not** install third-party binaries or start services.
3. Read `khermes/HANDOFF.md` for private items to migrate separately and current-state caveats. Run `hermes doctor` and test the CLI and Telegram gateway before retiring the old machine.

The Hermes source checkout and bundled skills are intentionally not duplicated here. Install Hermes on the new host; the existing published research, principles and agent skills remain in their canonical locations under [`agents/`](../agents/), [`projects/`](../projects/), [`lessons/`](../lessons/) and [`research/`](../research/). This snapshot is for the active Hermes personality and conservative configuration, not a claim that an older `kapilubot` or `kapilebot` persona is the same instance.

## What this covers

- `restore.sh`: opt-in, idempotent portable configuration, no secrets.
- `HANDOFF.md`: boundaries, migration checklist and verification.

**Not plug-and-play without the private handoff.** Auth tokens, OAuth grants, exchange credentials, private skills, full chat history, cron tasks and machine-specific deployment state are deliberately absent. Do not deactivate the old VM before transferring any of those that matter through a secure private channel.
