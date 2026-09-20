from dataclasses import dataclass
from decimal import Decimal
from packages.data_engine.gateway import MarketEvent

@dataclass(frozen=True)
class PriceFlow:
    bid_volume: Decimal = Decimal(0)
    ask_volume: Decimal = Decimal(0)

@dataclass(frozen=True)
class AdvancedSnapshot:
    cumulative_delta: Decimal
    stacked_buy_levels: int
    stacked_sell_levels: int
    absorption_bid: bool
    absorption_ask: bool

class AdvancedOrderFlow:
    def __init__(self, imbalance_ratio: Decimal = Decimal(3), absorption_volume: Decimal = Decimal(50)):
        self.levels: dict[Decimal, PriceFlow] = {}
        self.cumulative_delta = Decimal(0)
        self.imbalance_ratio = imbalance_ratio
        self.absorption_volume = absorption_volume

    def ingest(self, event: MarketEvent) -> None:
        if event.kind != "trade":
            return
        flow = self.levels.get(event.price, PriceFlow())
        if event.side == "ask":
            flow = PriceFlow(flow.bid_volume, flow.ask_volume + event.size)
            self.cumulative_delta += event.size
        elif event.side == "bid":
            flow = PriceFlow(flow.bid_volume + event.size, flow.ask_volume)
            self.cumulative_delta -= event.size
        self.levels[event.price] = flow

    def snapshot(self) -> AdvancedSnapshot:
        buys = sells = 0
        absorption_bid = absorption_ask = False
        for flow in self.levels.values():
            if flow.bid_volume and flow.ask_volume / flow.bid_volume >= self.imbalance_ratio:
                buys += 1
            if flow.ask_volume and flow.bid_volume / flow.ask_volume >= self.imbalance_ratio:
                sells += 1
            absorption_bid |= flow.bid_volume >= self.absorption_volume
            absorption_ask |= flow.ask_volume >= self.absorption_volume
        return AdvancedSnapshot(self.cumulative_delta, buys, sells, absorption_bid, absorption_ask)
