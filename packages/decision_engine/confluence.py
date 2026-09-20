from dataclasses import dataclass
from enum import Enum

class Action(str,Enum):
    LONG="LONG"
    SHORT="SHORT"
    WAIT="WAIT"

@dataclass(frozen=True)
class Evidence:
    structure: float
    orderflow: float
    regime: float
    macro: float
    risk_ok: bool=True

@dataclass(frozen=True)
class Decision:
    action: Action
    score: float
    probability: float | None
    reason: str

def decide(e: Evidence, threshold: float=.55) -> Decision:
    if not e.risk_ok:
        return Decision(Action.WAIT,0.0,None,"risk veto")
    score=.30*e.structure+.35*e.orderflow+.20*e.regime+.15*e.macro
    if score >= threshold:
        action=Action.LONG
    elif score <= -threshold:
        action=Action.SHORT
    else:
        action=Action.WAIT
    return Decision(action,score,None,"probability unavailable until OOS calibration")
