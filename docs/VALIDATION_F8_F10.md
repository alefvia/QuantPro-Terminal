# F8–F10 Validation / Replay / Decision + AI

## F8 Backtest and walk-forward
Backtest metrics include trade count, win rate, expectancy, profit factor, maximum drawdown and Sharpe. Fees and slippage are deducted per trade. Expanding walk-forward keeps training strictly before each test window.

This is infrastructure, not evidence that a strategy is profitable. A strategy must later be tested on real point-in-time datasets.

## F9 Replay and journal
Replay orders events by available_at and only exposes the accumulated information known at that point. Decision logs are append-only JSONL. Journal schema records score, regime, stop/target, MAE/MFE and PnL.

## F10 Decision + AI Analyst
TradeThesis produces LONG/SHORT/WAIT from supplied evidence and risk approval. Event risk or risk veto forces WAIT. AI Analyst converts structured evidence into explanations; it does not create market facts. Probability remains None / NÃO CALIBRADA until a real calibration pipeline is validated.
