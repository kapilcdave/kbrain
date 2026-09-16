# Measuring latency to hosted / trading APIs

Goal: answer "how fast are we, and would relocating the VM help?" Separate the
three layers — network RTT (geography, fixable by moving), TLS handshake, and
server/platform processing (NOT fixable by moving).

## curl timing breakdown (the core probe)
```
FMT='  DNS:%{time_namelookup} TCP:%{time_connect} TLS:%{time_appconnect} TTFB:%{time_starttransfer} total:%{time_total} ip:%{remote_ip}\n'
curl -o /dev/null -s -w "$FMT" --connect-timeout 5 "https://api.example.com/health"
```
Interpretation:
- `time_connect - time_namelookup` = **TCP round-trip = the network floor.** This
  is what co-location changes.
- `time_appconnect - time_connect` = TLS handshake (~1 extra RTT).
- `time_starttransfer - time_appconnect` = **server-side processing.** If TTFB is
  huge but TCP connect is tiny, the latency is the platform's backend, not the
  network — relocating won't help.

Run 5 warm samples and take avg + best; first request pays DNS + cold cache:
```
for i in 1 2 3 4 5; do curl -o /dev/null -s -w "%{time_connect} %{time_appconnect} %{time_starttransfer}\n" \
  --connect-timeout 5 "https://host/"; done | awk '{c+=$1;n++} END{printf "TCP avg %.0fms\n", c/n*1000}'
```
`ping -c 4 -q <host>` gives the raw ICMP RTT with no TLS — but many trading hosts
(Kalshi) block ICMP; Cloudflare-fronted ones (Polymarket) answer.

## Map an API's IP to its AWS region (decides where to co-locate)
```
curl -s https://ip-ranges.amazonaws.com/ip-ranges.json | python3 -c "
import json,sys,ipaddress
d=json.load(sys.stdin); t=sys.argv[1]; ipa=ipaddress.ip_address(t)
for p in d['prefixes']:
    if ipa in ipaddress.ip_network(p['ip_prefix']):
        print(t, p['region'], p['service']); break" <IP>
```

## Findings from a real GCP us-central1 (Iowa) VM (2026-09)
- **Kalshi** `trading-api.kalshi.com` origin is **AWS us-east-2 (Ohio)**. From
  GCP Iowa the TCP RTT was ~23ms best / ~36ms avg. Co-locating the VM in **AWS
  us-east-2** drops that to low single-digit ms (often 1-3ms) — a 5-10x win on
  the leg that matters for a fast 15-min up/down strategy. This is the single
  biggest latency lever. (`api.elections.kalshi.com` is CloudFront/global edge.)
- **Polymarket** (`clob.polymarket.com`, `gamma-api.polymarket.com`) sits behind
  **Cloudflare** (~11-13ms edge RTT already), but TTFB was ~220ms — that is
  Polymarket's own API + Polygon-chain settlement, NOT network. Relocating barely
  helps; you won't beat ~200ms end-to-end. Levers there: keep-alive connections
  to the CLOB API, and running your own low-latency Polygon RPC for on-chain
  settlement rather than a public endpoint.

## Honest framing for the user
Latency co-location improves *fill quality at the margins*. It does NOT fix a bad
max-drawdown — that's strategy/sizing/entry-timing. Say so; don't let a 20ms
network win masquerade as a P&L fix.
