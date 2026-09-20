from dataclasses import dataclass

@dataclass(frozen=True)
class LiveGate:
    allowed: bool
    reasons: tuple[str,...]

def evaluate_live_gate(*,paper_validated: bool,feed_licensed: bool,risk_verified: bool,explicit_authorization: bool,kill_switch_ready: bool) -> LiveGate:
    reasons=[]
    if not paper_validated: reasons.append("PAPER_NOT_VALIDATED")
    if not feed_licensed: reasons.append("FEED_LICENSE_NOT_CONFIRMED")
    if not risk_verified: reasons.append("RISK_CONTROLS_NOT_VERIFIED")
    if not explicit_authorization: reasons.append("EXPLICIT_LIVE_AUTHORIZATION_REQUIRED")
    if not kill_switch_ready: reasons.append("KILL_SWITCH_NOT_READY")
    return LiveGate(not reasons,tuple(reasons))
