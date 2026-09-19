from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Trade:
    entry: float
    exit: float
    side: int
    quantity: float = 1.0
    fees: float = 0.0
    slippage: float = 0.0

    @property
    def pnl(self) -> float:
        gross=(self.exit-self.entry)*self.side*self.quantity
        return gross-self.fees-self.slippage

@dataclass(frozen=True)
class BacktestMetrics:
    trades: int
    win_rate: float
    expectancy: float
    profit_factor: float | None
    max_drawdown: float
    sharpe: float | None

def metrics(trades: list[Trade]) -> BacktestMetrics:
    pnl=[t.pnl for t in trades]
    if not pnl:
        return BacktestMetrics(0,0.0,0.0,None,0.0,None)
    wins=[x for x in pnl if x>0]
    losses=[x for x in pnl if x<0]
    gross_profit=sum(wins)
    gross_loss=abs(sum(losses))
    equity=0.0
    peak=0.0
    max_dd=0.0
    for x in pnl:
        equity+=x
        peak=max(peak,equity)
        max_dd=max(max_dd,peak-equity)
    mean=sum(pnl)/len(pnl)
    sharpe=None
    if len(pnl)>1:
        variance=sum((x-mean)**2 for x in pnl)/(len(pnl)-1)
        if variance>0:
            sharpe=mean/math.sqrt(variance)*math.sqrt(len(pnl))
    return BacktestMetrics(
        trades=len(pnl),
        win_rate=len(wins)/len(pnl),
        expectancy=mean,
        profit_factor=(gross_profit/gross_loss if gross_loss>0 else None),
        max_drawdown=max_dd,
        sharpe=sharpe,
    )
