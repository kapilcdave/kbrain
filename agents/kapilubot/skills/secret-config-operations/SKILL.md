---
name: secret-config-operations
description: "Use when editing secret files. Prevent credential leaks."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    category: devops
    tags: [secrets, env, credentials, security, configuration]
    created_by: agent
---

# Secret Config Operations

Handle `.env`, keyfiles, credential stores, and authenticated-client settings
without allowing tool output, diffs, logs, process arguments, or Git to disclose
values.

## Procedure

### 1. Discover without reading values

Locate the file, then use `scripts/safe_env.py inspect PATH`. Report only:

- variable names;
- set / empty status;
- value length;
- malformed line numbers;
- owner and permission mode.

Never use `read_file` on a secret file. Never print prefixes or suffixes as a
“safe preview”; partial tokens can still be sensitive and make later rotation
ambiguous.

### 2. Validate capabilities without echoing credentials

Load credentials inside a short file-based script, call the cheapest read-only
health or identity endpoint, and print only status code plus a non-sensitive
result such as `health=ok`, row count, or authenticated account ID hash. Do not
use verbose HTTP modes, shell tracing, exception bodies that may contain request
headers, or inline interpreter payloads containing secrets.

Validate identifiers separately from credentials. A public wallet address may be
shown only when the user supplied it publicly; still compare exact values and
chain format before configuring it.

### 3. Edit without unified diffs

Do **not** use a patch tool on a secret-bearing file: unified diffs include
neighboring context lines and can expose unrelated credentials. Do not rewrite
the whole file with a file-writing tool either, because the complete secret set
would enter the tool call.

For key-only renames, use:

```bash
python3 scripts/safe_env.py rename PATH OLD_KEY NEW_KEY
```

The helper preserves the value, writes atomically, forces mode `0600`, and emits
only key names. For a new or rotated secret value, have the user edit it locally
or use an approved secret manager/input channel that does not place the value in
chat, command arguments, or tool output.

### 4. Verify the effect safely

Run `safe_env.py inspect PATH` again and verify the target key name, set status,
permissions, and absence of the old key. Then exercise the exact read-only API
that depends on it. A syntactically present key is not a working credential.

Check repository tracking separately. Secret files belong outside the repository
or under a verified ignore rule; never stage them to test whether ignore works.

### 5. Respond to accidental disclosure

If any tool output shows a credential value, say so immediately without
repeating it. Name the affected services/keys, stop state-changing use of those
credentials, and require rotation or revocation before live execution. Do not
claim that an internal-only diff is harmless: transcripts, approvals, and tool
logs extend the exposure boundary.

## Always-on rules

- Keep credential files mode `0600` and owned by the service user.
- Distinguish public identifiers from signing secrets; a public address is safe
  to configure, but it does not authorize spending.
- Never infer transfer authorization from the presence of a private key. Require
  exact source, network, asset, amount, destination, and worst-case fee.
- Keep research API keys separate from wallet signing keys.
- Never load a primary-wallet seed into an unattended bot. Use a dedicated,
  capped wallet only after an explicit live-risk gate.

## Supporting script

- `scripts/safe_env.py` — value-blind inspection and atomic key renaming for
  dotenv-style files.
