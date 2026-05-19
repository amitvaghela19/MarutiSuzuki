import asyncio
import time
from typing import Any

from backend.config.models import AppConfig
from backend.db.repository import Repository
from backend.ingestion.fred_client import fetch_fred
from backend.ingestion.gdelt_client import fetch_gdelt
from backend.ingestion.news_classifier import classify_articles
from backend.ingestion.rss_client import fetch_rss
from backend.ingestion.worldbank_client import fetch_worldbank


async def run_ingestion(cfg: AppConfig, repo: Repository) -> tuple[dict[str, Any], list[dict]]:
    health: dict[str, Any] = {}

    async def _wb():
        t0 = time.perf_counter()
        data, ok = await fetch_worldbank(cfg)
        ms = int((time.perf_counter() - t0) * 1000)
        repo.upsert_health("worldbank", ok=ok, error=None if ok else "using cache/fallback", latency_ms=ms)
        health["worldbank"] = "ok" if ok else "stale"
        return data

    async def _fred():
        t0 = time.perf_counter()
        data, ok, err = await fetch_fred(cfg)
        ms = int((time.perf_counter() - t0) * 1000)
        repo.upsert_health("fred", ok=ok, error=err, latency_ms=ms)
        health["fred"] = "ok" if ok else "stale"
        return data

    async def _rss():
        t0 = time.perf_counter()
        arts, ok = await fetch_rss(cfg)
        ms = int((time.perf_counter() - t0) * 1000)
        repo.upsert_health("rss", ok=ok, error=None if ok else "using cache", latency_ms=ms)
        health["rss"] = "ok" if ok else "stale"
        return arts

    async def _gdelt():
        t0 = time.perf_counter()
        arts, ok = await fetch_gdelt(cfg)
        ms = int((time.perf_counter() - t0) * 1000)
        repo.upsert_health("gdelt", ok=ok, error=None if ok else "using cache/rss only", latency_ms=ms)
        health["gdelt"] = "ok" if ok else "stale"
        return arts

    wb, fred, rss, gdelt = await asyncio.gather(_wb(), _fred(), _rss(), _gdelt())
    all_news = classify_articles(rss + gdelt, cfg)
    return {
        "macro": wb.get("macro", {}),
        "commodity_prices": fred.get("prices", {}),
        "health": health,
    }, all_news
