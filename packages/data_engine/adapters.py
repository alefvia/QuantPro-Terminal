from dataclasses import dataclass
from typing import Protocol

from packages.data_engine.gateway import FeedCapabilities, MarketEvent


class FuturesAdapter(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def capabilities(self) -> FeedCapabilities: ...

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def events(self) -> list[MarketEvent]: ...


@dataclass
class UnconfiguredAdapter:
    provider_name: str
    capabilities: FeedCapabilities

    @property
    def name(self) -> str:
        return self.provider_name

    def connect(self) -> None:
        raise RuntimeError(f"{self.provider_name} credentials/protocol are not configured")

    def disconnect(self) -> None:
        return None

    def events(self) -> list[MarketEvent]:
        return []


def rithmic_placeholder() -> UnconfiguredAdapter:
    return UnconfiguredAdapter(
        "Rithmic",
        FeedCapabilities(trades=True, quotes=True, depth=True, realtime=False, licensed=False),
    )


def ibkr_placeholder() -> UnconfiguredAdapter:
    return UnconfiguredAdapter(
        "IBKR",
        FeedCapabilities(trades=True, quotes=True, depth=True, realtime=False, licensed=False),
    )
