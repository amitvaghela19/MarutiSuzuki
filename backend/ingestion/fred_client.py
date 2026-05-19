import time
from typing import Any

import httpx

from backend.config.models import AppConfig
from backend.ingestion.cache import read_latest_cache, write_cache
from backend.settings import settings


async def fetch_fred(cfg: AppConfig) -> tuple[dict[str, Any], bool, str | None]:
    if not settings.fred_api_key:
        cached = read_latest_cache("fred")
        if cached:
            return cached, False, "FRED_API_KEY not set; using cache"
        data = _demo_commodity_prices(cfg)
        write_cache("fred", data)
        return data, False, "FRED_API_KEY not set; using demo series"

    series_map = {
        c.id: c.fred_series for c in cfg.data_sources.commodity_series if c.fred_series
    }
    prices: dict[str, list[dict]] = {}
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for cid, sid in series_map.items():
                url = "https://api.stlouisfed.org/fred/series/observations"
                r = await client.get(
                    url,
                    params={
                        "series_id": sid,
                        "api_key": settings.fred_api_key,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 24,
                    },
                )
                r.raise_for_status()
                obs = r.json().get("observations", [])
                prices[cid] = [
                    {"date": o["date"], "value": float(o["value"])}
                    for o in obs
                    if o.get("value") not in (".", None)
                ]
        data = {"prices": prices}
        write_cache("fred", data)
        return data, True, None
    except Exception as e:
        cached = read_latest_cache("fred")
        if cached:
            return cached, False, str(e)
        data = _demo_commodity_prices(cfg)
        write_cache("fred", data)
        return data, False, str(e)


def _demo_commodity_prices(cfg: AppConfig) -> dict:
    prices = {}
    base_vals = {
        "rubber": 1.2,
        "metals": 250.0,
        "electronics": 180.0,
        "semiconductors": 195.0,
        "batteries": 140.0,
        "plastics": 120.0,
        "tires": 1.3,
    }
    for c in cfg.data_sources.commodity_series:
        b = base_vals.get(c.id, 100.0)
        prices[c.id] = [
            {"date": f"2024-{m:02d}-01", "value": b * (1 + 0.02 * (m - 6))}
            for m in range(1, 13)
        ]
    return {"prices": prices}
