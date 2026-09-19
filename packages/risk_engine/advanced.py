from dataclasses import dataclass

@dataclass(frozen=True)
class RiskLimits:
    max_daily_loss: float
    max_drawdown: float
    max_consecutive_losses: int
    max_position_risk: float
    min_rr: float = 1.8

@dataclass(frozen=True)
class AccountState:
    daily_pnl: float
    drawdown: float
    consecutive_losses: int

@dataclass(frozen=True)
class RiskAssessment:
    approved: bool
    reason: str
    max_quantity: int

def assess(*,limits: RiskLimits,state: AccountState,risk_per_contract: float,rr: float,event_blocked: bool,data_ok: bool,kill_switch: bool=False) -> RiskAssessment:
    if kill_switch:
        return RiskAssessment(False,"KILL_SWITCH",0)
    if not data_ok:
        return RiskAssessment(False,"DATA_QUALITY_BLOCK",0)
    if event_blocked:
        return RiskAssessment(False,"EVENT_RISK_BLOCK",0)
    if state.daily_pnl <= -abs(limits.max_daily_loss):
        return RiskAssessment(False,"MAX_DAILY_LOSS",0)
    if state.drawdown >= limits.max_drawdown:
        return RiskAssessment(False,"MAX_DRAWDOWN",0)
    if state.consecutive_losses >= limits.max_consecutive_losses:
        return RiskAssessment(False,"CONSECUTIVE_LOSS_LIMIT",0)
    if rr < limits.min_rr:
        return RiskAssessment(False,"RR_BELOW_MINIMUM",0)
    if risk_per_contract <= 0:
        return RiskAssessment(False,"INVALID_CONTRACT_RISK",0)
    qty=int(limits.max_position_risk//risk_per_contract)
    if qty < 1:
        return RiskAssessment(False,"POSITION_RISK_TOO_HIGH",0)
    return RiskAssessment(True,"APPROVED_PAPER",qty)
