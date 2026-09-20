from dataclasses import dataclass
from statistics import mean, pstdev

from packages.validation.evidence import TradeResult, report


@dataclass(frozen=True)
class CostModel:
    commission: float = 0.0
    slippage: float = 0.0

    @property
    def round_trip(self) -> float:
        return self.commission + self.slippage


@dataclass(frozen=True)
class RobustnessReport:
    trades: int
    net_expectancy: float
    profit_factor: float | None
    max_drawdown: float
    sharpe_like: float | None
    avg_mae: float
    avg_mfe: float
    passed: bool


def evaluate(rows: list[TradeResult], costs: CostModel, min_trades: int = 100) -> RobustnessReport:
    adjusted = [
        TradeResult(r.pnl - costs.round_trip, r.mae, r.mfe, r.regime)
        for r in rows
    ]
    base = report(adjusted, min_trades=min_trades)
    return RobustnessReport(
        trades=base.trades,
        net_expectancy=base.expectancy,
        profit_factor=base.profit_factor,
        max_drawdown=base.max_drawdown,
        sharpe_like=base.sharpe_like,
        avg_mae=mean([r.mae for r in rows]) if rows else 0.0,
        avg_mfe=mean([r.mfe for r in rows]) if rows else 0.0,
        passed=base.passed,
    )


def regime_stability(rows: list[TradeResult]) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        groups.setdefault(row.regime, []).append(row.pnl)
    return {name: mean(values) for name, values in groups.items()}


def return_stability(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    sigma = pstdev(values)
    return mean(values) / sigma if sigma else None
