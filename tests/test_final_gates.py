from packages.core.maturity import Maturity,PromotionEvidence,highest_maturity
from packages.quant_engine.mbo_ab import Evaluation,compare
from packages.risk_engine.live_gate import evaluate_live_gate
from packages.monitoring.drift import mean_shift
from packages.monitoring.performance import assess_performance

def test_mbo_not_promoted_without_sample():
    a=Evaluation(.2,1.3,10,20)
    b=Evaluation(.3,1.4,9,20)
    assert not compare(a,b).promote_mbo

def test_mbo_promoted_only_on_defined_incremental_value():
    a=Evaluation(.2,1.3,10,120)
    b=Evaluation(.3,1.5,8,120)
    assert compare(a,b,min_expectancy_gain=.05).promote_mbo

def test_live_requires_explicit_authorization():
    gate=evaluate_live_gate(paper_validated=True,feed_licensed=True,risk_verified=True,explicit_authorization=False,kill_switch_ready=True)
    assert not gate.allowed
    assert "EXPLICIT_LIVE_AUTHORIZATION_REQUIRED" in gate.reasons

def test_maturity_stops_at_paper_without_authorization():
    e=PromotionEvidence(True,True,True,True,True,False)
    assert highest_maturity(e)==Maturity.PAPER_VALIDATED

def test_drift_and_performance_monitoring():
    assert mean_shift([0,1,0,1],[5,5,5]).drifted
    assert not assess_performance(expectancy=-1,profit_factor=.8,drawdown=20,drawdown_limit=10,sample=100).healthy
