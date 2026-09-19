from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class BookLevel:
    price: float
    bid_size: float
    ask_size: float

@dataclass(frozen=True)
class DepthSnapshot:
    symbol: str
    observed_at: datetime
    levels: tuple[BookLevel,...]

@dataclass(frozen=True)
class OrderEvent:
    symbol: str
    observed_at: datetime
    order_id: str
    action: str
    side: str
    price: float
    size: float
