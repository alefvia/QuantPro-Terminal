from dataclasses import dataclass
from datetime import date

import httpx

@dataclass(frozen=True)
class CotRecord:
    market: str
    report_date: date
    payload: dict

class CftcClient:
    """Thin adapter over CFTC public-data endpoints.

    Dataset identifiers/endpoints are configuration, not trading logic, so the
    adapter can follow CFTC schema changes without changing downstream engines.
    """

    def __init__(self, endpoint: str, client: httpx.Client | None = None):
        self.endpoint = endpoint
        self.client = client or httpx.Client(timeout=30.0)

    def fetch(self, *, market_code: str, limit: int = 5000) -> list[dict]:
        response = self.client.get(
            self.endpoint,
            params={"$limit": limit, "$order": "report_date_as_yyyy_mm_dd ASC", "cftc_contract_market_code": market_code},
        )
        response.raise_for_status()
        return response.json()
