# Remaining stages 1-3 completion

## Stage 1 — Order Flow
Implemented footprint rows, cumulative delta (existing), stacked imbalance, liquidity additions/pulls/persistence, and price-response confirmation primitives for absorption/exhaustion.

## Stage 2 — real market data path
QuantPro now has a concrete zero-market-data-cost research profile for Sierra Chart Delayed Exchange Data Feed. Official Sierra documentation states CME/COMEX delayed streaming is 10 minutes 10 seconds and includes market depth; MBO is available where supported. This profile is deliberately marked non-realtime and cannot pass the live gate.

External installation/account setup is still required before actual exchange packets can enter QuantPro. No credentials are stored.

## Stage 3 — 19:00-22:00 Brazil session
Implemented timezone-aware observations and per-symbol summaries for volume, absolute delta, depth imbalance, range and spread. This supports NQ/MNQ vs GC/MGC evidence collection without declaring a winner in advance.

No profitability claim. No live trading.
