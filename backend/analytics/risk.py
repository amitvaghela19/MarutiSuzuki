import statistics
from typing import Any

from backend.config.models import AppConfig


def _clamp(v: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, v))


def score_countries(cfg: AppConfig, ingest: dict[str, Any], news: list[dict]) -> list[tuple[str, float, dict]]:
    macro = ingest.get("macro", {})
    news_by_country: dict[str, int] = {}
    for n in news:
        cc = n.get("country_code")
        if cc:
            news_by_country[cc] = news_by_country.get(cc, 0) + n.get("severity", 1)

    results = []
    for c in cfg.data_sources.countries:
        ind_data = macro.get(c.code, {})
        vals = []
        for series in ind_data.values():
            if series:
                vals.append(series[0]["value"])
        macro_risk = 50.0
        if vals:
            # higher inflation / volatile GDP -> higher risk
            if len(vals) >= 2 and "FP.CPI" in str(ind_data):
                macro_risk = _clamp(abs(vals[0]) * 8)
            else:
                macro_risk = _clamp(50 + (10 - statistics.mean(vals)) * 3)

        event_density = _clamp(news_by_country.get(c.code, 0) * 12)
        score = _clamp(0.55 * macro_risk + 0.45 * event_density)
        results.append(
            (
                c.code,
                score,
                {"macro_risk": macro_risk, "news_events": news_by_country.get(c.code, 0)},
            )
        )
    return results


def score_commodities(cfg: AppConfig, ingest: dict[str, Any], news: list[dict]) -> list[tuple[str, float, dict]]:
    prices = ingest.get("commodity_prices", {})
    results = []
    for com in cfg.data_sources.commodity_series:
        series = prices.get(com.id, [])
        vol_risk = 30.0
        if len(series) >= 3:
            vals = [p["value"] for p in series[:12]]
            if len(vals) >= 2:
                mean = statistics.mean(vals)
                stdev = statistics.pstdev(vals)
                vol_risk = _clamp((stdev / mean) * 200 if mean else 30)
        news_hits = sum(
            1
            for n in news
            if com.id in (n.get("title", "") + n.get("summary", "")).lower()
            or n.get("risk_type") == "commodity"
        )
        news_risk = _clamp(news_hits * 15)
        score = _clamp(0.6 * vol_risk + 0.4 * news_risk)
        results.append((com.id, score, {"volatility_risk": vol_risk, "news_hits": news_hits}))
    return results


def score_suppliers(
    cfg: AppConfig,
    country_risks: dict[str, float],
    commodity_risks: dict[str, float],
) -> list[tuple[str, float, dict]]:
    results = []
    for s in cfg.suppliers:
        cr = country_risks.get(s.country, 50.0)
        com_scores = [commodity_risks.get(c, 40.0) for c in s.commodities]
        com_risk = statistics.mean(com_scores) if com_scores else 40.0
        lead_penalty = _clamp(s.lead_time_days * 1.2)
        score = _clamp(0.4 * cr + 0.35 * com_risk + 0.25 * lead_penalty)
        results.append(
            (
                s.id,
                score,
                {"country_risk": cr, "commodity_risk": com_risk, "lead_time": s.lead_time_days},
            )
        )
    return results
