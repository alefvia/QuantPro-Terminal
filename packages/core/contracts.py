from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Decision(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    WAIT = "WAIT"

@dataclass(frozen=True)
class Evidence:
    engine: str
    score: float
    reason: str
    observed_at: datetime

@dataclass(frozen=True)
class DecisionCandidate:
    symbol: str
    horizon: str
    decision: Decision
    score: float
    evidence: tuple[Evidence, ...]
    observed_at: datetime
