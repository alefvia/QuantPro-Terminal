from datetime import datetime, timezone
from pathlib import Path

from packages.data_engine.fred import FredClient
from packages.data_engine.manifest import create_manifest, write_manifest
from packages.data_engine.storage import to_frame, write_parquet_atomic

def ingest_fred_series(client: FredClient, series_id: str, root: Path) -> Path:
    observations = client.observations(series_id)
    # FRED observation date and release availability are distinct concepts.
    # Until a point-in-time release timestamp is supplied, available_at is the
    # ingestion timestamp; this prevents pretending data was known earlier.
    ingested_at = datetime.now(timezone.utc)
    rows = [
        {
            "observed_at": o.observed_at,
            "available_at": ingested_at,
            "source": o.source,
            "series": series_id,
            "value": o.value,
        }
        for o in observations
    ]
    frame = to_frame(rows)
    path = root / "processed" / "fred" / f"{series_id}.parquet"
    write_parquet_atomic(frame, path)
    manifest = create_manifest(series_id, "fred", path, frame.height)
    write_manifest(manifest, path.with_suffix(".manifest.json"))
    return path
