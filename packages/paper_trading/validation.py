from dataclasses import dataclass

@dataclass(frozen=True)
class PaperValidation:
    eligible: bool
    reasons: tuple[str,...]

def validate_paper(*,trades: int,expectancy: float,profit_factor: float | None,max_drawdown: float,drawdown_limit: float,min_trades: int=100,min_profit_factor: float=1.2) -> PaperValidation:
    reasons=[]
    if trades < min_trades:
        reasons.append("INSUFFICIENT_TRADES")
    if expectancy <= 0:
        reasons.append("NON_POSITIVE_EXPECTANCY")
    if profit_factor is None or profit_factor < min_profit_factor:
        reasons.append("PROFIT_FACTOR_BELOW_GATE")
    if max_drawdown > drawdown_limit:
        reasons.append("DRAWDOWN_LIMIT_EXCEEDED")
    return PaperValidation(not reasons,tuple(reasons))
