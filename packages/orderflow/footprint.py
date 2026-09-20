from dataclasses import dataclass
from decimal import Decimal

from packages.data_engine.gateway import MarketEvent


@dataclass(frozen=True)
class FootprintLevel:
    price: Decimal
    bid_volume: Decimal
    ask_volume: Decimal
    delta: Decimal
    buy_imbalance: bool
    sell_imbalance: bool


class Footprint:
    def __init__(
        self,
        ratio: Decimal = Decimal(3),
        tick_size: Decimal = Decimal(1),
    ):
        if ratio <= 0:
            raise ValueError("ratio must be positive")
        if tick_size <= 0:
            raise ValueError("tick_size must be positive")
        self.ratio = ratio
        self.tick_size = tick_size
        self.levels = {}

    def ingest(self, event: MarketEvent) -> None:
        if event.kind != "trade":
            return
        bid, ask = self.levels.get(event.price, (Decimal(0), Decimal(0)))
        if event.side == "bid":
            bid += event.size
        elif event.side == "ask":
            ask += event.size
        self.levels[event.price] = (bid, ask)

    def rows(self) -> list[FootprintLevel]:
        out = []
        for price, (bid, ask) in sorted(self.levels.items()):
            buy = bid > 0 and ask / bid >= self.ratio
            sell = ask > 0 and bid / ask >= self.ratio
            out.append(FootprintLevel(price, bid, ask, ask - bid, buy, sell))
        return out

    def stacked(self, minimum: int = 3) -> tuple[bool, bool]:
        if minimum < 1:
            raise ValueError("minimum must be at least 1")
        rows = self.rows()
        buy_run = sell_run = 0
        buy = sell = False
        previous_price = None
        for row in rows:
            adjacent = (
                previous_price is not None
                and row.price - previous_price == self.tick_size
            )
            if not adjacent:
                buy_run = sell_run = 0
            buy_run = buy_run + 1 if row.buy_imbalance else 0
            sell_run = sell_run + 1 if row.sell_imbalance else 0
            buy = buy or buy_run >= minimum
            sell = sell or sell_run >= minimum
            previous_price = row.price
        return buy, sell
