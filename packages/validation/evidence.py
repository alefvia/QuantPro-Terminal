from dataclasses import dataclass
from statistics import mean,pstdev

@dataclass(frozen=True)
class TradeResult:
    pnl: float
    mae: float
    mfe: float
    regime: str="unknown"

@dataclass(frozen=True)
class ValidationReport:
    trades: int
    expectancy: float
    profit_factor: float | None
    max_drawdown: float
    sharpe_like: float | None
    passed: bool

def report(rows: list[TradeResult], min_trades: int=100, min_pf: float=1.2) -> ValidationReport:
    if not rows:
        return ValidationReport(0,0.0,None,0.0,None,False)
    pnls=[x.pnl for x in rows]
    gains=sum(x for x in pnls if x>0)
    losses=-sum(x for x in pnls if x<0)
    pf=gains/losses if losses else None
    equity=peak=dd=0.0
    for p in pnls:
        equity+=p
        peak=max(peak,equity)
        dd=max(dd,peak-equity)
    sigma=pstdev(pnls)
    sharpe=mean(pnls)/sigma if sigma else None
    passed=len(rows)>=min_trades and mean(pnls)>0 and (pf is None or pf>=min_pf)
    return ValidationReport(len(rows),mean(pnls),pf,dd,sharpe,passed)
