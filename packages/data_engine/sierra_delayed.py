from dataclasses import dataclass, field
from packages.data_engine.gateway import FeedCapabilities

def delayed_capabilities() -> FeedCapabilities:
    return FeedCapabilities(trades=True,quotes=True,depth=True,realtime=False,licensed=False)

@dataclass(frozen=True)
class SierraDelayedProfile:
    provider: str="sierra_delayed"
    delay_seconds: int=610
    capabilities: FeedCapabilities=field(default_factory=delayed_capabilities)

    def validate_research(self) -> None:
        if not self.capabilities.depth:
            raise RuntimeError("market depth unavailable")
