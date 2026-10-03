"""Normalize Databento OHLCV downloads for the QuantPro chart.

The Databento parent-symbol download intentionally contains nearby expiries and
spreads.  A chart must never interleave those instruments minute-by-minute:
that would manufacture rollover jumps.  This module picks one outright
contract per trading date, based on that date's traded volume.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


MONTH_CODES = "FGHJKMNQUVXZ"


def load_continuous_ohlcv(path: str | Path, parent_symbol: str = "MNQ") -> list[dict[str, Any]]:
    """Return one real OHLCV-1m series, selecting the daily liquid expiry.

    ``path`` is a local ``.dbn`` or ``.dbn.zst`` file downloaded by the
    account owner.  The optional Databento reader is deliberately imported at
    run time so the relay itself does not require it to serve live Rithmic
    events.
    """
    try:
        import databento as db
    except ImportError as exc:  # pragma: no cover - deployment dependency
        raise RuntimeError("Install the optional databento package to import history") from exc

    parent = parent_symbol.upper()
    pattern = re.compile(rf"{re.escape(parent)}[{MONTH_CODES}]\d$")
    frame = db.DBNStore.from_file(Path(path)).to_df().reset_index()
    frame = frame[frame["symbol"].astype(str).map(lambda value: bool(pattern.fullmatch(value)))].copy()
    if frame.empty:
        raise ValueError(f"No outright {parent} contracts found in DBN file")

    # Pick one dominant expiry for the whole trading date.  The join retains
    # only its real candles and excludes calendar spreads.
    frame["trading_date"] = frame["ts_event"].dt.date
    daily = frame.groupby(["trading_date", "symbol"], as_index=False)["volume"].sum()
    selected = daily.loc[daily.groupby("trading_date")["volume"].idxmax(), ["trading_date", "symbol"]]
    frame = frame.merge(selected, on=["trading_date", "symbol"], how="inner").sort_values("ts_event")

    candles: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False):
        candles.append(
            {
                "time": int(row.ts_event.timestamp()),
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(row.volume),
                "source_symbol": str(row.symbol),
            }
        )
    return candles
