from datetime import UTC,datetime
from packages.data_engine.live_state import FeedPacket,MarketStateStore

def test_store_accepts_timestamped_packet():
    s=MarketStateStore()
    s.ingest(FeedPacket("NQ","trade",datetime.now(UTC),25000,1,"ask"))
    assert s.snapshot("NQ")["price"]==25000
    assert s.snapshot("NQ")["events"]==1

def test_store_rejects_bad_symbol_and_naive_time():
    s=MarketStateStore()
    try:
        s.ingest(FeedPacket("ES","trade",datetime.now(UTC),1,1,"ask"))
        assert False
    except ValueError:
        pass
    try:
        s.ingest(FeedPacket("NQ","trade",datetime.now(),1,1,"ask"))
        assert False
    except ValueError:
        pass
