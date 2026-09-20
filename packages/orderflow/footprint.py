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
    def __init__(self,ratio: Decimal=Decimal(3)):
        self.ratio=ratio
        self.levels={}

    def ingest(self,event: MarketEvent) -> None:
        if event.kind != "trade":
            return
        bid,ask=self.levels.get(event.price,(Decimal(0),Decimal(0)))
        if event.side=="bid":
            bid+=event.size
        elif event.side=="ask":
            ask+=event.size
        self.levels[event.price]=(bid,ask)

    def rows(self) -> list[FootprintLevel]:
        out=[]
        for price,(bid,ask) in sorted(self.levels.items()):
            buy=bid>0 and ask/bid>=self.ratio
            sell=ask>0 and bid/ask>=self.ratio
            out.append(FootprintLevel(price,bid,ask,ask-bid,buy,sell))
        return out

    def stacked(self,minimum: int=3) -> tuple[bool,bool]:
        rows=self.rows()
        buy=max((sum(1 for x in rows[i:i+minimum] if x.buy_imbalance) for i in range(len(rows))),default=0)>=minimum
        sell=max((sum(1 for x in rows[i:i+minimum] if x.sell_imbalance) for i in range(len(rows))),default=0)>=minimum
        return buy,sell
