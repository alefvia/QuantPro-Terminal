from fastapi.testclient import TestClient
from services.api.main import app
client=TestClient(app)

def test_health_is_research_and_live_disabled():
    p=client.get("/health").json()
    assert p["environment"]=="research"
    assert p["live_trading_enabled"] is False
    assert p["markets"]==["NQ","MNQ","GC","MGC"]

def test_terminal_fails_closed_without_feed():
    p=client.get("/terminal/state").json()
    assert p["decision"]=="WAIT"
    assert p["probability"] is None
    assert p["risk_veto"] is True
    assert p["data_mode"]=="offline"
    assert all(m["price"] is None for m in p["markets"])
