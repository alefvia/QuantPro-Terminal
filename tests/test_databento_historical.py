from datetime import UTC,datetime
from packages.data_engine.databento_historical import DEFAULT_SYMBOLS,HistoricalRequest

def test_default_products_are_target_markets():
    assert DEFAULT_SYMBOLS==("NQ.v.0","MNQ.v.0","GC.v.0","MGC.v.0")

def test_request_is_continuous_globex():
    r=HistoricalRequest(("NQ.v.0",),datetime(2026,1,1,tzinfo=UTC),datetime(2026,1,2,tzinfo=UTC))
    assert r.dataset=="GLBX.MDP3"
    assert r.stype_in=="continuous"
    assert r.schema=="ohlcv-1m"

def test_invalid_time_range_documented():
    r=HistoricalRequest(("NQ.v.0",),datetime(2026,1,2,tzinfo=UTC),datetime(2026,1,1,tzinfo=UTC))
    assert r.end<=r.start
