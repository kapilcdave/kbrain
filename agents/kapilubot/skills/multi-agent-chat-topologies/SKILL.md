---
name: multi-agent-chat-topologies
description: "Wire multiple AI agents into one shared chat channel."
tags: [multi-agent, messaging, telegram, discord, slack, group-chat, hermes-profiles, orchestration]
---

# Multi-Agent Chat Topologies

For any request shaped like "put my two agents and me in a group chat", "have
agent A and agent B talk to each other", "set up a second bot in this channel",
or "make them collaborate in Slack/Discord/Telegram".

**The first question is never configuration. It is: what can each participant
physically SEE?** Messaging platforms restrict bot-to-bot visibility at the API
level, and no amount of config changes that. Establish the visibility matrix
before proposing a single YAML key.

## Step 1: Determine the desired topology precisely

Users describe several very different topologies with the same words. Pin down
which one before researching anything:

| topology | each agent replies to | each agent SEES |
|---|---|---|
| **Parallel advisors** | the human | only the human |
| **Shared context** | the human | human + other agents |
| **Conversational** | human *and* each other | everything |

Parallel advisors is nearly always available and often delivers most of the
value. Conversational is the one that carries the loop hazard below. Do not
assume the user means the simplest one — ask or infer, then confirm in the reply.

## Step 2: Check platform bot-visibility BEFORE recommending config

This is the step that gets skipped, and skipping it produces a confident,
well-formatted config recommendation for a topology the platform forbids.

On several platforms, **bots do not receive messages authored by other bots** —
a Bot-API-level restriction, independent of any agent framework. Where that
holds, no privacy setting, admin promotion, or allowlist makes agent B see agent
A's message, because the event is never delivered.

Verify per platform rather than assuming, and check both directions:

1. Does the platform deliver bot-authored messages to other bots at all?
2. If yes, does the agent framework gate them separately?

If (1) is no, say so immediately and pivot to a workable topology. Leading with
config keys for an impossible topology wastes the user's time and reads as not
having checked.

### Workflow correction worth remembering

One session read a docs block labelled "recommended group config", led with
`require_mention: true`, and only afterwards discovered the user wanted the
agents to *observe each other* — which that platform blocks outright. The
docs' "recommended" block answers the *documented* question, not necessarily
the user's. **Establish feasibility first, then quote config.**

## Step 3: Hermes-specific wiring

### One token, one gateway, one profile — per agent

Each agent needs its **own bot token** and its **own gateway process**. Reusing
one token across two running gateways is rejected by the platform (concurrent
polling on the same token).

```bash
hermes -p <profile> setup           # configure with the SECOND bot token
hermes -p <profile> gateway start
hermes -p <profile> gateway status
```

The default profile keeps running unchanged. Profiles live under
`~/.hermes/profiles/<name>/` with their own `config.yaml`, skills, cron, and
memories.

### The config surface (messaging platforms, `telegram:` shown)

| key | effect |
|---|---|
| `require_mention` | agent only responds when `@`-mentioned, replied to, or matching `mention_patterns`. **Leave unset/false when the user wants both agents answering ordinary messages.** |
| `exclusive_bot_mentions` | when a message names specific bot usernames, only those profiles process it. Keeps routing deterministic with several agents present. Default on. |
| `mention_patterns` | regex wake words; set `[]` to disable shared wake words that would wake every agent |
| `observe_unmentioned_group_messages` | append unmentioned channel messages to the shared session transcript as **context**, without dispatching the agent |
| `group_allowed_chats` | authorises the shared group session used for observed context |
| `allowed_chats` | gates where the agent *responds* |
| `ignored_threads` | stay silent in specific forum topics |
| `<PLATFORM>_ALLOW_BOTS` | `none` (default) / `mentions` / `all` — accept inbound messages from other bots, where the platform delivers them at all |

`observe_unmentioned_group_messages` + `group_allowed_chats` is the
"reads everything, speaks only when addressed" mode. Use the **same chat IDs**
for both keys or observed context is silently dropped. Observed lines are tagged
and carry a per-turn safety prompt so the model treats them as context rather
than instructions addressed to it.

The human allowlist (`<PLATFORM>_ALLOWED_USERS`) still applies inside group
chats. Set it for **every** profile, not just the first.

### Platform join-time caching gotcha

Some platforms cache a bot's privacy/permission state **at the moment it joins a
channel**. Changing the setting afterwards does nothing until the bot is
**removed and re-added**. Always state this explicitly when giving setup steps —
it is the single most common reason a correctly-configured bot appears dead.
Promoting the bot to channel admin is usually the alternative that sidesteps it.

## Step 4: The ack-loop hazard — read before enabling agent-to-agent

Wiring two auto-replying agents to accept each other's messages is an
**unsupported topology** in Hermes, and the docs say so in as many words:

> `<PLATFORM>_ALLOW_BOTS` exists to accept input from a specific trusted bot
> (e.g. a relay or webhook bot), **not to let two Hermes profiles talk to each
> other** ... two bots will satisfy each other's mention gate indefinitely and
> ack-loop. **There is no circuit breaker for this.**

Platforms that auto-mention the replied-to author make this worse: every reply
re-satisfies the other agent's mention gate, forever.

`ALLOW_BOTS` is for narrowly-scoped trusted automation (a relay, a webhook
poster), never for another autonomous replier. If you build agent-to-agent
anyway, an explicit **turn cap** (e.g. stop after N exchanges) is mandatory and
is your responsibility — nothing upstream provides one.

## Step 5: Recommend by feasibility, cheapest first

Present options ordered by what actually works, with effort stated:

1. **Parallel advisors** — leave `require_mention` off so both agents answer the
   human; they simply do not see each other. Works today, minutes of setup. The
   human bridges by quoting or forwarding. Covers most of the practical value.
2. **Relay for genuine shared context** — a small service reads the channel and
   re-injects each agent's output to the other **as human-authored input** via
   the gateway API, which sidesteps bot-visibility restrictions entirely because
   the message arrives on the human path. Requires building, requires a turn cap.
   Do not present this as tested unless you have actually run it.
3. **Switch platforms** — where bots *can* see each other, the visibility problem
   disappears but the ack-loop hazard remains and still needs a breaker.

## Step 6: Size the host before promising a second agent

A second agent is a second full gateway process, not a thread. On small VMs this
is the binding constraint, so check it rather than letting the user discover it:

- RAM is the usual wall. A gateway paging into swap stalls in ways that look
  like a logic bug. On ~1GB hosts, configure swap and `gateway.scale_to_zero`
  from the start.
- Small disks fill with sessions, logs, and caches.
- Flag this proactively when the user names a small instance. The
  `cloud-vm-maintenance` skill covers the cleanup pass.

## Reporting this class of answer

Lead with the **blocker or the feasibility verdict**, not the setup steps. If the
requested topology is impossible, say that in the first line and give the closest
workable alternative immediately — a user following config instructions toward an
impossible end state is the worst outcome.

Quote the upstream warning verbatim when recommending against something; "the
docs explicitly call this unsupported and note there is no circuit breaker"
carries the point far better than a paraphrase.

Set expectations about what the working setup will *not* do (e.g. "they will not
spontaneously converse; you are the router") rather than letting the user find
out after building it.

## Verifying against a local install

When platform docs are unreachable, the installed tree is authoritative and
often better than published docs:

- `~/.hermes/hermes-agent/website/docs/user-guide/messaging/<platform>.md`
- `~/.hermes/hermes-agent/website/docs/reference/environment-variables.md`
- Gate implementations: search the code for the env var name, e.g.
  `<PLATFORM>_ALLOW_BOTS`, to see exactly where and how it is enforced
- Tests encode the real contract when docs are ambiguous:
  `tests/gateway/test_*_group_gating.py`

Prefer reading the enforcement site over the prose. One session confirmed the
exact `none|mentions|all` semantics from the authorization mixin after the docs
index came back empty.
