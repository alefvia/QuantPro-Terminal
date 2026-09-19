from datetime import UTC, datetime, timedelta
import pytest
from packages.quant_engine.events import MacroEvent, event_block
from packages.quant_engine.intermarket import relationship
from packages.quant_engine.macro import MacroSnapshot, gold_context, nq_context
from packages.quant_engine.positioning import positioning
from packages.quant_engine.regime import Regime, detect_regime

def test_event_window_blocks():
    now=datetime(2026,1,1,13,30,tzinfo=UTC)
    blocked,name=event_block(now,[MacroEvent("CPI",now+timedelta(minutes=2))])
    assert blocked and name=="CPI"

def test_macro_contexts():
    old=MacroSnapshot(us_2y=4.0,real_10y=2.0,vix=20,dollar_broad=100)
    new=MacroSnapshot(us_2y=3.9,real_10y=1.9,vix=19,dollar_broad=99)
    assert sum(nq_context(new,old).values())==4
    assert gold_context(new,old)["real_yield"]==1

def test_relationship_positive():
    r=relationship([100,101,102,103,104],[200,202,204,206,208])
    assert r.correlation==pytest.approx(1.0)

def test_positioning():
    p=positioning(120,80,30,[10,20,30,40])
    assert p.net==40 and p.change_1w==10 and p.percentile==1.0

def test_regime_event_has_priority():
    r=detect_regime(trend="UP",atr_ratio=2.0,range_pos=.8,event_blocked=True)
    assert r.regime==Regime.EVENT
