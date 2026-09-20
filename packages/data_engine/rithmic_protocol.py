"""Rithmic R|Protocol integration boundary for MNQ.

This module intentionally contains no unofficial wire implementation and no credentials.
The official R|Protocol Dev Kit supplies protobuf schemas, endpoints and application
identifiers. Until those artifacts are available, the adapter fails closed.

Confirmed research target: front-month MNQ on CME. Symbol resolution must come from
Rithmic reference data rather than a hard-coded contract month.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from packages.data_engine.gateway import FeedCapabilities, MarketEvent, validate_orderflow_feed


@dataclass(frozen=True)
class RithmicSettings:
    system_name: str = "Rithmic Paper Trading"
    exchange: str = "CME"
    root_symbol: str = "MNQ"
    app_name: str | None = None
    app_version: str | None = None
    websocket_url: str | None = None

    @property
    def devkit_ready(self) -> bool:
        return bool(self.app_name and self.app_version and self.websocket_url)


class RithmicProtocolAdapter:
    """Provider adapter prepared for the official R|Protocol Dev Kit."""

    name = "rithmic-r-protocol"

    def __init__(self, settings: RithmicSettings | None = None) -> None:
        self.settings = settings or RithmicSettings()
        # Do not claim MBO until the entitlement is verified programmatically.
        self.capabilities = FeedCapabilities(
            trades=True,
            quotes=True,
            depth=True,
            realtime=True,
            licensed=True,
        )

    def assert_connectable(self) -> None:
        if not self.settings.devkit_ready:
            raise RuntimeError(
                "Rithmic Dev Kit configuration is pending; refusing to invent endpoints "
                "or connect with incomplete credentials."
            )
        validate_orderflow_feed(self.capabilities, realtime=True)

    async def events(self) -> AsyncIterator[MarketEvent]:
        self.assert_connectable()
        raise RuntimeError(
            "Official R|Protocol protobuf bindings are not installed yet. "
            "Install the Dev Kit artifacts before enabling ingestion."
        )
        yield  # pragma: no cover


def normalize_trade(
    *,
    symbol: str,
    observed_at: datetime,
    price: Decimal,
    size: Decimal,
    aggressor: str,
) -> MarketEvent:
    """Normalize a Rithmic trade into QuantPro's provider-neutral event."""
    if observed_at.tzinfo is None:
        raise ValueError("Rithmic timestamps must be timezone-aware")
    side = {"buy": "ask", "sell": "bid"}.get(aggressor.lower(), "unknown")
    return MarketEvent("rithmic", symbol, "trade", observed_at, price, size, side)


def normalize_depth(
    *,
    symbol: str,
    observed_at: datetime,
    price: Decimal,
    size: Decimal,
    side: str,
    level: int | None = None,
) -> MarketEvent:
    """Normalize one MBP/depth level. Size zero removes the level downstream."""
    if observed_at.tzinfo is None:
        raise ValueError("Rithmic timestamps must be timezone-aware")
    normalized_side = side.lower()
    if normalized_side not in {"bid", "ask"}:
        raise ValueError("depth side must be bid or ask")
    return MarketEvent(
        "rithmic", symbol, "depth", observed_at, price, size, normalized_side, level
    )
