from datetime import UTC, datetime

import httpx

from packages.data_engine.contracts import MarketObservation

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

class FredClient:
    def __init__(self, api_key: str, client: httpx.Client | None = None):
        if not api_key:
            raise ValueError("FRED_API_KEY is required")
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=30.0)

    def observations(self, series_id: str, observation_start: str = "2000-01-01") -> list[MarketObservation]:
        response = self.client.get(
            FRED_URL,
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": observation_start,
                "sort_order": "asc",
            },
        )
        response.raise_for_status()
        rows = []
        for item in response.json()["observations"]:
            if item["value"] == ".":
                continue
            observed_at = datetime.fromisoformat(item["date"]).replace(tzinfo=UTC)
            rows.append(MarketObservation(series_id, observed_at, "fred", float(item["value"]), "value"))
        return rows
