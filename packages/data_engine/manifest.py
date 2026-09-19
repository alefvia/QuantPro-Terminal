from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

@dataclass(frozen=True)
class DatasetManifest:
    dataset: str
    source: str
    generated_at: str
    sha256: str
    rows: int

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def create_manifest(dataset: str, source: str, data_path: Path, rows: int) -> DatasetManifest:
    return DatasetManifest(dataset, source, datetime.now(UTC).isoformat(), sha256_file(data_path), rows)

def write_manifest(manifest: DatasetManifest, path: Path) -> None:
    path.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
