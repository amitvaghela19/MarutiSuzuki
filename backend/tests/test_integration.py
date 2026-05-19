import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_run_analysis_and_snapshot():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=120.0) as client:
        r = await client.post("/api/run-analysis")
        assert r.status_code == 200
        body = r.json()
        assert "run_id" in body
        assert "recommendations" in body
        snap = await client.get("/api/snapshot/latest")
        assert snap.status_code == 200
        assert snap.json()["run_id"] == body["run_id"]
