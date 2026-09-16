# agent/skills

The published subset of the skill library used by my Hermes agent
(`@kapilubot`). Context and rationale: [Agent Skills](../../projects/agent-skills.md).

Each directory is one skill. `SKILL.md` holds the frontmatter and the procedure;
`references/` holds deep material loaded only when relevant; `scripts/` holds
executable helpers.

| Skill | Use when |
|---|---|
| [cloud-vm-maintenance](cloud-vm-maintenance) | A small cloud VM is out of RAM or disk, or you need real latency numbers to a hosted API |
| [hermes-provider-diagnosis](hermes-provider-diagnosis) | A model or provider route keeps failing and you need to classify the fault before reacting |
| [secret-config-operations](secret-config-operations) | Editing a credential file without leaking values into diffs, logs, or transcripts |
| [multi-agent-chat-topologies](multi-agent-chat-topologies) | Wiring several agents into one shared channel |
| [trading-strategy-validation](trading-strategy-validation) | A strategy or backtest looks profitable and you need to try to kill it first |

## Reading These Outside My Setup

These are written for an agent with shell and file access, and they name that
agent's own quirks where relevant. The procedures are portable; the tool names
are not. `trading-strategy-validation` is the most generally useful of the five
and stands alone as a research checklist.

## Boundary

Skills that encode private deployment detail — repository layouts, credential
search paths, service definitions, hosts, accounts — are not published here.
See the [publication boundary](../../decisions/publication-boundary.md).
