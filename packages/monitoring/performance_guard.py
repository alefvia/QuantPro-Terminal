from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class PerformanceGuard:
    allowed: bool
    reason: str
    recent_expectancy: float | None


def evaluate_recent(pnls: list[float], min_sample: int = 30, floor: float = 0.0) -> PerformanceGuard:
    if len(pnls) < min_sample:
        return PerformanceGuard(False, "INSUFFICIENT_RECENT_SAMPLE", None)
    expectancy = mean(pnls[-min_sample:])
    if expectancy <= floor:
        return PerformanceGuard(False, "RECENT_EXPECTANCY_BELOW_FLOOR", expectancy)
    return PerformanceGuard(True, "OK", expectancy)
