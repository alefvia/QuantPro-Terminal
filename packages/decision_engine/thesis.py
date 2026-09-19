from dataclasses import dataclass
from packages.core.contracts import Decision

@dataclass(frozen=True)
class TradeThesis:
    symbol: str
    decision: Decision
    score: float
    probability: float | None
    regime: str
    positive: tuple[str, ...]
    negative: tuple[str, ...]
    invalidation: str
    event_risk: str | None

def build_thesis(*,symbol: str,score: float,regime: str,positive: list[str],negative: list[str],invalidation: str,event_risk: str | None,risk_approved: bool,threshold: float=.55) -> TradeThesis:
    if not risk_approved or event_risk or abs(score)<threshold:
        decision=Decision.WAIT
    else:
        decision=Decision.LONG if score>0 else Decision.SHORT
    return TradeThesis(symbol,decision,score,None,regime,tuple(positive),tuple(negative),invalidation,event_risk)
