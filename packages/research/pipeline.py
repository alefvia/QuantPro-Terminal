from dataclasses import dataclass

from packages.research.discovery import PatternCandidate, discover_binary_patterns
from packages.validation.advanced import CostModel, RobustnessReport, evaluate
from packages.validation.evidence import TradeResult


@dataclass(frozen=True)
class ResearchRun:
    candidates: list[PatternCandidate]
    validation: RobustnessReport
    live_eligible: bool = False


def run_research(
    feature_rows: list[dict[str, float | bool]],
    trades: list[TradeResult],
    feature_names: list[str],
    *,
    target: str = "future_return",
    costs: CostModel | None = None,
) -> ResearchRun:
    candidates = discover_binary_patterns(
        feature_rows,
        feature_names=feature_names,
        target=target,
        min_features=2,
        max_features=min(4, len(feature_names)),
        min_occurrences=30,
    )
    validation = evaluate(trades, costs or CostModel())
    return ResearchRun(candidates, validation, False)
