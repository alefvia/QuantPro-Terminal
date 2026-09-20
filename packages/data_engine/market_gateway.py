from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol

class EventType(str, Enum):
    TRADE="trade"
    QUOTE="quote"
    DEPTH="depth"

class Side(str, Enum):
    BID="bid"
    ASK="ask"
    UNKNOWN="unknown"

@dataclass(frozen=True)
class MarketEvent:
    provider: str
    symbol: str
    event_type: EventType
    observed_at: datetime
    sequence: int | None = None
    price: Decimal | None = None
    size: Decimal | None = None
    side: Side = Side.UNKNOWN
    level: int | None = None

@dataclass(frozen=True)
class GatewayCapabilities:
    trades: bool
    bid_ask: bool
    depth: bool
    mbo: bool
    realtime: bool
    delayed: bool
    licensed: bool

class MarketDataAdapter(Protocol):
    name: str
    capabilities: GatewayCapabilities
    async def events(self, symbols: tuple[str, ...]) -> AsyncIterator[MarketEvent]: ...

class MarketDataGateway:
    def __init__(self, adapter: MarketDataAdapter):
        self.adapter=adapter

    def assert_orderflow_ready(self, *, require_realtime: bool=False) -> None:
        c=self.adapter.capabilities
        if not (c.trades and c.bid_ask and c.depth):
            raise RuntimeError("Order Flow requires trades, bid/ask and market depth")
        if require_realtime and not (c.realtime and c.licensed):
            raise RuntimeError("Realtime Order Flow requires a licensed realtime feed")

    async def stream(self, symbols: tuple[str, ...]):
        self.assert_orderflow_ready()
        async for event in self.adapter.events(symbols):
            if event.observed_at.tzinfo is None:
                raise ValueError("Market events must be timezone-aware")
            yield event
