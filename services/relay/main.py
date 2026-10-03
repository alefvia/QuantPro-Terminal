from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from pydantic import BaseModel

app = FastAPI(title="QuantPro Relay", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quant-pro-terminal.vercel.app"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

SYMBOLS = ("NQ", "MNQ", "GC", "MGC")
RELAY_AUDIENCE = os.environ["QUANTPRO_RELAY_AUDIENCE"]
VM_SERVICE_ACCOUNT = os.environ["QUANTPRO_VM_SERVICE_ACCOUNT"]
state: dict[str, dict[str, Any]] = {symbol: {} for symbol in SYMBOLS}

class FeedEvent(BaseModel):
    symbol: str
    kind: str
    observed_at: str
    price: float | None = None
    size: float | None = None
    side: str | None = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def verify_vm_identity(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="missing vm identity")
    try:
        claims = id_token.verify_oauth2_token(authorization[7:], Request(), RELAY_AUDIENCE)
    except Exception as exc:
        raise HTTPException(status_code=403, detail="invalid vm identity") from exc
    if claims.get("email") != VM_SERVICE_ACCOUNT or not claims.get("email_verified"):
        raise HTTPException(status_code=403, detail="unexpected vm identity")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "read-only"}

@app.post("/ingest", status_code=202)
def ingest(event: FeedEvent, authorization: str | None = Header(default=None)) -> dict[str, str]:
    verify_vm_identity(authorization)
    symbol = event.symbol.upper()
    if symbol not in state:
        raise HTTPException(status_code=422, detail="unsupported symbol")
    state[symbol] = event.model_dump() | {"received_at": now_iso()}
    return {"status": "accepted"}

@app.get("/terminal/state")
def terminal_state() -> dict[str, Any]:
    markets = []
    realtime = False
    for symbol in SYMBOLS:
        event = state[symbol]
        status = "realtime" if event else "offline"
        realtime = realtime or status == "realtime"
        markets.append({"symbol": symbol, "price": event.get("price"), "feed_status": status, "last_event": event or None})
    return {
        "symbols": list(SYMBOLS),
        "decision": "WAIT",
        "probability": None,
        "risk_veto": True,
        "data_mode": "realtime" if realtime else "offline",
        "markets": markets,
        "execution": "disabled",
    }
