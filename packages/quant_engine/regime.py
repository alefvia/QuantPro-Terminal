from dataclasses import dataclass
from enum import Enum

class Regime(str, Enum):
    TREND_UP="TREND_UP"
    TREND_DOWN="TREND_DOWN"
    RANGE="RANGE"
    BREAKOUT="BREAKOUT"
    HIGH_VOL="HIGH_VOL"
    EVENT="EVENT"
    UNKNOWN="UNKNOWN"

@dataclass(frozen=True)
class RegimeState:
    regime: Regime
    confidence_score: float
    reason: str

def detect_regime(*, trend: str, atr_ratio: float | None, range_pos: float | None, event_blocked: bool) -> RegimeState:
    if event_blocked:
        return RegimeState(Regime.EVENT, 1.0, "high-impact event window")
    if atr_ratio is None:
        return RegimeState(Regime.UNKNOWN, 0.0, "insufficient volatility history")
    if atr_ratio >= 1.6:
        return RegimeState(Regime.HIGH_VOL, min(1.0, atr_ratio/2.5), "ATR expansion")
    if range_pos is not None and (range_pos > 1.0 or range_pos < 0.0):
        return RegimeState(Regime.BREAKOUT, 0.75, "price outside reference range")
    if trend == "UP":
        return RegimeState(Regime.TREND_UP, 0.65, "fast structure above slow")
    if trend == "DOWN":
        return RegimeState(Regime.TREND_DOWN, 0.65, "fast structure below slow")
    return RegimeState(Regime.RANGE, 0.55, "no directional trend")
