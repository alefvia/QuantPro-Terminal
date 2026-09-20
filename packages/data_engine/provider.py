from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass(frozen=True)
class Tick:
    symbol: str
    observed_at: datetime
    price: float
    size: float
    bid: float | None = None
    ask: float | None = None

class FuturesProvider(Protocol):
    @property
    def mode(self) -> str: ...
    def latest(self, symbol: str) -> Tick: ...
    def history(self, symbol: str, start: datetime, end: datetime) -> list[Tick]: ...
