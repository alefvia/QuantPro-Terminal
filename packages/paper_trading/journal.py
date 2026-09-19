from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class JournalRecord:
    symbol: str
    opened_at: datetime
    closed_at: datetime | None
    side: str
    entry: float
    exit: float | None
    stop: float
    target: float
    score: float
    regime: str
    mae: float | None = None
    mfe: float | None = None
    pnl: float | None = None
