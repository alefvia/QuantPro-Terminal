from dataclasses import dataclass
from packages.decision_engine.thesis import TradeThesis

@dataclass(frozen=True)
class Explanation:
    headline: str
    facts: tuple[str, ...]

def explain(thesis: TradeThesis) -> Explanation:
    facts=tuple(
        [f"Favorável: {x}" for x in thesis.positive]
        +[f"Contrário: {x}" for x in thesis.negative]
        +([f"Risco de evento: {thesis.event_risk}"] if thesis.event_risk else [])
        +[f"Invalidação: {thesis.invalidation}"]
    )
    return Explanation(
        headline=f"{thesis.symbol}: {thesis.decision.value} | regime={thesis.regime} | score={thesis.score:.2f}",
        facts=facts,
    )
