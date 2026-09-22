"""Rithmic R|Protocol integration boundary for MNQ.

Prepared against the official R|Protocol 0.90.0.0 package supplied by Rithmic.
No credentials or vendor protobuf sources are committed here.

The approved development environment is Rithmic Test. Contract resolution must
use Rithmic reference/front-month data rather than a hard-coded expiry.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from packages.data_engine.gateway import FeedCapabilities, MarketEvent, validate_orderflow_feed


@dataclass(frozen=True)
class RithmicSettings:
    system_name: str = "Rithmic Test"
    exchange: str = "CME"
    root_symbol: str = "MNQ"
    app_name: str = "QuantPro"
    app_version: str = "0.1.0"
    websocket_url: str | None = None

    @property
    def devkit_ready(self) -> bool:
        return bool(
            self.system_name == "Rithmic Test"
            and self.app_name
            and self.app_version
            and self.websocket_url
            and self.websocket_url.startswith("wss://")
        )


class RithmicProtocolAdapter:
    """Provider boundary for the official R|Protocol ticker-plant connection."""

    name = "rithmic-r-protocol"

    def __init__(self, settings: RithmicSettings | None = None) -> None:
        self.settings = settings or RithmicSettings()
        # API package confirms message support for trades, BBO and order book.
        # MBO entitlement still requires an authenticated runtime test.
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
                "Rithmic Test connection metadata is incomplete; refusing to guess "
                "or use a non-TLS endpoint."
            )
        validate_orderflow_feed(self.capabilities, realtime=True)

    async def events(self) -> AsyncIterator[MarketEvent]:
        self.assert_connectable()
        raise RuntimeError(
            "R|Protocol 0.90.0.0 bindings must be supplied at deployment/runtime "
            "before WebSocket ingestion can start."
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
    if observed_at.tzinfo is None:
        raise ValueError("Rithmic timestamps must be timezone-aware")
    normalized_side = side.lower()
    if normalized_side not in {"bid", "ask"}:
        raise ValueError("depth side must be bid or ask")
    return MarketEvent(
        "rithmic", symbol, "depth", observed_at, price, size, normalized_side, level
    )
