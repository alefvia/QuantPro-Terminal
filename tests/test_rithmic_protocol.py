from datetime import UTC, datetime
from decimal import Decimal

import pytest

from packages.data_engine.rithmic_protocol import (
    RithmicProtocolAdapter,
    RithmicSettings,
    normalize_depth,
    normalize_trade,
)


def test_rithmic_adapter_fails_closed_without_devkit():
    adapter = RithmicProtocolAdapter()
    with pytest.raises(RuntimeError, match="Dev Kit"):
        adapter.assert_connectable()


def test_devkit_readiness_requires_all_connection_metadata():
    assert not RithmicSettings(app_name="QuantPro").devkit_ready
    settings = RithmicSettings(
        app_name="QuantPro",
        app_version="1",
        websocket_url="wss://example.invalid",
    )
    assert settings.devkit_ready


def test_trade_aggressor_normalization():
    event = normalize_trade(
        symbol="MNQ",
        observed_at=datetime.now(UTC),
        price=Decimal("30000.25"),
        size=Decimal("2"),
        aggressor="buy",
    )
    assert event.kind == "trade"
    assert event.side == "ask"


def test_depth_normalization():
    event = normalize_depth(
        symbol="MNQ",
        observed_at=datetime.now(UTC),
        price=Decimal("30000.00"),
        size=Decimal("8"),
        side="bid",
        level=1,
    )
    assert event.kind == "depth"
    assert event.side == "bid"
    assert event.level == 1


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        normalize_depth(
            symbol="MNQ",
            observed_at=datetime(2026, 9, 21),
            price=Decimal("30000"),
            size=Decimal("1"),
            side="ask",
        )
