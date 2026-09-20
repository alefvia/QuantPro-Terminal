from dataclasses import dataclass


@dataclass(frozen=True)
class ReactionWindow:
    event: str
    surprise: float | None
    nq_return: float | None = None
    gold_return: float | None = None
    yield_2y_change: float | None = None
    yield_10y_change: float | None = None
    dollar_return: float | None = None
    cvd_change: float | None = None


@dataclass(frozen=True)
class ReactionAssessment:
    cross_market_alignment: float
    flow_alignment: float
    usable: bool
    reason: str


def assess_reaction(window: ReactionWindow) -> ReactionAssessment:
    observed = [
        window.nq_return,
        window.gold_return,
        window.yield_2y_change,
        window.dollar_return,
    ]
    if window.surprise is None or sum(x is not None for x in observed) < 2:
        return ReactionAssessment(0.0, 0.0, False, "insufficient point-in-time reaction data")

    signs = [1 if x > 0 else -1 if x < 0 else 0 for x in observed if x is not None]
    alignment = abs(sum(signs)) / len(signs) if signs else 0.0
    flow = 0.0
    if window.cvd_change is not None and window.nq_return is not None:
        flow = 1.0 if window.cvd_change * window.nq_return > 0 else -1.0
    return ReactionAssessment(alignment, flow, True, "descriptive reaction; not a forecast")
