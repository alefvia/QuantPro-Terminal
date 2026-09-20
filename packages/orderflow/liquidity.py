from dataclasses import dataclass
from decimal import Decimal
from packages.data_engine.gateway import MarketEvent

@dataclass(frozen=True)
class LiquiditySnapshot:
    added_bid: Decimal
    added_ask: Decimal
    pulled_bid: Decimal
    pulled_ask: Decimal
    persistent_bid_levels: int
    persistent_ask_levels: int

class LiquidityTracker:
    def __init__(self, persistence_updates: int = 3):
        self.books={"bid":{},"ask":{}}
        self.age={"bid":{},"ask":{}}
        self.added={"bid":Decimal(0),"ask":Decimal(0)}
        self.pulled={"bid":Decimal(0),"ask":Decimal(0)}
        self.persistence_updates=persistence_updates

    def ingest(self,event: MarketEvent) -> None:
        if event.kind != "depth" or event.side not in self.books:
            return
        book=self.books[event.side]
        old=book.get(event.price,Decimal(0))
        diff=event.size-old
        if diff > 0:
            self.added[event.side]+=diff
        elif diff < 0:
            self.pulled[event.side]+=-diff
        if event.size == 0:
            book.pop(event.price,None)
            self.age[event.side].pop(event.price,None)
        else:
            book[event.price]=event.size
            self.age[event.side][event.price]=self.age[event.side].get(event.price,0)+1

    def snapshot(self) -> LiquiditySnapshot:
        pb=sum(v>=self.persistence_updates for v in self.age["bid"].values())
        pa=sum(v>=self.persistence_updates for v in self.age["ask"].values())
        return LiquiditySnapshot(self.added["bid"],self.added["ask"],self.pulled["bid"],self.pulled["ask"],pb,pa)
