# Agent Skills

The published subset of the skill library used by Khermes
([@kapilebot](https://t.me/kapilebot)). Context and rationale:
[Agent Skills](../../projects/agent-skills.md).

Each directory is one skill. `SKILL.md` holds the frontmatter and procedure;
`references/` holds deep material loaded only when relevant; `scripts/` holds
executable helpers.

| Skill | Use when |
| --- | --- |
| [cloud-vm-maintenance](cloud-vm-maintenance) | A small cloud VM is out of RAM or disk, or real latency numbers are needed |
| [evidence-first-research](evidence-first-research) | A research claim needs explicit baselines and falsification gates |
| [hermes-provider-diagnosis](hermes-provider-diagnosis) | A model route keeps failing and the fault must be classified |
| [kbrain-curation](kbrain-curation) | Private working context must become durable public knowledge safely |
| [multi-agent-chat-topologies](multi-agent-chat-topologies) | Several agents must share one channel without feedback loops |
| [safe-agent-handoff](safe-agent-handoff) | Work must move between agents with explicit state and authority |
| [secret-config-operations](secret-config-operations) | A credential file must be edited without exposing values |
| [trading-strategy-validation](trading-strategy-validation) | A profitable-looking strategy or backtest must be challenged first |
| [verified-delivery](verified-delivery) | Work must be implemented, exercised, and verified end to end |

## Reading These Outside My Setup

These are written for an agent with shell and file access, and some name
Hermes-specific tools. The procedures are portable; the exact tool names may
not be. `trading-strategy-validation` is the deepest research checklist, while
the four newer workflow skills encode the operating rules used to maintain this
knowledge base.

## Boundary

Skills that encode private deployment detail — repository layouts, credential
search paths, service definitions, hosts, or accounts — are not published here.
See the [publication boundary](../../decisions/publication-boundary.md).
