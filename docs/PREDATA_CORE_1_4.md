# Pre-data core — blocks 1–4

This phase prepares research logic before a licensed real-time futures feed is connected.

## 1. Order Flow hardening
PR #16 made the CME evening window DST-aware and stacked imbalance tick-adjacent. This phase adds a stricter response primitive that combines executed volume, side imbalance and limited adverse price response. It remains a research heuristic, not proof of institutional absorption or exhaustion.

Depth reductions are not labelled as cancellations unless the eventual feed explicitly distinguishes cancel/modify from execution. MBP-only data must remain conservative.

## 2. Macro Engine V2 foundation
Macro events now support actual, consensus, previous and surprise. Event risk is separated from directional forecasting. High-impact events can reduce or veto new risk around the release window. Macro context weight is dynamic and bounded rather than permanently fixed.

Future real-data work will align releases point-in-time and measure rates, dollar, volatility and NQ/Gold reaction after releases.

## 3. Discovery Engine foundation
The discovery module enumerates controlled binary feature combinations, requires a minimum number of occurrences, reports search-space size and exposes multiple-testing correction. Every result is a hypothesis only.

No discovered pattern may become a trading signal without temporal out-of-sample validation, walk-forward stability, realistic costs/slippage and paper evidence.

## 4. Candidate setup catalog
Initial hypotheses: trend continuation, VWAP reclaim, absorption reversal, liquidity breakout and exhaustion reversal. These are named research templates, not profitable strategies.

## Safety / truth
No real-time market feed is connected.
No calibrated probability exists.
No profitability or win-rate claim is made.
Live execution remains blocked.
