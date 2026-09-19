from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Bar:
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass(frozen=True)
class MarketSnapshot:
    last: float
    vwap: float | None
    atr: float | None
    realized_vol: float | None
    trend: str
    range_position: float | None

def true_range(current: Bar, previous_close: float) -> float:
    return max(current.high-current.low, abs(current.high-previous_close), abs(current.low-previous_close))

def atr(bars: list[Bar], period: int = 14) -> float | None:
    if len(bars) < period + 1:
        return None
    trs=[true_range(bars[i], bars[i-1].close) for i in range(len(bars)-period, len(bars))]
    return sum(trs)/period

def realized_vol(closes: list[float], annualization: float = 252.0) -> float | None:
    if len(closes) < 3 or any(x <= 0 for x in closes):
        return None
    returns=[math.log(closes[i]/closes[i-1]) for i in range(1,len(closes))]
    mean=sum(returns)/len(returns)
    variance=sum((x-mean)**2 for x in returns)/(len(returns)-1)
    return math.sqrt(variance)*math.sqrt(annualization)

def session_vwap(prices: list[float], volumes: list[float]) -> float | None:
    if len(prices) != len(volumes) or not prices:
        raise ValueError("prices and volumes must have equal non-zero length")
    total=sum(volumes)
    if total <= 0:
        return None
    return sum(p*v for p,v in zip(prices,volumes,strict=True))/total

def range_position(last: float, low: float, high: float) -> float | None:
    if high <= low:
        return None
    return (last-low)/(high-low)

def simple_trend(closes: list[float], fast: int = 8, slow: int = 21) -> str:
    if len(closes) < slow:
        return "UNKNOWN"
    f=sum(closes[-fast:])/fast
    s=sum(closes[-slow:])/slow
    threshold=abs(s)*0.0005
    if f-s > threshold:
        return "UP"
    if s-f > threshold:
        return "DOWN"
    return "FLAT"
