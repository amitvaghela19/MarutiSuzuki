import pytest
from httpx import ASGITransport, AsyncClient

from backend.analytics.sourcing import build_sourcing_matrix
from backend.config.loader import load_config
from backend.main import app


def test_sourcing_matrix_has_primary_and_alternates():
    cfg = load_config()
    matrix = build_sourcing_matrix(cfg)
    assert matrix["parts"]
    assert len(matrix["parts"]) == len(cfg.parts)
    brake = next(p for p in matrix["parts"] if p["part_id"] == "PART-BRAKE-PAD")
    assert brake["primary_supplier"]["id"] == "SUP-IN-FRICTION"
    assert len(brake["alternate_suppliers"]) >= 1
    assert len(brake["alternative_solutions"]) >= 2


@pytest.mark.asyncio
async def test_sourcing_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/sourcing/matrix")
        assert r.status_code == 200
        data = r.json()
        assert "parts" in data
        assert "suppliers_index" in data
