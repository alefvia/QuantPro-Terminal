from packages.decision_engine.engine import decide
from packages.risk_engine.engine import RiskEngine
from packages.core.contracts import Decision

def test_risk_veto_forces_wait():
    risk = RiskEngine().evaluate(rr=3.0, event_blocked=True, data_ok=True)
    assert risk.approved is False
    assert decide(0.95, risk.approved) == Decision.WAIT

def test_long_requires_risk_approval():
    risk = RiskEngine().evaluate(rr=2.0, event_blocked=False, data_ok=True)
    assert risk.approved is True
    assert decide(0.70, risk.approved) == Decision.LONG
