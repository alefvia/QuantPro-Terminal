from dataclasses import dataclass
from datetime import datetime
from packages.decision_engine.confluence import Decision

@dataclass(frozen=True)
class PaperObservation:
    ts: datetime
    symbol: str
    decision: Decision
    reference_price: float
    feed_delayed: bool

class PaperLedger:
    def __init__(self):
        self.rows: list[PaperObservation]=[]

    def append(self,row: PaperObservation) -> None:
        if row.ts.tzinfo is None:
            raise ValueError("timezone-aware timestamp required")
        self.rows.append(row)

    @property
    def live_eligible(self) -> bool:
        return False
