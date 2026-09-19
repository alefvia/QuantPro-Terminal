import argparse
import os
from pathlib import Path

from packages.data_engine.fred import FredClient
from packages.data_engine.pipeline import ingest_fred_series

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("series_id")
    parser.add_argument("--root", default="data")
    args = parser.parse_args()
    client = FredClient(os.environ["FRED_API_KEY"])
    path = ingest_fred_series(client, args.series_id, Path(args.root))
    print(path)

if __name__ == "__main__":
    main()
