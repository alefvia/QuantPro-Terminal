from datetime import UTC,datetime
from packages.decision_engine.confluence import Action,Evidence,decide
from packages.paper.live_paper import PaperLedger,PaperObservation
from packages.validation.evidence import TradeResult,report
from packages.validation.walk_forward import expanding_folds

def test_decision_wait_and_risk_veto():
    assert decide(Evidence(.1,.1,.1,.1)).action is Action.WAIT
    assert decide(Evidence(1,1,1,1,False)).action is Action.WAIT

def test_decision_long_short_and_no_fake_probability():
    long=decide(Evidence(1,1,1,1))
    short=decide(Evidence(-1,-1,-1,-1))
    assert long.action is Action.LONG
    assert short.action is Action.SHORT
    assert long.probability is None

def test_validation_gate():
    rows=[TradeResult(2,-1,3) for _ in range(80)]+[TradeResult(-1,-2,1) for _ in range(20)]
    r=report(rows)
    assert r.trades==100
    assert r.expectancy>0
    assert r.passed

def test_walk_forward_no_overlap():
    folds=expanding_folds(200,100,25)
    assert folds[0].train_end==folds[0].test_start
    assert folds[-1].test_end<=200

def test_paper_never_live_eligible():
    ledger=PaperLedger()
    d=decide(Evidence(1,1,1,1))
    ledger.append(PaperObservation(datetime.now(UTC),"NQ",d,25000.0,True))
    assert len(ledger.rows)==1
    assert not ledger.live_eligible
