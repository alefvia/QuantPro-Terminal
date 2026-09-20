from datetime import UTC, datetime
from decimal import Decimal

from packages.data_engine.gateway import MarketEvent
from packages.data_engine.sierra_delayed import SierraDelayedProfile
from packages.orderflow.footprint import Footprint
from packages.orderflow.liquidity import LiquidityTracker
from packages.orderflow.night_session import (
    NightObservation,
    cme_reopen_brazil,
    summarize,
)
from packages.orderflow.response import assess_response


def event(kind, side, size, price="100"):
    return MarketEvent(
        "test",
        "NQ",
        kind,
        datetime.now(UTC),
        Decimal(price),
        Decimal(size),
        side,
    )


def add_buy_imbalance(f, price):
    f.ingest(event("trade", "bid", "1", price))
    f.ingest(event("trade", "ask", "4", price))


def test_footprint_stacked_buy_requires_adjacent_ticks():
    f = Footprint(Decimal(3), tick_size=Decimal("0.25"))
    for p in ("100.00", "100.25", "100.50"):
        add_buy_imbalance(f, p)
    assert f.stacked(3) == (True, False)


def test_footprint_gap_is_not_stacked():
    f = Footprint(Decimal(3), tick_size=Decimal("0.25"))
    for p in ("100.00", "100.25", "100.75"):
        add_buy_imbalance(f, p)
    assert f.stacked(3) == (False, False)


def test_liquidity_add_pull():
    t = LiquidityTracker(2)
    t.ingest(event("depth", "bid", "10"))
    t.ingest(event("depth", "bid", "12"))
    t.ingest(event("depth", "bid", "7"))
    s = t.snapshot()
    assert s.added_bid == Decimal(12)
    assert s.pulled_bid == Decimal(5)
    assert s.persistent_bid_levels == 1


def test_absorption_response_confirmation():
    a = assess_response(
        bid_volume=Decimal(60),
        ask_volume=Decimal(10),
        start=Decimal(100),
        end=Decimal(101),
        threshold=Decimal(50),
    )
    assert a.bid_confirmed


def test_sierra_delayed_never_realtime():
    p = SierraDelayedProfile()
    assert p.delay_seconds == 610
    assert p.capabilities.depth
    assert not p.capabilities.realtime


def test_reopen_tracks_us_dst_in_brazil():
    summer = cme_reopen_brazil(datetime(2026, 9, 20, 22, tzinfo=UTC))
    winter = cme_reopen_brazil(datetime(2026, 12, 20, 23, tzinfo=UTC))
    assert summer.hour == 19
    assert winter.hour == 20


def test_night_session_summary_uses_reopen_window():
    rows = [
        NightObservation(
            "NQ",
            datetime(2026, 9, 20, 22, 30, tzinfo=UTC),
            100,
            20,
            0.2,
            10,
            1,
        )
    ]
    s = summarize(rows)
    assert s["NQ"]["observations"] == 1
