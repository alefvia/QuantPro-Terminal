from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

BRAZIL=ZoneInfo("America/Sao_Paulo")

@dataclass(frozen=True)
class SessionStats:
    symbol: str
    observations: int
    total_volume: float
    absolute_delta: float
    average_depth_imbalance: float
    realized_range: float

def in_night_window(ts: datetime, start_hour: int=19, end_hour: int=22) -> bool:
    if ts.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    hour=ts.astimezone(BRAZIL).hour
    return start_hour <= hour < end_hour

def compare_key(stats: SessionStats) -> tuple[float,float,float]:
    if stats.observations <= 0:
        return (0.0,0.0,0.0)
    return (
        stats.total_volume / stats.observations,
        stats.absolute_delta / stats.observations,
        abs(stats.average_depth_imbalance),
    )
