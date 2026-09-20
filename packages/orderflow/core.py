from dataclasses import dataclass
from decimal import Decimal
from packages.data_engine.gateway import MarketEvent

@dataclass(frozen=True)
class OrderFlowSnapshot:
    buy_volume: Decimal
    sell_volume: Decimal
    delta: Decimal
    bid_depth: Decimal
    ask_depth: Decimal
    depth_imbalance: Decimal | None

class OrderFlowEngine:
    def __init__(self):
        self.buy = Decimal(0)
        self.sell = Decimal(0)
        self.bid = {}
        self.ask = {}

    def ingest(self, event: MarketEvent) -> None:
        if event.kind == "trade":
            if event.side == "ask":
                self.buy += event.size
            elif event.side == "bid":
                self.sell += event.size
        if event.kind == "depth":
            book = self.bid if event.side == "bid" else self.ask
            if event.size == 0:
                book.pop(event.price, None)
            else:
                book[event.price] = event.size

    def snapshot(self) -> OrderFlowSnapshot:
        bid = sum(self.bid.values(), Decimal(0))
        ask = sum(self.ask.values(), Decimal(0))
        total = bid + ask
        imbalance = (bid - ask) / total if total else None
        return OrderFlowSnapshot(self.buy, self.sell, self.buy - self.sell, bid, ask, imbalance)
