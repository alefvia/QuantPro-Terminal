# F5–F7 Intelligence Layer

## F5 External intelligence
Implemented:
- macro snapshots for US 2Y/10Y, real yield, VIX and dollar
- NQ/Gold contextual transforms
- rolling intermarket correlation/beta
- COT positioning primitives: net, weekly change, percentile
- high-impact event blocking

These are evidence transforms, not universal causal claims. Signs/weights must be validated by regime and out-of-sample data.

## F6 Regime
Baseline regime detector:
TREND_UP, TREND_DOWN, RANGE, BREAKOUT, HIGH_VOL, EVENT, UNKNOWN.
Event risk has priority. Regime confidence is a score, not a calibrated probability.

## F7 Quant/ML foundation
- normalized feature vector
- transparent weighted baseline benchmark
- temporal train/validation/test split
- ensemble disagreement -> WAIT
- probability field remains None until calibration exists

Complex ML must beat the simple baseline out-of-sample after costs before promotion.
