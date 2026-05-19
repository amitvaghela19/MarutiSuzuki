import pytest
from httpx import ASGITransport, AsyncClient

from backend.config.loader import load_config
from backend.main import app


def test_supplier_count_expanded():
    cfg = load_config()
    assert len(cfg.suppliers) >= 30
    indiamart = [s for s in cfg.suppliers if s.trust_tier == "indiamart_verified"]
    assert len(indiamart) >= 10
    assert all(s.reference_url for s in indiamart)


@pytest.mark.asyncio
async def test_suppliers_catalog_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/suppliers/catalog")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] >= 30
        assert "trust_tiers" in body
        assert body["suppliers"][0].get("reference_url") or body["suppliers"][0].get("trust_tier")
