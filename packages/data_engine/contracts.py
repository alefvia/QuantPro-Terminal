from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class MarketObservation:
    symbol: str
    observed_at: datetime
    source: str
    value: float
    field: str
