from __future__ import annotations

import os
from collections import deque
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from pydantic import BaseModel

app = FastAPI(title="QuantPro Relay", version="1.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["https://quant-pro-terminal.vercel.app"], allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])

SYMBOLS = ("NQ", "MNQ", "GC", "MGC")
RELAY_AUDIENCE = os.environ["QUANTPRO_RELAY_AUDIENCE"]
VM_SERVICE_ACCOUNT = os.environ["QUANTPRO_VM_SERVICE_ACCOUNT"]
MAX_EVENTS = 25_000
state: dict[str, dict[str, Any]] = {symbol: {} for symbol in SYMBOLS}
events: dict[str, deque[dict[str, Any]]] = {symbol: deque(maxlen=MAX_EVENTS) for symbol in SYMBOLS}
book: dict[str, dict[str, dict[int, dict[str, Any]]]] = {symbol: {"bid": {}, "ask": {}} for symbol in SYMBOLS}

class FeedEvent(BaseModel):
    symbol: str
    kind: str
    observed_at: str
    price: float | None = None
    size: float | None = None
    side: str | None = None
    level: int | None = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def event_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def verify_vm_identity(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="missing vm identity")
    try:
        claims = id_token.verify_oauth2_token(authorization[7:], Request(), RELAY_AUDIENCE)
    except Exception as exc:
        raise HTTPException(status_code=403, detail="invalid vm identity") from exc
    if claims.get("email") != VM_SERVICE_ACCOUNT or not claims.get("email_verified"):
        raise HTTPException(status_code=403, detail="unexpected vm identity")

def candles(symbol: str, seconds: int, limit: int) -> list[dict[str, Any]]:
    buckets: dict[int, dict[str, Any]] = {}
    for event in events[symbol]:
        if event["kind"] != "trade" or event.get("price") is None:
            continue
        stamp = int(event_time(event["observed_at"]).timestamp())
        key = stamp - (stamp % seconds)
        price, size = float(event["price"]), float(event.get("size") or 0)
        candle = buckets.setdefault(key, {"time": key, "open": price, "high": price, "low": price, "close": price, "volume": 0.0, "buy_volume": 0.0, "sell_volume": 0.0})
        candle["high"], candle["low"], candle["close"] = max(candle["high"], price), min(candle["low"], price), price
        candle["volume"] += size
        if event.get("side") == "ask": candle["buy_volume"] += size
        elif event.get("side") == "bid": candle["sell_volume"] += size
    return list(sorted(buckets.values()))[-max(1, min(limit, 800)) :]

def order_book(symbol: str) -> dict[str, list[dict[str, Any]]]:
    levels = book[symbol]
    return {"bids": sorted(levels["bid"].values(), key=lambda row: row["price"], reverse=True)[:10], "asks": sorted(levels["ask"].values(), key=lambda row: row["price"])[:10]}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "read-only"}

@app.post("/ingest", status_code=202)
def ingest(event: FeedEvent, authorization: str | None = Header(default=None)) -> dict[str, str]:
    verify_vm_identity(authorization)
    symbol = event.symbol.upper()
    if symbol not in state: raise HTTPException(status_code=422, detail="unsupported symbol")
    payload = event.model_dump() | {"received_at": now_iso()}
    state[symbol] = payload
    events[symbol].append(payload)
    if event.kind == "depth" and event.side in {"bid", "ask"} and event.level and event.price is not None:
        book[symbol][event.side][event.level] = {"level": event.level, "price": event.price, "size": event.size or 0.0, "observed_at": event.observed_at}
    return {"status": "accepted"}

@app.get("/terminal/chart")
def terminal_chart(symbol: str = "MNQ", timeframe: str = "1m", limit: int = Query(400, ge=1, le=800)) -> dict[str, Any]:
    symbol = symbol.upper()
    if symbol not in events: raise HTTPException(status_code=422, detail="unsupported symbol")
    seconds = {"1m": 60, "5m": 300, "15m": 900}.get(timeframe)
    if seconds is None: raise HTTPException(status_code=422, detail="unsupported timeframe")
    return {"symbol": symbol, "timeframe": timeframe, "candles": candles(symbol, seconds, limit), "source": "rithmic-realtime", "persistence": "memory-window"}

@app.get("/terminal/book")
def terminal_book(symbol: str = "MNQ") -> dict[str, Any]:
    symbol = symbol.upper()
    if symbol not in book: raise HTTPException(status_code=422, detail="unsupported symbol")
    return {"symbol": symbol, "book": order_book(symbol), "source": "rithmic-realtime"}

@app.get("/terminal/state")
def terminal_state() -> dict[str, Any]:
    markets, realtime = [], False
    for symbol in SYMBOLS:
        event, status = state[symbol], "realtime" if state[symbol] else "offline"
        realtime = realtime or status == "realtime"
        markets.append({"symbol": symbol, "price": event.get("price"), "feed_status": status, "last_event": event or None})
    mnq_trades = [event for event in events["MNQ"] if event["kind"] == "trade"]
    cvd = sum((event.get("size") or 0) if event.get("side") == "ask" else -(event.get("size") or 0) if event.get("side") == "bid" else 0 for event in mnq_trades)
    return {"symbols": list(SYMBOLS), "decision": "WAIT", "probability": None, "risk_veto": True, "data_mode": "realtime" if realtime else "offline", "markets": markets, "mnq": {"event_count": len(events["MNQ"]), "trade_count": len(mnq_trades), "cvd": cvd, "book": order_book("MNQ")}, "execution": "disabled"}
