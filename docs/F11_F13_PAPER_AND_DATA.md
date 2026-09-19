# F11–F13 Risk, Paper and Advanced Data

## F11 Risk Engine advanced
Independent gates now cover kill switch, data quality, event risk, max daily loss, max drawdown, consecutive losses, minimum R:R and per-position risk sizing. Approval is explicitly PAPER, not live.

## F12 Paper Trading
Market-order simulator applies adverse slippage and fees. Portfolio tracks position, average price, realized PnL and fees. Paper-validation gate requires a minimum sample, positive expectancy, minimum profit factor and drawdown within limits. Thresholds are research policy defaults, not promises of profitability.

## F13 Advanced data readiness
A provider-neutral futures interface and capability gate were added. Intraday use requires confirmed licensing, real-time mode and trades. Contracts for market depth and individual order events are ready for Level 2/MBO providers.

No vendor has been hard-coded and no delayed/free feed is mislabeled as real-time. Provider selection must verify current pricing, entitlements and API/licensing terms before credentials are added.
