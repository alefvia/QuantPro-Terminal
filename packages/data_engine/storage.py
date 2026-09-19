from pathlib import Path

import polars as pl

CANONICAL_COLUMNS = ["observed_at", "available_at", "source", "series", "value"]

def to_frame(rows: list[dict]) -> pl.DataFrame:
    frame = pl.DataFrame(rows)
    missing = set(CANONICAL_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing canonical columns: {sorted(missing)}")
    return frame.select(CANONICAL_COLUMNS).sort("observed_at")

def write_parquet_atomic(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    frame.write_parquet(tmp)
    tmp.replace(path)

def read_parquet(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)
