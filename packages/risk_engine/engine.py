from dataclasses import dataclass

@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    reason: str

class RiskEngine:
    """Independent veto layer. Live execution remains disabled in F0."""

    def evaluate(self, *, rr: float, event_blocked: bool, data_ok: bool) -> RiskDecision:
        if not data_ok:
            return RiskDecision(False, "DATA_QUALITY_BLOCK")
        if event_blocked:
            return RiskDecision(False, "EVENT_RISK_BLOCK")
        if rr < 1.8:
            return RiskDecision(False, "RR_BELOW_MINIMUM")
        return RiskDecision(True, "APPROVED_FOR_RESEARCH_OR_PAPER")
