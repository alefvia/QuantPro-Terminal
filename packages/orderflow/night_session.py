from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

TZ=ZoneInfo("America/Sao_Paulo")

@dataclass(frozen=True)
class NightObservation:
    symbol: str
    ts: datetime
    volume: float
    abs_delta: float
    abs_depth_imbalance: float
    range_points: float
    spread_ticks: float

def eligible(o: NightObservation) -> bool:
    if o.ts.tzinfo is None:
        raise ValueError("timezone-aware timestamp required")
    h=o.ts.astimezone(TZ).hour
    return 19 <= h < 22

def summarize(items: list[NightObservation]) -> dict[str,dict[str,float]]:
    groups={}
    for o in items:
        if not eligible(o):
            continue
        g=groups.setdefault(o.symbol,[])
        g.append(o)
    result={}
    for symbol,rows in groups.items():
        n=len(rows)
        result[symbol]={
            "observations":float(n),
            "avg_volume":sum(x.volume for x in rows)/n,
            "avg_abs_delta":sum(x.abs_delta for x in rows)/n,
            "avg_depth_imbalance":sum(x.abs_depth_imbalance for x in rows)/n,
            "avg_range_points":sum(x.range_points for x in rows)/n,
            "avg_spread_ticks":sum(x.spread_ticks for x in rows)/n,
        }
    return result
