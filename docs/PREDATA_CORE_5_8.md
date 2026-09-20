# Pre-data core — blocks 5–8

## 5. Advanced validation
Adds explicit transaction-cost/slippage sensitivity, MAE/MFE summaries, regime stability and purged/embargoed expanding temporal folds. This is infrastructure; no edge is claimed.

## 6. Market Reaction Engine
Adds a point-in-time event reaction contract for surprise, NQ, Gold, 2Y/10Y yields, dollar and CVD. The assessment is descriptive and fails closed when evidence is incomplete. Future data ingestion will define exact event windows and normalization.

## 7. Provider adapter boundary
Adds provider-neutral adapter contracts plus fail-closed Rithmic and IBKR placeholders. They intentionally do not invent undocumented vendor protocol fields and cannot connect until authorized credentials, official protocol details and market-data rights are available.

## 8. Terminal V3 preparation
The web terminal now exposes the research pipeline layers: Discovery, Validation, Macro Reaction and Feed Adapter readiness. Market prices remain blank while offline; live execution remains locked.

## Required evidence before promotion
- Licensed/authorized feed and point-in-time historical data.
- OOS + walk-forward evidence with realistic costs.
- Sufficient paper sample.
- Calibrated probability only after held-out evidence.
- Explicit live authorization and independent risk gate.
