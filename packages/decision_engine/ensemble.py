from dataclasses import dataclass
from packages.core.contracts import Decision

@dataclass(frozen=True)
class EnsembleDecision:
    decision: Decision
    score: float
    disagreement: float

def ensemble(scores: list[float], threshold: float = 0.55, max_disagreement: float = 0.55) -> EnsembleDecision:
    if not scores:
        return EnsembleDecision(Decision.WAIT,0.0,1.0)
    mean=sum(scores)/len(scores)
    disagreement=max(scores)-min(scores)
    if disagreement > max_disagreement or abs(mean) < threshold:
        return EnsembleDecision(Decision.WAIT,mean,disagreement)
    return EnsembleDecision(Decision.LONG if mean>0 else Decision.SHORT,mean,disagreement)
