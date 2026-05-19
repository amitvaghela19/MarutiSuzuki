import pytest
from httpx import ASGITransport, AsyncClient

from backend.analytics.fear_greed import build_fear_greed_indices
from backend.config.loader import load_config
from backend.main import app


def test_fear_greed_maruti_and_suppliers():
    cfg = load_config()
    out = build_fear_greed_indices(cfg)
    assert out["maruti_suzuki"]["fear_index"] >= 0
    assert out["maruti_suzuki"]["greed_index"] >= 0
    assert len(out["suppliers"]) == len(cfg.suppliers)
    for row in out["suppliers"]:
        assert 0 <= row["fear_index"] <= 100
        assert 0 <= row["greed_index"] <= 100
        assert row["sentiment_label"]


@pytest.mark.asyncio
async def test_fear_greed_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/sentiment/fear-greed")
        assert r.status_code == 200
        body = r.json()
        assert "maruti_suzuki" in body
        assert len(body["suppliers"]) > 0
