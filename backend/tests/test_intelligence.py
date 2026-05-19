from fastapi.testclient import TestClient

from backend.main import app


def test_ai_models_endpoint():
    client = TestClient(app)
    r = client.get("/api/ai/models")
    assert r.status_code == 200
    data = r.json()
    assert "models" in data
    assert len(data["models"]) >= 6
    assert "summary" in data
    first = data["models"][0]
    assert "report" in first
    assert first["report"]["headline"]
    assert len(first["report"]["sections"]) >= 3
    facts = next(s for s in first["report"]["sections"] if s["title"] == "Facts from this run")
    assert facts.get("bullets")
    msil = next(s for s in first["report"]["sections"] if "Maruti Suzuki" in s["title"])
    assert "Maruti Suzuki" in msil["body"]


def test_digital_twin_endpoint():
    client = TestClient(app)
    r = client.get("/api/digital-twin/status")
    assert r.status_code == 200
    data = r.json()
    assert "plants" in data
    assert len(data["plants"]) >= 2


def test_command_signals_endpoint():
    client = TestClient(app)
    r = client.get("/api/command/signals")
    assert r.status_code == 200
    assert "signals" in r.json()


def test_disruptions_history_route():
    client = TestClient(app)
    r = client.get("/api/disruptions/history")
    assert r.status_code == 200
    assert r.json()["incidents"]
