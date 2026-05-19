import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx

from backend.config.models import AppConfig
from backend.ingestion.cache import read_latest_cache, write_cache


async def fetch_gdelt(cfg: AppConfig) -> tuple[list[dict], bool]:
    queries = cfg.data_sources.gdelt_queries[:3]
    articles: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            for q in queries:
                r = await client.get(
                    "https://api.gdeltproject.org/api/v2/doc/doc",
                    params={
                        "query": q,
                        "mode": "ArtList",
                        "maxrecords": 10,
                        "format": "json",
                    },
                )
                if r.status_code != 200:
                    continue
                data = r.json()
                for art in data.get("articles", []):
                    articles.append(
                        {
                            "id": str(uuid4()),
                            "source": "gdelt",
                            "title": art.get("title", ""),
                            "url": art.get("url", ""),
                            "published_at": art.get("seendate"),
                            "summary": art.get("title", ""),
                            "query": q,
                        }
                    )
        if articles:
            write_cache("gdelt", {"articles": articles})
            return articles, True
        raise ValueError("No GDELT articles returned")
    except Exception:
        cached = read_latest_cache("gdelt")
        if cached:
            return cached.get("articles", []), False
        return [], False
