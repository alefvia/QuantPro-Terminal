from dataclasses import dataclass
from packages.data_engine.gateway import FeedCapabilities

@dataclass(frozen=True)
class SierraDelayedProfile:
    provider: str="sierra_delayed"
    delay_seconds: int=610
    capabilities: FeedCapabilities=FeedCapabilities(
        trades=True,quotes=True,depth=True,realtime=False,licensed=False
    )

    def validate_research(self) -> None:
        if not self.capabilities.depth:
            raise RuntimeError("market depth unavailable")
