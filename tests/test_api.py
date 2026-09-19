from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_health_is_research_and_live_disabled():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["environment"] == "research"
    assert payload["live_trading_enabled"] is False
    assert payload["markets"] == ["NQ", "MNQ", "GC", "MGC"]
