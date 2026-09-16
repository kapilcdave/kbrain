# Weather Markets: Settlement Gauge and Release Timing

Kalshi temperature/precipitation markets. Both obvious theses here were tested
against live data and **both are dead**. This file records the measured result
and the method, so the same trade is not rediscovered.

**Headline: there is no tradeable latency edge, and a forecast-vs-market model
built on any public weather API is sign-flipped by the settlement gauge.**

## 1. The settlement gauge is not NWS METAR

These markets settle on **The Weather Company's CLI value** for the named site
(`rules_primary` says so explicitly, e.g. "Austin (CLIAUS) ... according to The
Weather Company"). They do **not** settle on the raw NWS METAR series, and not on
any forecast API.

This is not recoverable by guessing. Fit it instead: settled markets expose the
exact settled number as `expiration_value`.

```
GET /markets?series_ticker=KXLOWTAUS&status=settled&limit=200
  -> market['expiration_value']   # e.g. "76.00" — the number that settled
  -> market['result']             # 'yes' | 'no'
```

Scoring candidate (station, window, rounding) combinations against that value
for Austin overnight minima: **0/6 exact on every candidate window**. The CLI
value is not reproducible from METAR at all.

But the miss is **systematic**, which is the usable part:

| date | Kalshi settled | KATT METAR min | delta |
|---|---|---|---|
| d1 | 78.00 | 80.06 | +2.06 |
| d2 | 73.00 | 77.00 | +4.00 |
| d3 | 77.00 | 78.08 | +1.08 |
| d4 | 73.00 | 77.00 | +4.00 |
| d5 | 73.00 | 78.08 | +5.08 |
| d6 | 76.00 | 78.98 | +2.98 |

**6/6 positive, mean +3.20 °F, stdev 1.33 °F.** METAR reads WARM vs settlement.

Why that destroys a naive model: the bias is **3.2x the 1 °F strike spacing**,
and its dispersion alone spans ~1.3 buckets. Applying the correction flipped one
apparent +0.503/contract trade to **-0.144**. Window choice does not rescue it —
`cal_local`, `lst_day`, `utc_day`, `prev_eve` all yield identical overnight
extrema because the minimum falls in the pre-dawn hours all four share.

**Rule: fit on `expiration_value`. Never on METAR, never on a forecast API.**
n=6 is enough to kill a trade and nowhere near enough to support one; a real
model needs months of `expiration_value` history per city.

## 2. Release-linked repricing is REAL and NOT harvestable

The timing hypothesis is testable retrospectively because model releases are
**scheduled**: HRRR runs hourly at :00Z and publishes ~:50-:58Z.

Kalshi exposes 1-minute bid/ask history on settled markets:

```
GET /series/{series}/markets/{ticker}/candlesticks
    ?start_ts=<unix>&end_ts=<unix>&period_interval=1
  -> candlesticks[].end_period_ts
  -> candlesticks[].yes_bid.close_dollars / yes_ask.close_dollars
  -> candlesticks[].volume_fp
```

112 settled markets across 8 cities yielded **82,933 consecutive-minute pairs**
in minutes of wall time — vastly more power than waiting for live releases.

**Result: clustering is real.** Mean `|d mid|` by minute-of-hour, baseline
0.857c/min, elevated at :56-:04 exactly where HRRR publishes:

| window | ratio | z | p |
|---|---|---|---|
| 55-04 (10m) | 1.132 | +7.56 | 2e-14 |
| 00-04 (5m) | 1.177 | +6.01 | 9.5e-10 |
| 58-02 (5m) | 1.121 | +4.34 | 7.2e-06 |
| 50-05 (16m) | 1.069 | +5.29 | 6.1e-08 |
| 50-59 (10m) | 1.012 | +1.64 | n.s. |

The window that FAILS is informative: `:50-:59` covers publication but misses
`:00-:04` where the excess actually sits. The effect is tight and **late** —
quotes reacting after data lands, not anticipating it.

**But it is not harvestable from either side:**

*Taker.* `|d mid|` is unsigned. Signed continuation after each release-window
move was **negative at 4/4 horizons** and statistically indistinguishable from
non-window control (p=0.30-0.87). The move mean-reverts — quote flicker, not
sustained repricing. Against a ~4c spread + ~2c fee hurdle: **-6.1c/contract**.

*Maker.* Spreads genuinely widen in the window (4.216c vs 3.727c, +13.1%,
t=+9.20, p=3e-20) and volume rises (+36%). But the round trip is negative at
every horizon:

| horizon | earn | drift | exit | realised |
|---|---|---|---|---|
| t+1 | 2.166c | 1.503c | 2.010c | **-1.347c** |
| t+3 | 2.103c | 2.746c | 1.868c | -2.511c |
| t+5 | 2.086c | 3.545c | 1.836c | -3.294c |

And **88% of the gross maker edge exists in ordinary minutes** — the
release-specific increment is only 12%. Even had it worked, the weather-release
thesis adds almost nothing over generic market-making.

The makers are already pricing the event correctly: they widen 13%, and that
widening is almost exactly compensation for the extra drift they absorb. That is
what an efficiently-priced scheduled event looks like.

## 3. Market structure facts worth keeping

Series: `KXHIGHT{LOC}` (daily high), `KXLOWT{LOC}` (daily low), `KXTEMP*`
(hourly directional), `KXRAIN*` / `RAIN*` (precipitation, thin).

Ticker shape: `KXLOWTAUS-26SEP11-T77`. Discover real series via
`GET /series?limit=500` and filter on ticker prefix — do **not** keyword-match
titles, which pulls in NFL/NCAA markets on city names.

**Strikes are a mutually exclusive LADDER**, not isolated thresholds:
`floor_strike=77` + `yes_sub_title="78 or above"` is one rung of six. Price a rung
against the whole ladder normalised for overround. That normalisation is what
exposed the gauge bias: the market put 30.5% on a bucket that was "impossible"
under the METAR floor, which was the tell that the gauge assumption was wrong.

Typical liquidity is thin — ~$500/day notional per ladder, 4-10c spreads.

## 4. Method notes for retrospective timing tests

These generalise to any scheduled-release timing question:

- **Quote hygiene.** Keep only two-sided sane quotes (`ask > bid`, `0 < bid`,
  `ask < 1`). A 0/1 quote is an empty book; counting it manufactures huge fake
  moves when a market wakes up.
- **Strictly consecutive minutes only** (`ts diff == 60`). A gap means the book
  was empty between, so the change is not attributable to one minute.
- **Null = within-market-hour exchangeability**, not "flat across the hour". Each
  market has its own hour-of-day activity profile that would otherwise fake or
  mask the effect.
- **Closed-form permutation moments** beat brute force: per block,
  `E = k*mean`, `Var = k(n-k)/(n-1)*popvar`, summed over independent blocks.
  Pure-Python shuffling over thousands of blocks does not finish. Validate the
  closed form against ~1500 real shuffles before trusting the p-value (agreement
  was 0.03% on the mean, 1% on the sd).
- **Report every window tried** with a Bonferroni threshold. The same effect read
  1.012 (n.s.) or 1.177 (p=9e-10) depending on window choice.
- **Cache the fetch separately from the inference.** Kalshi 429s under sustained
  candlestick polling; sleep ~1.2s between calls with backoff. Cache *every*
  field you might need — a mid-only cache had to be refetched entirely to test
  spread and volume.

## 5. Why this venue is structurally hard

A Kalshi contract lives on [0,1], so costs are a percentage of the **whole
instrument**: ~4c spread + up to 1.75c fee is **~6% of notional** round trip.
SPY is ~0.01%. That is a ~600x difference in the edge required to break even.

The release-timing effect was real, statistically overwhelming, and worth ~0.2c
against a 6c hurdle — a good signal in the wrong venue. Before investing in any
signal here, check that its plausible size can clear ~6% of notional.
