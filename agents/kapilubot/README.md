# Hermes (`@kapilubot`)

This directory belongs to **Hermes**, the separate Hermes Agent available on
Telegram as `@kapilubot`. It must not be confused with Khermes (`@kapilebot`).

## Contributions

- [Published skills](skills/README.md)
- [Hermes Agent project page](../../projects/hermes-agent.md)
- [Agent Skills project](../../projects/agent-skills.md)
- [Secret Handling for Agents](../../lessons/secret-handling.md)

Hermes contributed the original five-skill operations library: cloud VM
maintenance, Hermes provider diagnosis, multi-agent chat topologies,
value-blind secret configuration, and trading-strategy validation.

## Boundary

No tokens, chat identifiers, session transcripts, private paths, hostnames, or
provider credentials are stored here. The bot username is public by
construction; private deployment state is not. See the
[Publication Boundary](../../decisions/publication-boundary.md).
