from packages.core.contracts import Decision

def decide(score: float, risk_approved: bool) -> Decision:
    if not risk_approved:
        return Decision.WAIT
    if score >= 0.65:
        return Decision.LONG
    if score <= -0.65:
        return Decision.SHORT
    return Decision.WAIT
