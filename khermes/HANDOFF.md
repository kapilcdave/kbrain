# Private handoff and verification

This repo is public. The active Hermes installation has private material which is **not** committed here. Do not treat this directory as a complete backup or delete the source VM on its strength.

## Transfer separately, only after choosing a secure private destination

- Provider credentials, OAuth grants, Telegram token, exchange credentials, SSH keys and any other secrets. Re-authorize on the new VM; never upload raw `.env`, `auth.json`, credential-store files, key files or shell history to public Git.
- Private Hermes memory and user profile, if desired. The old default profile has a `memories/MEMORY.md` file, but **memory and user-profile features are disabled in the current config**. Full chats live in a SQLite session store and may contain private data or secrets; do not publish it.
- Locally modified and custom skills. The installed skills tree contains bundled content plus modified and additional files; importing it wholesale would duplicate upstream and may publish private operational procedures. Compare against the Hermes source `skills/` tree, review differences, then move only approved files in a private handoff.
- Scheduled jobs and local scripts: four cron jobs were present at snapshot time, all disabled. Review each command, destination and credential reference before restoring; leave disabled until its dependencies are migrated. Machine-specific service units, trading projects and runtime databases also need their own migration plan.
- Agent-personality files such as `SOUL.md` were not copied into this public snapshot. Restore through an approved private channel if needed.

## Checklist on new VM

1. `hermes setup`, model/provider auth, Telegram setup, and `hermes doctor` on the **new** machine.
2. Run `bash khermes/restore.sh` inside the cloned repository, then inspect `hermes config show`. The script intentionally leaves the default model and provider selected by setup; do not infer them from an older on-disk config after an in-chat model switch.
3. Migrate only approved private materials using a secure channel, applying restrictive permissions. Restore cron jobs only after confirming scripts, dependencies, destinations and the intended enabled/disabled state.
4. Test one CLI request, one Telegram request, memory behavior (if you deliberately enable it), and every retained job/service. Check the remote repository contains only the reviewed public files.
5. Keep the original machine available until these checks pass and any needed chat history or raw data has been transferred separately.

This file is an inventory of **gaps**, not evidence those gaps have been backed up.
