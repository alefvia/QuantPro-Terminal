from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

BRAZIL = ZoneInfo("America/Sao_Paulo")
CHICAGO = ZoneInfo("America/Chicago")


@dataclass(frozen=True)
class NightObservation:
    symbol: str
    ts: datetime
    volume: float
    abs_delta: float
    abs_depth_imbalance: float
    range_points: float
    spread_ticks: float


def cme_reopen_brazil(ts: datetime) -> datetime:
    """Return the 17:00 Chicago Globex reopen expressed in Sao Paulo time."""
    if ts.tzinfo is None:
        raise ValueError("timezone-aware timestamp required")
    chicago_date = ts.astimezone(CHICAGO).date()
    reopen_chicago = datetime.combine(
        chicago_date,
        time(17, 0),
        tzinfo=CHICAGO,
    )
    return reopen_chicago.astimezone(BRAZIL)


def eligible(o: NightObservation, window_hours: int = 3) -> bool:
    if o.ts.tzinfo is None:
        raise ValueError("timezone-aware timestamp required")
    if window_hours < 1:
        raise ValueError("window_hours must be positive")
    local = o.ts.astimezone(BRAZIL)
    reopen = cme_reopen_brazil(o.ts)
    elapsed = (local - reopen).total_seconds()
    return 0 <= elapsed < window_hours * 3600


def summarize(items: list[NightObservation]) -> dict[str, dict[str, float]]:
    groups = {}
    for o in items:
        if not eligible(o):
            continue
        g = groups.setdefault(o.symbol, [])
        g.append(o)
    result = {}
    for symbol, rows in groups.items():
        n = len(rows)
        result[symbol] = {
            "observations": float(n),
            "avg_volume": sum(x.volume for x in rows) / n,
            "avg_abs_delta": sum(x.abs_delta for x in rows) / n,
            "avg_depth_imbalance": sum(x.abs_depth_imbalance for x in rows) / n,
            "avg_range_points": sum(x.range_points for x in rows) / n,
            "avg_spread_ticks": sum(x.spread_ticks for x in rows) / n,
        }
    return result
