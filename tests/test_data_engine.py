from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from packages.data_engine.point_in_time import as_known_at
from packages.data_engine.quality import validate_observation
from packages.data_engine.storage import read_parquet, to_frame, write_parquet_atomic

def test_quality_rejects_naive_timestamp():
    result = validate_observation(observed_at=datetime(2026, 1, 1), value=1.0)
    assert result.ok is False

def test_point_in_time_hides_future_information():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    frame = pl.DataFrame({
        "observed_at": [now, now],
        "available_at": [now, now + timedelta(days=1)],
        "source": ["test", "test"],
        "series": ["x", "x"],
        "value": [1.0, 2.0],
    })
    visible = as_known_at(frame, now)
    assert visible.height == 1
    assert visible["value"][0] == 1.0

def test_parquet_round_trip(tmp_path: Path):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    frame = to_frame([{
        "observed_at": now,
        "available_at": now,
        "source": "test",
        "series": "x",
        "value": 42.0,
    }])
    path = tmp_path / "x.parquet"
    write_parquet_atomic(frame, path)
    loaded = read_parquet(path)
    assert loaded.height == 1
    assert loaded["value"][0] == 42.0
