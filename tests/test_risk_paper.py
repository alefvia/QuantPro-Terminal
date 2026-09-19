import pytest
from packages.paper_trading.engine import PaperOrder,Side,simulate_market_fill
from packages.paper_trading.portfolio import PaperPosition
from packages.paper_trading.validation import validate_paper
from packages.risk_engine.advanced import AccountState,RiskLimits,assess

def limits():
    return RiskLimits(500,1000,3,200,1.8)

def test_risk_veto_and_position_size():
    state=AccountState(0,0,0)
    ok=assess(limits=limits(),state=state,risk_per_contract=50,rr=2,event_blocked=False,data_ok=True)
    assert ok.approved and ok.max_quantity==4
    blocked=assess(limits=limits(),state=state,risk_per_contract=50,rr=2,event_blocked=True,data_ok=True)
    assert not blocked.approved and blocked.reason=="EVENT_RISK_BLOCK"

def test_paper_fill_has_adverse_slippage():
    order=PaperOrder("MNQ",Side.BUY,2,100,95,110)
    fill=simulate_market_fill(order,slippage_per_unit=.25,fee_per_contract=1)
    assert fill.fill_price==pytest.approx(100.25)
    assert fill.fee==2

def test_portfolio_round_trip():
    p=PaperPosition("MNQ")
    p.apply(simulate_market_fill(PaperOrder("MNQ",Side.BUY,1,100,95,110)))
    p.apply(simulate_market_fill(PaperOrder("MNQ",Side.SELL,1,105,110,95)))
    assert p.quantity==0 and p.realized_pnl==5

def test_paper_gate_requires_evidence():
    bad=validate_paper(trades=20,expectancy=1,profit_factor=2,max_drawdown=10,drawdown_limit=100)
    assert not bad.eligible and "INSUFFICIENT_TRADES" in bad.reasons
