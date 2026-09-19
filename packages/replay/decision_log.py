from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path

@dataclass(frozen=True)
class DecisionLog:
    decided_at: datetime
    symbol: str
    decision: str
    score: float
    regime: str
    risk_approved: bool
    reasons: tuple[str, ...]

def append_jsonl(record: DecisionLog, path: Path) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    row=asdict(record)
    row["decided_at"]=record.decided_at.isoformat()
    with path.open("a",encoding="utf-8") as fh:
        fh.write(json.dumps(row,sort_keys=True)+"\n")
