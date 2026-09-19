from dataclasses import dataclass
from datetime import UTC, datetime
import math

@dataclass(frozen=True)
class QualityResult:
    ok: bool
    reason: str

def validate_observation(*, observed_at: datetime, value: float) -> QualityResult:
    if observed_at.tzinfo is None:
        return QualityResult(False, "TIMESTAMP_NOT_TIMEZONE_AWARE")
    if observed_at > datetime.now(UTC):
        return QualityResult(False, "FUTURE_TIMESTAMP")
    if not math.isfinite(value):
        return QualityResult(False, "NON_FINITE_VALUE")
    return QualityResult(True, "OK")
