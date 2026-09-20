from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventTier(str, Enum):
    NONE = "none"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class MacroEvent:
    name: str
    scheduled_at: datetime
    actual: float | None = None
    consensus: float | None = None
    previous: float | None = None
    tier: EventTier = EventTier.HIGH

    @property
    def surprise(self) -> float | None:
        if self.actual is None or self.consensus is None:
            return None
        return self.actual - self.consensus


@dataclass(frozen=True)
class MacroContext:
    rates_2y: float = 0.0
    rates_10y: float = 0.0
    real_yield_10y: float = 0.0
    dollar: float = 0.0
    volatility: float = 0.0
    event: MacroEvent | None = None


def event_risk_multiplier(minutes_to_event: float | None, tier: EventTier) -> float:
    if minutes_to_event is None or tier is EventTier.NONE:
        return 1.0
    distance = abs(minutes_to_event)
    if tier is EventTier.HIGH:
        if distance <= 5:
            return 0.0
        if distance <= 15:
            return 0.25
        if distance <= 30:
            return 0.5
    if tier is EventTier.MEDIUM and distance <= 10:
        return 0.5
    return 1.0


def dynamic_macro_weight(
    *,
    base_weight: float = 0.15,
    minutes_to_event: float | None = None,
    tier: EventTier = EventTier.NONE,
    reaction_confirmed: bool = False,
) -> float:
    """Context weight, not a directional forecast."""
    weight = base_weight
    if tier is EventTier.HIGH and minutes_to_event is not None and abs(minutes_to_event) <= 30:
        weight = max(weight, 0.30)
    if reaction_confirmed:
        weight = max(weight, 0.35)
    return min(weight, 0.40)
