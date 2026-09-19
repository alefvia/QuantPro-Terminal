from dataclasses import dataclass

@dataclass(frozen=True)
class SessionLevels:
    high: float
    low: float
    midpoint: float

def levels(highs: list[float], lows: list[float]) -> SessionLevels:
    if not highs or not lows:
        raise ValueError("highs/lows required")
    high=max(highs)
    low=min(lows)
    return SessionLevels(high=high, low=low, midpoint=(high+low)/2)
