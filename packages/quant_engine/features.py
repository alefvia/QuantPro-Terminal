from dataclasses import dataclass

@dataclass(frozen=True)
class FeatureVector:
    structure: float
    volume: float
    volatility: float
    macro: float
    intermarket: float
    positioning: float
    event_risk: float
    regime: float

    def values(self) -> tuple[float, ...]:
        return (self.structure,self.volume,self.volatility,self.macro,self.intermarket,self.positioning,self.event_risk,self.regime)
