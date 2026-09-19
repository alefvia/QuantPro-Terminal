from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True)
class MacroEvent:
    name: str
    scheduled_at: datetime
    impact: str = "high"

def event_block(now: datetime, events: list[MacroEvent], before_minutes: int = 10, after_minutes: int = 5) -> tuple[bool, str | None]:
    for event in events:
        if event.scheduled_at.tzinfo is None or now.tzinfo is None:
            raise ValueError("event timestamps must be timezone-aware")
        if event.impact == "high" and event.scheduled_at - timedelta(minutes=before_minutes) <= now <= event.scheduled_at + timedelta(minutes=after_minutes):
            return True, event.name
    return False, None
