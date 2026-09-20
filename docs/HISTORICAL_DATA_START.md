# Historical data start — Databento

Initial research path: Databento Historical CME Globex MDP 3.0, usage-based, no live subscription required.

Target continuous front-month products:
- NQ.v.0
- MNQ.v.0
- GC.v.0
- MGC.v.0

Default first schema: OHLCV 1 minute. This is intentionally cheaper/lighter than MBO and is enough to validate the ingestion -> replay -> feature -> backtest pipeline. Tick/order-book data is a later experiment.

## Secret
Set DATABENTO_API_KEY only in the runtime environment. Never commit it.

## First controlled download
Run:
python scripts/ingest_databento_history.py --start 2026-01-01T00:00:00+00:00 --end 2026-01-08T00:00:00+00:00

Start with one week. Verify cost/credit in the provider portal before expanding to months/years.

## Safety
The connector never fabricates data. Without the API key it fails closed. Historical data does not make the system Live eligible.
