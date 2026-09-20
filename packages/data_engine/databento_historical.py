from dataclasses import dataclass
from datetime import datetime
import os

@dataclass(frozen=True)
class HistoricalRequest:
    symbols: tuple[str, ...]
    start: datetime
    end: datetime
    schema: str = "ohlcv-1m"
    dataset: str = "GLBX.MDP3"
    stype_in: str = "continuous"

DEFAULT_SYMBOLS=("NQ.v.0","MNQ.v.0","GC.v.0","MGC.v.0")

def load_history(request: HistoricalRequest):
    try:
        import databento as db
    except ImportError as exc:
        raise RuntimeError("Install the optional databento package") from exc
    key=os.getenv("DATABENTO_API_KEY")
    if not key:
        raise RuntimeError("DATABENTO_API_KEY is required")
    if request.end <= request.start:
        raise ValueError("end must be after start")
    client=db.Historical(key)
    return client.timeseries.get_range(
        dataset=request.dataset,
        schema=request.schema,
        stype_in=request.stype_in,
        symbols=list(request.symbols),
        start=request.start.isoformat(),
        end=request.end.isoformat(),
    )
