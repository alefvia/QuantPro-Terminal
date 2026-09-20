from dataclasses import dataclass

from packages.core.maturity import Maturity, PromotionEvidence, highest_maturity
from packages.monitoring.performance_guard import evaluate_recent
from packages.risk_engine.live_gate import evaluate_live_gate


@dataclass(frozen=True)
class PromotionDecision:
    maturity: Maturity
    live_allowed: bool
    reasons: tuple[str, ...]


def evaluate_promotion(
    evidence: PromotionEvidence,
    recent_pnls: list[float],
    *,
    kill_switch_ready: bool,
) -> PromotionDecision:
    maturity = highest_maturity(evidence)
    live = evaluate_live_gate(
        paper_validated=evidence.paper_validated,
        feed_licensed=evidence.feed_licensed,
        risk_verified=evidence.risk_controls_verified,
        explicit_authorization=evidence.explicit_live_authorization,
        kill_switch_ready=kill_switch_ready,
    )
    performance = evaluate_recent(recent_pnls)
    reasons = list(live.reasons)
    if not performance.allowed:
        reasons.append(performance.reason)
    allowed = maturity is Maturity.LIVE_ELIGIBLE and live.allowed and performance.allowed
    return PromotionDecision(maturity, allowed, tuple(reasons))
