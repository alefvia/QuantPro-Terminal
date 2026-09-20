from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class MarketEvent:
    provider: str
    symbol: str
    kind: str
    observed_at: datetime
    price: Decimal
    size: Decimal
    side: str = "unknown"
    level: int | None = None

@dataclass(frozen=True)
class FeedCapabilities:
    trades: bool
    quotes: bool
    depth: bool
    realtime: bool
    licensed: bool

def validate_orderflow_feed(c: FeedCapabilities, realtime: bool = False) -> None:
    if not (c.trades and c.quotes and c.depth):
        raise ValueError("order flow requires trades, quotes and depth")
    if realtime and not (c.realtime and c.licensed):
        raise ValueError("realtime requires a licensed realtime feed")
