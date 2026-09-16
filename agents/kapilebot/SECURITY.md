# Security Boundary

This directory is an allowlisted export of public agent material. It is not a
backup of the live Hermes installation.

## Included

- Public identity and Telegram username
- General behavior and operating principles
- Capability names and short descriptions
- Original kbrain-specific skills
- Links to public upstream projects

## Excluded

- Environment files, API keys, OAuth material, tokens, and cookies
- Hermes authentication files and connector credentials
- Session databases, transcripts, request dumps, and logs
- Cron state, process state, caches, pairings, and runtime sockets
- Private memories, account activity, deployment details, and local paths
- Vendored third-party skill bodies without a separate rights review

## Release Check

Before every update:

1. Review only the files intended for publication.
2. Scan the staged tree and Git history for secrets.
3. Check links and Markdown structure.
4. Confirm that no private operational state entered the diff.
5. Push only after the exact commit passes those checks.
