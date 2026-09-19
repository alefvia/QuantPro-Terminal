from packages.ai_analyst.explainer import explain
from packages.ai_analyst.guardrails import probability_label
from packages.core.contracts import Decision
from packages.decision_engine.thesis import build_thesis

def test_event_forces_wait():
    thesis=build_thesis(symbol="NQ",score=.9,regime="TREND_UP",positive=["above VWAP"],negative=[],invalidation="below VWAP",event_risk="CPI",risk_approved=True)
    assert thesis.decision==Decision.WAIT

def test_probability_not_faked():
    thesis=build_thesis(symbol="GC",score=.8,regime="TREND_UP",positive=["real yield falling"],negative=[],invalidation="structure break",event_risk=None,risk_approved=True)
    assert thesis.probability is None
    assert probability_label(thesis.probability)=="NÃO CALIBRADA"
    assert "GC: LONG" in explain(thesis).headline
