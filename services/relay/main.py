from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="QuantPro Relay", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quant-pro-terminal.vercel.app"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Quantpro-Token"],
)

TOKEN = os.environ.get("RELAY_INGEST_TOKEN", "")
SYMBOLS = ("NQ", "MNQ", "GC", "MGC")
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "read-only"}


@app.post("/ingest", status_code=202)
def ingest(event: FeedEvent, x_quantpro_token: str | None = Header(default=None)) -> dict[str, str]:
    if not TOKEN or not x_quantpro_token or not hmac.compare_digest(x_quantpro_token, TOKEN):
        raise HTTPException(status_code=403, detail="unauthorized")
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
