from datetime import UTC, datetime, timedelta
import pytest
from packages.backtest.engine import Trade, metrics
from packages.backtest.walk_forward import expanding_walk_forward
from packages.replay.engine import ReplayEvent, replay

def test_costs_reduce_pnl_and_metrics():
    trades=[Trade(100,110,1,fees=1,slippage=1),Trade(100,95,1,fees=1,slippage=1)]
    m=metrics(trades)
    assert [t.pnl for t in trades]==[8,-7]
    assert m.trades==2
    assert m.expectancy==pytest.approx(.5)
    assert m.profit_factor==pytest.approx(8/7)
    assert m.max_drawdown==7

def test_walk_forward_never_trains_on_test():
    folds=expanding_walk_forward(100,60,10)
    assert folds[0].train==slice(0,60)
    assert folds[0].test==slice(60,70)
    assert folds[-1].test.stop==100

def test_replay_reveals_by_available_time():
    t=datetime(2026,1,1,tzinfo=UTC)
    future_observed=ReplayEvent(t+timedelta(days=1),t+timedelta(hours=2),"macro",{})
    now=ReplayEvent(t,t+timedelta(hours=1),"price",{})
    states=list(replay([future_observed,now]))
    assert states[0][0]==t+timedelta(hours=1)
    assert len(states[0][1])==1
