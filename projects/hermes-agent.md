# Hermes Agent

A long-running personal agent I talk to over Telegram, hosted on a single GCP
always-free `e2-micro` in Iowa. Upstream is
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent); the
work here is the deployment, not the agent framework.

Status: **maintained**.

## Shape

One VM, one user-level systemd unit, Telegram as the only interface. No
inbound ports, no webhook, no load balancer, no container orchestration. The
agent long-polls Telegram, so the box needs outbound internet and nothing
else — which is what makes a 964 MB instance with an ephemeral IP a
sufficient host.

The deployment is reproducible from
[`hermes/`](../hermes/README.md): provision the correctly-shaped free VM,
install the pinned upstream, paste five secrets, start the unit.

## What this taught me

**An "export the whole disk" instinct was wrong by two orders of magnitude.**
A deployed agent's disk decomposes into a few GB of upstream checkout, a few
more of installer-fetched toolchain, about a GB of cache and per-install
environments, whatever co-tenant projects write, and a few tens of MB that
are actually mine. Of that remainder, the part worth keeping is also the part
that must never be public. The right export was a pinned upstream SHA plus a
credential template — ~99% smaller than the disk and the only safe shape.

**`active (running)` is not evidence the agent works.** A gateway with a bad
token, an empty allowlist, or a broken import sits in `active (running)` while
round-tripping nothing. The checks that actually bind are external: has a
Telegram update been acknowledged, and recently; is the heartbeat fresh; are
there error lines the process survived.
[`preflight.sh`](../hermes/bin/preflight.sh) asserts those and exits non-zero,
because a unit state check would have passed in every failure mode worth
catching.

**User-level systemd needs lingering, and fails silently without it.** The
unit runs under `systemd --user`, which exits at logout unless the user
lingers. Lose that and the agent dies at the next reboot with nothing in the
system journal explaining it — and `sudo systemctl status hermes-gateway`
reports the unit does not exist, which sends you looking in the wrong place.

**"Always free" is a shape you have to hold, not a tier you fall back to.** A
lapsed trial closes the billing account and stops every VM; the free
allowances only apply once you have upgraded to a paid account. And the free
tier covers compute and disk, not the external IPv4 address every
internet-reachable VM needs — so the floor is a few dollars a month, not zero.
Written up in [ALWAYS-FREE.md](../hermes/ALWAYS-FREE.md).

**The binding constraint on a 1 GB VM is RAM, not CPU.** An `e2-micro` has
964 MB, and the agent carries a Chromium for its browser tools. Bootstrap
adds a swapfile with `vm.swappiness=10` because the realistic failure is an
OOM kill mid-turn, not a slow turn — and on a shared box, moving the
co-tenant off buys more headroom than trimming the agent does.
