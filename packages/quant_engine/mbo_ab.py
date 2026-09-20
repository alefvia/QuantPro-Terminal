from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Evaluation:
    expectancy: float
    profit_factor: float | None
    max_drawdown: float
    trades: int

@dataclass(frozen=True)
class ABResult:
    baseline: Evaluation
    mbo: Evaluation
    expectancy_delta: float
    drawdown_delta: float
    promote_mbo: bool
    reason: str

def compare(baseline: Evaluation,mbo: Evaluation,*,min_trades: int=100,min_expectancy_gain: float=0.0) -> ABResult:
    delta=mbo.expectancy-baseline.expectancy
    dd_delta=mbo.max_drawdown-baseline.max_drawdown
    enough=min(baseline.trades,mbo.trades)>=min_trades
    promote=enough and math.isfinite(delta) and delta>min_expectancy_gain and dd_delta<=0
    reason="PROMOTE_MBO" if promote else ("INSUFFICIENT_SAMPLE" if not enough else "NO_ROBUST_INCREMENTAL_VALUE")
    return ABResult(baseline,mbo,delta,dd_delta,promote,reason)
