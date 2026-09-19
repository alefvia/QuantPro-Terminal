# Data Catalog — F1/F2

## Macro/intermarket (FRED)
Initial canonical series:
- DGS2 — US 2Y Treasury
- DGS10 — US 10Y Treasury
- DFII10 — US 10Y real yield
- VIXCLS — VIX
- DTWEXBGS — broad dollar index
- DFF — effective fed funds
- CPIAUCSL / CPILFESL — CPI/core CPI
- PCEPI / PCEPILFE — PCE/core PCE
- UNRATE — unemployment
- PAYEMS — nonfarm payrolls

FRED v1 requires an API key. The key is never committed.

## Positioning (CFTC)
COT adapter is prepared for CFTC public-data/Socrata endpoints. Dataset endpoint is configuration because report families have different schemas and CFTC can evolve them.

Initial market codes:
- Nasdaq-100: 209742
- Gold: 088691

## Futures price
NQ/MNQ/GC/MGC exchange-quality real-time futures data is intentionally NOT fabricated in F1/F2. A legal/provider-specific adapter will be selected later. Delayed/free data may be used for UI development, never represented as real-time.

## Point-in-time rule
Every canonical record has:
- observed_at — period/market timestamp
- available_at — timestamp at which the system can prove it had the information
- source
- series
- value

Backtests filter on available_at to prevent future knowledge.
