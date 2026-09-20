# Remaining stages 1-3 completion

## Stage 1 — Order Flow
Implemented footprint rows, cumulative delta (existing), stacked imbalance, liquidity additions/pulls/persistence, and price-response confirmation primitives for absorption/exhaustion.

Stacked imbalance now requires consecutive **tick-adjacent** price levels. The footprint accepts an explicit instrument tick size so a gap in observed prices cannot be misclassified as a stack.

## Stage 2 — real market data path
QuantPro has a zero-market-data-cost research profile for Sierra Chart Delayed Exchange Data Feed. The profile is deliberately marked non-realtime and cannot pass the live gate.

The protected provider-neutral bridge remains the integration boundary for an authorized external feed. Rithmic and other licensed providers can be added behind this boundary without changing the decision/risk contracts. External account/API approval is still required before actual exchange packets can enter QuantPro. No credentials are stored.

## Stage 3 — Brazil evening / CME reopen session
The research window is anchored to the CME Globex 17:00 America/Chicago reopen and converted with IANA time zones to America/Sao_Paulo. This makes the Brazil-local start automatically follow US daylight-saving changes (commonly 19:00 BRT during Chicago daylight time and 20:00 BRT during Chicago standard time).

Per-symbol summaries cover volume, absolute delta, depth imbalance, range and spread. This supports NQ/MNQ vs GC/MGC evidence collection without declaring a winner in advance.

No profitability claim. No live trading.
