from datetime import UTC, datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from services.api.feed import router as feed_router, store

app = FastAPI(title="QuantPro API", version="0.4.0")
app.include_router(feed_router)


class SystemStatus(BaseModel):
    environment: Literal["research", "paper", "live"]
    live_trading_enabled: bool
    markets: list[str]
    phase: str


class EngineState(BaseModel):
    name: str
    status: Literal["ready", "waiting_data", "disabled"]


class MarketState(BaseModel):
    symbol: Literal["NQ", "MNQ", "GC", "MGC"]
    price: float | None = None
    vwap: float | None = None
    poc: float | None = None
    cvd: float | None = None
    dom_imbalance: float | None = None
    feed_status: Literal["offline", "delayed", "realtime"] = "offline"


class TerminalState(BaseModel):
    symbols: list[str]
    decision: Literal["LONG", "SHORT", "WAIT"]
    probability: float | None
    risk_veto: bool
    data_mode: Literal["offline", "delayed", "realtime"]
    markets: list[MarketState]
    engines: list[EngineState]


@app.get("/health", response_model=SystemStatus)
def health() -> SystemStatus:
    return SystemStatus(
        environment="research",
        live_trading_enabled=False,
        markets=["NQ", "MNQ", "GC", "MGC"],
        phase="institutional-v2",
    )


@app.get("/terminal/state", response_model=TerminalState)
def terminal_state() -> TerminalState:
    symbols = ["NQ", "MNQ", "GC", "MGC"]
    snapshots = [store.snapshot(symbol) for symbol in symbols]
    now = datetime.now(UTC)

    def status(snapshot: dict) -> Literal["offline", "delayed", "realtime"]:
        if not snapshot["last_event_at"]:
            return "offline"
        age = (now - datetime.fromisoformat(snapshot["last_event_at"])).total_seconds()
        return "realtime" if age <= 15 else "delayed"

    statuses = [status(snapshot) for snapshot in snapshots]
    mode: Literal["offline", "delayed", "realtime"] = (
        "realtime" if "realtime" in statuses else "delayed" if "delayed" in statuses else "offline"
    )
    return TerminalState(
        symbols=symbols,
        decision="WAIT",
        probability=None,
        risk_veto=True,
        data_mode=mode,
        markets=[
            MarketState(
                symbol=snapshot["symbol"],
                price=snapshot["price"],
                feed_status=current,
            )
            for snapshot, current in zip(snapshots, statuses)
        ],
        engines=[
            EngineState(name="Structure", status="ready"),
            EngineState(name="Order Flow", status="ready"),
            EngineState(name="Liquidity", status="ready"),
            EngineState(name="Regime", status="ready"),
            EngineState(name="Macro/Intermarket", status="waiting_data"),
            EngineState(name="Quant Models", status="waiting_data"),
            EngineState(name="Live Futures Feed", status="waiting_data"),
            EngineState(name="MBO", status="disabled"),
        ],
    )
