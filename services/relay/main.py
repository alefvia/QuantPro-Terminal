from __future__ import annotations

import os
import secrets
import sqlite3
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
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
HISTORY_IMPORT_TOKEN = os.getenv("QUANTPRO_HISTORY_IMPORT_TOKEN")
MAX_EVENTS = 25_000
DB_PATH = os.getenv("QUANTPRO_DB_PATH", "/tmp/quantpro_relay.sqlite3")
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


class HistoricalCandle(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    source_symbol: str


class HistoricalImport(BaseModel):
    symbol: str
    source: str
    candles: list[HistoricalCandle]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def event_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def db() -> sqlite3.Connection:
    """Open the relay event store.

    Set QUANTPRO_DB_PATH to a mounted persistent disk on Render. The default
    deliberately remains local/ephemeral for development, rather than
    claiming that an unmounted Render filesystem is durable.
    """
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_store() -> None:
    with db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                kind TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                received_at TEXT NOT NULL,
                price REAL,
                size REAL,
                side TEXT,
                level INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_market_events_symbol_time
                ON market_events(symbol, observed_at DESC);
            CREATE INDEX IF NOT EXISTS idx_market_events_symbol_kind_time
                ON market_events(symbol, kind, observed_at DESC);
            CREATE TABLE IF NOT EXISTS historical_candles (
                symbol TEXT NOT NULL,
                time INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                source_symbol TEXT NOT NULL,
                source TEXT NOT NULL,
                PRIMARY KEY (symbol, time)
            );
            """
        )


@app.on_event("startup")
def restore_relay_state() -> None:
    initialize_store()
    # The last live values make a restart transparent when the disk is mounted.
    with db() as connection:
        for symbol in SYMBOLS:
            rows = connection.execute(
                "SELECT symbol, kind, observed_at, received_at, price, size, side, level "
                "FROM market_events WHERE symbol = ? ORDER BY id DESC LIMIT ?",
                (symbol, MAX_EVENTS),
            ).fetchall()
            for row in reversed(rows):
                apply_event(dict(row), persist=False)


def persist_event(payload: dict[str, Any]) -> None:
    with db() as connection:
        connection.execute(
            "INSERT INTO market_events (symbol, kind, observed_at, received_at, price, size, side, level) "
            "VALUES (:symbol, :kind, :observed_at, :received_at, :price, :size, :side, :level)",
            payload,
        )


def history_events(symbol: str, limit: int = 100_000) -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute(
            "SELECT symbol, kind, observed_at, received_at, price, size, side, level "
            "FROM market_events WHERE symbol = ? ORDER BY id DESC LIMIT ?",
            (symbol, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def history_candles(symbol: str) -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute(
            "SELECT time, open, high, low, close, volume, source_symbol "
            "FROM historical_candles WHERE symbol = ? ORDER BY time",
            (symbol,),
        ).fetchall()
    return [dict(row) | {"buy_volume": 0.0, "sell_volume": 0.0} for row in rows]


def apply_event(payload: dict[str, Any], persist: bool = True) -> None:
    symbol = payload["symbol"]
    state[symbol] = payload
    events[symbol].append(payload)
    if payload["kind"] == "depth" and payload.get("side") in {"bid", "ask"} and payload.get("level") and payload.get("price") is not None:
        book[symbol][payload["side"]][int(payload["level"])] = {
            "level": int(payload["level"]),
            "price": payload["price"],
            "size": payload.get("size") or 0.0,
            "observed_at": payload["observed_at"],
        }
    if persist:
        persist_event(payload)

def verify_vm_identity(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="missing vm identity")
    try:
        claims = id_token.verify_oauth2_token(authorization[7:], Request(), RELAY_AUDIENCE)
    except Exception as exc:
        raise HTTPException(status_code=403, detail="invalid vm identity") from exc
    if claims.get("email") != VM_SERVICE_ACCOUNT or not claims.get("email_verified"):
        raise HTTPException(status_code=403, detail="unexpected vm identity")


def verify_history_import(token: str | None) -> None:
    if not HISTORY_IMPORT_TOKEN or not token or not secrets.compare_digest(token, HISTORY_IMPORT_TOKEN):
        raise HTTPException(status_code=403, detail="invalid history import token")

def candles(symbol: str, seconds: int, limit: int) -> list[dict[str, Any]]:
    buckets: dict[int, dict[str, Any]] = {}
    for event in history_candles(symbol):
        stamp = int(event["time"])
        key = stamp - (stamp % seconds)
        candle = buckets.setdefault(key, {"time": key, "open": event["open"], "high": event["high"], "low": event["low"], "close": event["close"], "volume": 0.0, "buy_volume": 0.0, "sell_volume": 0.0})
        candle["high"], candle["low"], candle["close"] = max(candle["high"], event["high"]), min(candle["low"], event["low"]), event["close"]
        candle["volume"] += event["volume"]
    for event in history_events(symbol):
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
    return sorted(buckets.values(), key=lambda candle: candle["time"])[-max(1, min(limit, 800)) :]

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
    apply_event(payload)
    return {"status": "accepted"}


@app.post("/terminal/import/ohlcv", status_code=202)
def import_ohlcv(payload: HistoricalImport, x_quantpro_history_token: str | None = Header(default=None)) -> dict[str, Any]:
    verify_history_import(x_quantpro_history_token)
    symbol = payload.symbol.upper()
    if symbol not in SYMBOLS:
        raise HTTPException(status_code=422, detail="unsupported symbol")
    if not payload.candles or len(payload.candles) > 4_000:
        raise HTTPException(status_code=422, detail="send between 1 and 4000 candles per request")
    rows = [
        (symbol, candle.time, candle.open, candle.high, candle.low, candle.close, candle.volume, candle.source_symbol, payload.source)
        for candle in payload.candles
    ]
    with db() as connection:
        connection.executemany(
            "INSERT OR REPLACE INTO historical_candles "
            "(symbol, time, open, high, low, close, volume, source_symbol, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
    return {"status": "accepted", "symbol": symbol, "imported": len(rows)}

@app.get("/terminal/chart")
def terminal_chart(symbol: str = "MNQ", timeframe: str = "1m", limit: int = Query(400, ge=1, le=800)) -> dict[str, Any]:
    symbol = symbol.upper()
    if symbol not in events: raise HTTPException(status_code=422, detail="unsupported symbol")
    seconds = {"1m": 60, "5m": 300, "15m": 900}.get(timeframe)
    if seconds is None: raise HTTPException(status_code=422, detail="unsupported timeframe")
    return {"symbol": symbol, "timeframe": timeframe, "candles": candles(symbol, seconds, limit), "source": "rithmic-realtime", "persistence": "sqlite-mounted-disk" if DB_PATH.startswith("/var/data/") else "sqlite-ephemeral"}


@app.get("/terminal/history")
def terminal_history(symbol: str = "MNQ") -> dict[str, Any]:
    symbol = symbol.upper()
    if symbol not in events:
        raise HTTPException(status_code=422, detail="unsupported symbol")
    with db() as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS event_count, MIN(observed_at) AS first_event, MAX(observed_at) AS last_event "
            "FROM market_events WHERE symbol = ?",
            (symbol,),
        ).fetchone()
    return {"symbol": symbol, **dict(row), "db_path": DB_PATH, "durable": DB_PATH.startswith("/var/data/")}

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
