from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class BaselineComparison:
    candidate_expectancy: float
    baseline_expectancy: float
    uplift: float
    beats_baseline: bool


def compare(candidate: list[float], baseline: list[float]) -> BaselineComparison:
    if not candidate or not baseline:
        raise ValueError("candidate and baseline samples are required")
    candidate_mean = mean(candidate)
    baseline_mean = mean(baseline)
    uplift = candidate_mean - baseline_mean
    return BaselineComparison(candidate_mean, baseline_mean, uplift, uplift > 0)
