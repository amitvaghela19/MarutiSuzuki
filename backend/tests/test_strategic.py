import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.utils.strategic import normalize_strategic_payload


def test_normalize_cited_bullets():
    raw = {
        "maruti_suzuki": {
            "swot": {
                "strengths": [
                    {"text": "A point", "source_url": "https://example.com", "source_label": "Ex"},
                ]
            },
            "pestle": {},
        },
        "partners": [],
    }
    out = normalize_strategic_payload(raw)
    s = out["maruti_suzuki"]["swot"]["strengths"][0]
    assert s["text"] == "A point"
    assert s["source_url"] == "https://example.com"


@pytest.mark.asyncio
async def test_strategic_api_returns_urls():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/company/strategic")
        assert r.status_code == 200
        body = r.json()
        first = body["maruti_suzuki"]["swot"]["strengths"][0]
        assert first.get("source_url", "").startswith("http")
