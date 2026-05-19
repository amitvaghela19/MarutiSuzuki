from fastapi.testclient import TestClient

from backend.config.loader import load_config
from backend.main import app


def test_parts_count_merged():
    cfg = load_config()
    assert len(cfg.parts) >= 80


def test_enriched_catalog_endpoint():
    client = TestClient(app)
    r = client.get("/api/parts/catalog/enriched")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 80
    first = data["parts"][0]
    assert "suppliers" in first
    assert "why_summary" in first


def test_suppliers_strategic_endpoint():
    client = TestClient(app)
    r = client.get("/api/suppliers/strategic")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 30
    assert "swot" in data["suppliers"][0]
