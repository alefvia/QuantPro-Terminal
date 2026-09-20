from dataclasses import dataclass

@dataclass(frozen=True)
class PerformanceGate:
    healthy: bool
    reasons: tuple[str,...]

def assess_performance(*,expectancy: float,profit_factor: float | None,drawdown: float,drawdown_limit: float,sample: int,min_sample: int=30) -> PerformanceGate:
    reasons=[]
    if sample<min_sample: reasons.append("LOW_SAMPLE")
    if expectancy<=0: reasons.append("EXPECTANCY_DEGRADED")
    if profit_factor is None or profit_factor<1.0: reasons.append("PROFIT_FACTOR_DEGRADED")
    if drawdown>drawdown_limit: reasons.append("DRAWDOWN_BREACH")
    return PerformanceGate(not reasons,tuple(reasons))
