import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import feedparser

from backend.config.models import AppConfig
from backend.ingestion.cache import read_latest_cache, write_cache


async def fetch_rss(cfg: AppConfig) -> tuple[list[dict], bool]:
    feeds = cfg.data_sources.rss_feeds
    articles: list[dict] = []
    try:
        for url in feeds:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:15]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                articles.append(
                    {
                        "id": str(uuid4()),
                        "source": "rss",
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published_at": published.isoformat() if published else None,
                        "summary": entry.get("summary", "")[:500],
                    }
                )
        write_cache("rss", {"articles": articles})
        return articles, True
    except Exception:
        cached = read_latest_cache("rss")
        if cached:
            return cached.get("articles", []), False
        return _demo_articles(), False


def _demo_articles() -> list[dict]:
    return [
        {
            "id": "demo-1",
            "source": "rss",
            "title": "Port delays affect automotive parts shipments",
            "url": "",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "summary": "Logistics strike causes rubber and metal component delays.",
        }
    ]
