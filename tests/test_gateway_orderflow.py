from datetime import UTC, datetime
from decimal import Decimal
import pytest
from packages.data_engine.gateway import FeedCapabilities, MarketEvent, validate_orderflow_feed
from packages.orderflow.core import OrderFlowEngine

def ev(kind, side, size, price="100"):
    return MarketEvent("test", "NQ", kind, datetime.now(UTC), Decimal(price), Decimal(size), side)

def test_delta_and_depth():
    engine = OrderFlowEngine()
    engine.ingest(ev("trade", "ask", "5"))
    engine.ingest(ev("trade", "bid", "2"))
    engine.ingest(ev("depth", "bid", "12", "99.75"))
    engine.ingest(ev("depth", "ask", "8", "100.25"))
    snap = engine.snapshot()
    assert snap.delta == Decimal(3)
    assert snap.depth_imbalance == Decimal("0.2")

def test_realtime_is_fail_closed():
    caps = FeedCapabilities(True, True, True, True, False)
    with pytest.raises(ValueError):
        validate_orderflow_feed(caps, realtime=True)
