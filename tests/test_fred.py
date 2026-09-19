import httpx

from packages.data_engine.fred import FredClient

def test_fred_parser_skips_missing_values():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"observations": [
            {"date": "2026-01-01", "value": "4.25"},
            {"date": "2026-01-02", "value": "."},
        ]})
    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = FredClient("x" * 32, client).observations("DGS10")
    assert len(rows) == 1
    assert rows[0].value == 4.25
