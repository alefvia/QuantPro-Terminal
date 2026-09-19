from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator

@dataclass(frozen=True)
class ReplayEvent:
    observed_at: datetime
    available_at: datetime
    kind: str
    payload: dict

def replay(events: Iterable[ReplayEvent]) -> Iterator[tuple[datetime, list[ReplayEvent]]]:
    ordered=sorted(events,key=lambda x:(x.available_at,x.observed_at))
    known: list[ReplayEvent]=[]
    for event in ordered:
        if event.available_at.tzinfo is None or event.observed_at.tzinfo is None:
            raise ValueError("timestamps must be timezone-aware")
        known.append(event)
        yield event.available_at, list(known)
