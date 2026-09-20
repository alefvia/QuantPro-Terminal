from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Literal

Side=Literal["bid","ask"]
Kind=Literal["trade","quote","depth"]

@dataclass(frozen=True)
class FeedPacket:
    symbol: str
    kind: Kind
    observed_at: datetime
    price: float
    size: float
    side: Side | None=None

class MarketStateStore:
    allowed={"NQ","MNQ","GC","MGC"}
    def __init__(self):
        self._lock=RLock()
        self._last={}
        self._count={s:0 for s in self.allowed}

    def ingest(self,p: FeedPacket)->None:
        if p.symbol not in self.allowed:
            raise ValueError("unsupported symbol")
        if p.observed_at.tzinfo is None:
            raise ValueError("timezone-aware timestamp required")
        if p.price<=0 or p.size<0:
            raise ValueError("invalid market packet")
        with self._lock:
            prev=self._last.get(p.symbol)
            if prev and p.observed_at<prev.observed_at:
                raise ValueError("out-of-order packet")
            self._last[p.symbol]=p
            self._count[p.symbol]+=1

    def snapshot(self,symbol:str)->dict:
        with self._lock:
            p=self._last.get(symbol)
            return {"symbol":symbol,"price":p.price if p else None,
                    "last_event_at":p.observed_at.astimezone(UTC).isoformat() if p else None,
                    "events":self._count[symbol]}
