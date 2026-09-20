from datetime import UTC,datetime
from decimal import Decimal
from packages.data_engine.gateway import MarketEvent
from packages.orderflow.advanced import AdvancedOrderFlow
from packages.orderflow.session_compare import in_night_window

def trade(price,size,side):
    return MarketEvent("test","NQ","trade",datetime.now(UTC),Decimal(price),Decimal(size),side)

def test_cumulative_delta_and_imbalance():
    e=AdvancedOrderFlow(imbalance_ratio=Decimal(3),absorption_volume=Decimal(10))
    e.ingest(trade("100","12","ask"))
    e.ingest(trade("100","2","bid"))
    s=e.snapshot()
    assert s.cumulative_delta == Decimal(10)
    assert s.stacked_buy_levels == 1
    assert s.absorption_ask

def test_brazil_night_window():
    ts=datetime(2026,9,20,22,30,tzinfo=UTC)
    assert in_night_window(ts)
