import pytest

from packages.quant_engine.market import Bar, atr, range_position, realized_vol, session_vwap, simple_trend
from packages.quant_engine.volume_profile import build_volume_profile

def test_vwap():
    assert session_vwap([100, 110], [3, 1]) == pytest.approx(102.5)

def test_atr():
    bars=[Bar(101+i,99+i,100+i) for i in range(16)]
    assert atr(bars,14) == pytest.approx(2.0)

def test_realized_vol_and_range():
    assert realized_vol([100,101,100,103]) is not None
    assert range_position(105,100,110) == pytest.approx(0.5)

def test_trend():
    closes=[100+i for i in range(30)]
    assert simple_trend(closes) == "UP"

def test_volume_profile():
    p=build_volume_profile([100,101,102],[10,70,20])
    assert p.poc == 101
    assert p.total_volume == 100
    assert p.val <= p.poc <= p.vah
