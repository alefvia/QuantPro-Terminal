from datetime import datetime

import polars as pl

def as_known_at(frame: pl.DataFrame, timestamp: datetime) -> pl.DataFrame:
    """Return only information that was available by timestamp."""
    return frame.filter(pl.col("available_at") <= timestamp).sort("observed_at")
