from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="QuantPro API", version="0.1.0")

class SystemStatus(BaseModel):
    environment: Literal["research", "paper", "live"]
    live_trading_enabled: bool
    markets: list[str]
    phase: str

@app.get("/health", response_model=SystemStatus)
def health() -> SystemStatus:
    return SystemStatus(
        environment="research",
        live_trading_enabled=False,
        markets=["NQ", "MNQ", "GC", "MGC"],
        phase="F0-foundation",
    )
