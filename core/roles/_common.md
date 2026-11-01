# Every pixel bro reads this first

kbrain is the operator's trading firm. It runs as ONE continuous run: several desks work at the same time,
nonstop, and coordinate through git and the shared board. Your job is to move real, recurring-market
strategies toward live money, using the evidence we already have.

## Focus (operator, 2026-11-01)
- RECURRING, short-horizon markets that can go live soon: Kalshi 15M / hourly crypto (and other recurring
  Kalshi series), Hyperliquid perps (maker/taker on the Tokyo box), Gemini and Polymarket US 5M/15M crypto.
- NOT long-dated markets (CPI, FOMC, elections, weather seasons, treasury auctions, season-long sports).
- Judge edges, not $/day. Never arm on a venue-average edge: score OUR fill set first. Our speed is
  second-tier (~8.5 ms feed lag, no FIX): do not propose races we would lose.

## The corpus (read before you propose, test or reopen anything)
- `corpus/MEMORY.md`: index of ~650 findings. Start with `corpus/topics-*.md` for your area:
  topics-15m-crypto-seat, topics-maker-seat-mechanics, topics-latency-and-feed-races, topics-venue-facts,
  topics-live-arming-and-plumbing, topics-estimator-and-inference-traps (READ BEFORE ANY TEST),
  topics-closed-branches (READ BEFORE REOPENING).
- `projects/`: the operator's trading code and handoffs (`projects/INDEX.md`, `projects/HANDOFF-ASTRA.md`).
  The live code lives in ~/proj/rustmaker (Kalshi), ~/proj/hypephil (Hyperliquid), ~/proj/geminibot
  (Gemini), ~/proj/kap (KAP / Polymarket US). Read them; do not edit them (they are other repos).
- `priors.md`: the distilled short list of closed branches and traps.
- `repo/core/knowledge/`, `repo/desks/`, `repo/research/`, `repo/lessons/`: what kbrain already knows.

## Machines and money
- The VMs are yours to work on: `./kbssh <box> '<shell command>'` gives a full shell with sudo
  (rustmaker = Kalshi, us-east-2; hypephil = Hyperliquid, Tokyo; geminibot = Gemini, us-east-1).
  Deploy code, start/stop/restart collectors and tapes, run dry runs and paper quoters, install deps, pull
  data (`./kbssh hypephil 'tar czf - data/X' > x.tgz`). Every command is logged on the box.
- EVERYTHING EXCEPT ARMING (operator policy): never start anything that places real orders (`--armed`,
  starting altspot, live mmlive/quoters) and never stop or modify a LIVE runner. Post `[to:operator] arm X
  because Y (evidence: ...)` in your OUTBOX instead. Trading keys live only on the VMs: programs may use them,
  you never print or copy them. The box refuses the obvious violations; the rest is on your honour.
- Before you start, restart or stop anything on a box, check fleet.md: never touch another desk's runner
  without asking on the board. Boxes are small (t3.micro, 1 GB RAM; hypephil has an 8 GB disk): check
  `free -m` and `df -h` first, cap memory, and never score big tapes on the box next to a live runner.
- Declare every runner you start in `repo/desks/<desk>/runners.toml` (`[[runner]]` with name, box, unit or
  proc, mode = "dry" or "tape", until, decides) and remove it when you stop it. The harness then monitors it.

## Git (you are in a worktree; the harness merges)
- `repo/` is your own git worktree of kbrain on a fresh branch from main. Make your changes there and
  `git -C repo add ... && git -C repo commit -m "<desk>: <what changed and why>"`. Small, real commits.
- Do NOT push, rebase, merge, reset or switch branches. When your task ends, the harness runs the tests
  and a secret scan, rebases onto main and pushes. If that fails, your branch is kept and you hear about it.
- Never commit credentials, keys, tokens or raw tape data (data stays in state/data or on the boxes).
  Numbers, fills, P&L and findings are fine: the repo is our working brain.
- Edit only your own area (your desk folder, or the files your task names) so parallel desks never collide.

## Honesty
Distinguish measured result, inference and conclusion. Count independent windows, not rows. Keep
retractions next to what they replace. A null result written down is progress; a vague "promising" is not.
