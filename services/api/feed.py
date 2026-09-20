import os
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from packages.data_engine.live_state import FeedPacket,MarketStateStore

router=APIRouter(prefix="/feed",tags=["feed"])
store=MarketStateStore()

class PacketIn(BaseModel):
    symbol:str
    kind:str
    observed_at:datetime
    price:float
    size:float
    side:str|None=None

def _authorized(token:str|None)->bool:
    expected=os.getenv("QUANTPRO_INGEST_TOKEN")
    return bool(expected) and token==expected

@router.post("/ingest")
def ingest(body:PacketIn,x_quantpro_token:str|None=Header(default=None)):
    if not _authorized(x_quantpro_token):
        raise HTTPException(status_code=401,detail="feed ingest locked")
    try:
        p=FeedPacket(symbol=body.symbol,kind=body.kind,observed_at=body.observed_at,
                     price=body.price,size=body.size,side=body.side)
        store.ingest(p)
    except (ValueError,TypeError) as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"accepted":True,"symbol":body.symbol}

@router.get("/status")
def status():
    return {"markets":[store.snapshot(s) for s in ("NQ","MNQ","GC","MGC")],
            "ingest_configured":bool(os.getenv("QUANTPRO_INGEST_TOKEN"))}
