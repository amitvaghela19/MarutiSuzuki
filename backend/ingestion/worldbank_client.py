import time
from typing import Any

import httpx

from backend.config.models import AppConfig
from backend.ingestion.cache import read_latest_cache, write_cache


async def fetch_worldbank(cfg: AppConfig) -> tuple[dict[str, Any], bool]:
    """Returns macro data by country/indicator and whether fetch succeeded."""
    indicators = cfg.data_sources.worldbank_indicators
    countries = [c.code for c in cfg.data_sources.countries]
    if not indicators:
        return {"macro": {}}, True

    macro: dict[str, dict[str, list[dict]]] = {}
    base = "https://api.worldbank.org/v2/country"
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for country in countries:
                macro[country] = {}
                for ind in indicators:
                    url = f"{base}/{country}/indicator/{ind.id}"
                    r = await client.get(url, params={"format": "json", "per_page": 10})
                    r.raise_for_status()
                    payload = r.json()
                    if len(payload) < 2:
                        continue
                    series = []
                    for row in payload[1]:
                        if row.get("value") is not None:
                            series.append(
                                {
                                    "year": int(row["date"]),
                                    "value": float(row["value"]),
                                    "indicator": ind.id,
                                }
                            )
                    macro[country][ind.id] = series
        write_cache("worldbank", {"macro": macro})
        return {"macro": macro}, True
    except Exception:
        cached = read_latest_cache("worldbank")
        if cached:
            return cached, False
        # deterministic demo fallback
        fallback = _demo_macro(countries, indicators)
        write_cache("worldbank", fallback)
        return fallback, False


def _demo_macro(countries: list[str], indicators: list) -> dict:
    macro: dict[str, dict[str, list[dict]]] = {}
    seeds = {"IN": 6.5, "TH": 3.2, "MY": 4.1, "JP": 1.0, "DE": 0.5}
    for c in countries:
        macro[c] = {}
        for ind in indicators:
            base = seeds.get(c, 2.0)
            macro[c][ind.id] = [
                {"year": 2022, "value": base, "indicator": ind.id},
                {"year": 2023, "value": base * 0.95, "indicator": ind.id},
            ]
    return {"macro": macro}
