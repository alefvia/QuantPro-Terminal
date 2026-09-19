from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="QuantPro API", version="0.2.0")

class SystemStatus(BaseModel):
    environment: Literal["research", "paper", "live"]
    live_trading_enabled: bool
    markets: list[str]
    phase: str

class EngineState(BaseModel):
    name: str
    status: Literal["ready", "waiting_data", "disabled"]

class TerminalState(BaseModel):
    symbols: list[str]
    decision: Literal["LONG", "SHORT", "WAIT"]
    probability_available: bool
    data_mode: Literal["offline", "delayed", "realtime"]
    engines: list[EngineState]

@app.get("/health", response_model=SystemStatus)
def health() -> SystemStatus:
    return SystemStatus(environment="research",live_trading_enabled=False,markets=["NQ","MNQ","GC","MGC"],phase="F3-F4")

@app.get("/terminal/state", response_model=TerminalState)
def terminal_state() -> TerminalState:
    return TerminalState(
        symbols=["NQ","MNQ","GC","MGC"],
        decision="WAIT",
        probability_available=False,
        data_mode="offline",
        engines=[
            EngineState(name="Structure",status="ready"),
            EngineState(name="VWAP",status="ready"),
            EngineState(name="Volume Profile",status="ready"),
            EngineState(name="ATR/Volatility",status="ready"),
            EngineState(name="Live Futures Feed",status="waiting_data"),
            EngineState(name="Order Flow",status="waiting_data"),
            EngineState(name="MBO",status="disabled"),
        ],
    )
