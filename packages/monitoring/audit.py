from dataclasses import asdict,dataclass
from datetime import datetime
import json
from pathlib import Path

@dataclass(frozen=True)
class AuditEvent:
    occurred_at: datetime
    component: str
    event: str
    detail: str

def append_audit(event: AuditEvent,path: Path) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    row=asdict(event)
    row["occurred_at"]=event.occurred_at.isoformat()
    with path.open("a",encoding="utf-8") as fh:
        fh.write(json.dumps(row,sort_keys=True)+"\n")
