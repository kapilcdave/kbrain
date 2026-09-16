# Kalshi venue notes (verified against the live API, 2026-09)

Base: `https://api.elections.kalshi.com/trade-api/v2`. Public read endpoints need
no auth; portfolio endpoints need RSA-PSS request signing.

## Auth

Credentials live outside the repo. Loader searches `KALSHI_ENV_FILE`, then
`./.env`, then a credential search path:

```bash
export KALSHI_ENV_FILE=$HOME/.config/trading/keys.env   # KALSHI_API_KEY_ID + KALSHI_PRIVATE_KEY_PATH
```

Signing: `base64(RSA_PSS_SHA256(timestamp_ms + METHOD + "/trade-api/v2" + path))`,
sent as `KALSHI-ACCESS-KEY` / `-TIMESTAMP` / `-SIGNATURE`. Sign the **full** path
including the `/trade-api/v2` prefix; sign the path without the query string.

A private key that is group/world readable is rejected by the loader — `chmod 600`.

## Fixed-point decimal STRINGS everywhere

Price/size fields are decimal strings under `*_dollars` / `*_fp` names:
`yes_bid_dollars: "0.8400"`, `yes_bid_size_fp: "3956.36"`. Reading the bare key
(`volume`, `yes_bid`) returns `None` **silently**. `_fp` means "decimal", not
"scaled integer" — 1 unit is 1 contract.

But `revenue` and `value` on settlements are integer **cents**. Mixed units in
one payload; normalise explicitly.

## The orderbook endpoint disagrees with the market touch — use the market payload

`/markets/{ticker}/orderbook` returns:

```json
{"orderbook_fp": {"yes_dollars": [["0.0010","177549.30"], ...],
                  "no_dollars":  [["0.0010","60730.99"],  ...]}}
```

- Keys are `yes_dollars` / `no_dollars`, **not** `yes` / `no`. Wrong key → `None`
  for every level, silently.
- Levels are `[price, size]` **ascending**, so the touch is the **LAST** row.
- A NO bid at `n` is a YES offer at `1-n`.
- `?depth=N` truncates the **cheap** end, not the touch. `depth=200`+ can return
  empty.
- **Even read correctly it disagrees with the market payload's own touch.**
  Bracketing the orderbook call between two `/markets/{ticker}` calls put the book
  inside the bracket only **8 of 18 times**, one-sided. One sample showed a best
  YES bid of 0.65 against a reported ask of 0.59 — a crossed book, i.e. a stale
  snapshot.

**Use `/markets?series_ticker=...` instead.** It carries `yes_bid_dollars` with
`yes_bid_size_fp` (and the ask pair), so price and queue depth come from **one
self-consistent object in one call**. Only fall back to the ladder when you need
depth beyond the touch, and treat it as indicative.

## Fees round UP to the cent — apply before believing any edge

```
taker fee = ceil(0.07 * C * P * (1-P) * 100) / 100     # maker = 0
```

The ceiling makes it **1.00c per contract at every price in 0.88-0.97**. Against
a 2.46c gross edge that is 40%. A "2.5c edge" crossing the spread is really
~1.5c. Compute fees per contract at the actual entry price, not as a percentage.

## Market structure

- **Only ONE market per 15M series is open at a time**, cycling 900s → 0s. There
  is no ladder of concurrent expiries. A collector started mid-window sees each
  market for the first time at an arbitrary point in its life — so any filter that
  needs price *history* cannot judge those, and must record
  "history unknown" rather than treating them as clean.
- Crypto 15M settles off a ~60s average of a CF benchmark, so `result` is not
  populated the instant the market closes. Wait ~90s before asking.
- Co-expiring crypto legs settle off one benchmark and agree ~99.3% of the time:
  nine legs on one boundary are **~one draw**, not nine. Only other factors
  (metals, energy) and more days add independent clusters.
- **~26 `*15M` series are listed, but they are ~5 factors, not 26.** Group them
  before claiming independent replication:

  | factor | series |
  |---|---|
  | crypto | BTC ETH SOL XRP DOGE HYPE BNB NEAR ZEC ADA BCH TON, CRYPTOCOMP/CRYPTOLEAD |
  | metals | GOLD SILVER COPPER PLATINUM PALLADIUM |
  | energy | WTI NATGAS |
  | fx | EURUSD GBPUSD USDJPY |
  | equity | INX NDQ (market hours only) |

  Adding ETH to BTC buys almost no independence; adding GOLD or WTI does.
- **Listed does not mean traded.** Several series settle nothing over a 180-day
  window (observed: ADA, BCH, and the whole FX and equity set). Enumerate from
  `/series?category=...` but verify settled-market counts before planning around
  a series — the genuinely independent factors are often the empty ones.
- Discovery: `/series?category=<Crypto|Commodities|Financials|...>`, filter
  tickers ending `15M`.
- Exchange is **sharded** (0 Default, 1 Combos, 2 Crypto, 3 Tennis/Baseball) and
  **each shard has its own balance**. `/portfolio/balance` returns a
  `balance_breakdown` per shard; the exchange-wide total can look fine while the
  shard you trade is empty.
- A quote at 0.999/1.000 is not a tradeable wing. Cap entry (e.g. `MAX_ENTRY =
  0.99`) or qualification rates are wildly overstated.

## Confirming an account is flat

```
GET /portfolio/orders?status=resting     -> cancel each via DELETE /portfolio/orders/{id}
GET /portfolio/positions                 -> check position_fp != 0
GET /portfolio/balance                   -> balance_dollars, portfolio_value
```

A dead local process does **not** mean no exposure: resting orders survive it.
Check the venue, not just `ps`.

## Rate limits

Candlestick fan-out 429s readily. Two concurrent sweeps took one collection from
350s to 5,651s. Run one at a time; back off 1.5s x attempt.
