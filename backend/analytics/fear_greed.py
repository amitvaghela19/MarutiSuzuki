"""Supply-chain Fear & Greed indices (demo heuristic, 0–100 scale)."""

from __future__ import annotations

import statistics
from typing import Any

from backend.analytics.fear_greed_bulletins import build_fear_greed_bulletins
from backend.config.models import AppConfig
from backend.utils.countries import country_name


def _clamp(v: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, v))


def _sentiment_label(fear: float, greed: float) -> str:
    net = greed - fear
    if net <= -35:
        return "Extreme Fear"
    if net <= -12:
        return "Fear"
    if net <= 12:
        return "Neutral"
    if net <= 35:
        return "Greed"
    return "Extreme Greed"


def _news_pressure_for_country(news: list[dict], country: str) -> float:
    score = 0.0
    for n in news:
        if n.get("country_code") == country:
            score += n.get("severity", 1) * 8
    return _clamp(score)


def _maruti_news_pressure(news: list[dict]) -> float:
    keys = ("maruti", "suzuki", "msil", "passenger vehicle", "automotive india")
    score = 0.0
    for n in news:
        blob = f"{n.get('title', '')} {n.get('summary', '')}".lower()
        if any(k in blob for k in keys):
            score += n.get("severity", 1) * 10
    return _clamp(score)


def _max_stockout(sim_results: list[dict]) -> float:
    if not sim_results:
        return 0.0
    return max(float(r.get("metrics", {}).get("stockout_probability", 0)) for r in sim_results)


def _supplier_part_weights(cfg: AppConfig) -> dict[str, float]:
    weights: dict[str, float] = {s.id: 0.0 for s in cfg.suppliers}
    for part in cfg.parts:
        w = float(part.criticality)
        for sid in part.supplier_ids:
            weights[sid] = weights.get(sid, 0.0) + w
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def _score_supplier_fear_greed(
    supplier: Any,
    supplier_risk: float,
    country_risk: float,
    commodity_risk: float,
    news: list[dict],
    components: dict[str, float] | None = None,
) -> tuple[float, float, list[str]]:
    comp = components or {}
    cr = comp.get("country_risk", country_risk)
    com = comp.get("commodity_risk", commodity_risk)
    lead = comp.get("lead_time", supplier.lead_time_days)

    news_fear = _news_pressure_for_country(news, supplier.country)
    lead_fear = _clamp(lead * 1.1)

    fear = _clamp(0.42 * supplier_risk + 0.22 * cr + 0.18 * com + 0.10 * lead_fear + 0.08 * news_fear)

    cost_greed = _clamp((1.2 - supplier.cost_index) * 55)
    cap = supplier.capability_flags or {}
    cap_bonus = 8.0 if cap.get("ev_ready") else 0.0
    cap_bonus += 6.0 if cap.get("tier1") else 0.0
    stability = _clamp(100 - supplier_risk)
    greed = _clamp(0.38 * stability + 0.28 * cost_greed + 0.20 * (100 - com) + 0.14 * (100 - cr) + cap_bonus)

    drivers: list[str] = []
    if supplier_risk >= 70:
        drivers.append("Elevated composite supplier risk")
    if news_fear >= 40:
        drivers.append(f"Negative news density in {country_name(supplier.country)}")
    if lead >= 25:
        drivers.append("Long lead time increases fear")
    if cost_greed >= 55:
        drivers.append("Cost-competitive positioning supports greed")
    if cap.get("ev_ready"):
        drivers.append("EV-ready capability lifts confidence")

    return fear, greed, drivers


def _baseline_supplier_risk(supplier: Any, country_risk: float, commodity_risk: float) -> float:
    lead_penalty = _clamp(supplier.lead_time_days * 1.2)
    return _clamp(0.4 * country_risk + 0.35 * commodity_risk + 0.25 * lead_penalty)


def build_fear_greed_indices(
    cfg: AppConfig,
    supplier_risks: dict[str, float] | None = None,
    supplier_components: dict[str, dict[str, float]] | None = None,
    country_risks: dict[str, float] | None = None,
    commodity_risks: dict[str, float] | None = None,
    news: list[dict] | None = None,
    sim_results: list[dict] | None = None,
) -> dict[str, Any]:
    news = news or []
    supplier_risks = supplier_risks or {}
    supplier_components = supplier_components or {}
    country_risks = country_risks or {}
    commodity_risks = commodity_risks or {}
    sim_results = sim_results or []

    part_weights = _supplier_part_weights(cfg)
    supplier_rows: list[dict] = []

    for s in cfg.suppliers:
        com_scores = [commodity_risks.get(c, 45.0) for c in s.commodities]
        com_risk = statistics.mean(com_scores) if com_scores else 45.0
        cr = country_risks.get(s.country, 45.0)
        sr = supplier_risks.get(s.id)
        if sr is None:
            sr = _baseline_supplier_risk(s, cr, com_risk)
        fear, greed, drivers = _score_supplier_fear_greed(
            s, sr, cr, com_risk, news, supplier_components.get(s.id)
        )
        supplier_rows.append(
            {
                "id": s.id,
                "name": s.name,
                "country": s.country,
                "country_name": country_name(s.country),
                "fear_index": round(fear, 1),
                "greed_index": round(greed, 1),
                "sentiment_label": _sentiment_label(fear, greed),
                "part_exposure_weight": round(part_weights.get(s.id, 0) * 100, 1),
                "drivers": drivers,
                "reference_url": s.reference_url,
            }
        )

    supplier_rows.sort(key=lambda x: x["fear_index"], reverse=True)

    in_country_risk = country_risks.get("IN", 45.0)
    maruti_news = _maruti_news_pressure(news)
    stockout = _max_stockout(sim_results)

    weighted_fear = sum(
        supplier_risks.get(s.id, _baseline_supplier_risk(s, country_risks.get(s.country, 45.0), 45.0))
        * part_weights.get(s.id, 0)
        for s in cfg.suppliers
    )
    avg_greed = statistics.mean([r["greed_index"] for r in supplier_rows]) if supplier_rows else 50.0

    maruti_fear = _clamp(
        0.35 * weighted_fear
        + 0.25 * in_country_risk
        + 0.20 * maruti_news
        + 0.20 * stockout * 100
    )
    maruti_greed = _clamp(
        0.40 * avg_greed + 0.30 * (100 - maruti_fear) + 0.20 * (100 - stockout * 100) + 0.10 * (100 - in_country_risk)
    )

    maruti_drivers = [
        f"Supplier-network fear (weighted): {weighted_fear:.0f}",
        f"India macro / country risk: {in_country_risk:.0f}",
        f"Auto-sector news pressure: {maruti_news:.0f}",
        f"Simulation stockout stress: {stockout * 100:.0f}%",
    ]

    maruti_ref = getattr(cfg.company, "reference_url", None) if cfg.company else None
    maruti_payload = {
        "id": "MARUTI-SZKI",
        "name": cfg.company.name if cfg.company else "Maruti Suzuki India Limited",
        "ticker": cfg.company.ticker if cfg.company else "NSE MARUTI",
        "fear_index": round(maruti_fear, 1),
        "greed_index": round(maruti_greed, 1),
        "sentiment_label": _sentiment_label(maruti_fear, maruti_greed),
        "drivers": maruti_drivers,
        "reference_url": maruti_ref or "https://www.marutisuzuki.com/",
    }

    return {
        "disclaimer": (
            "Demo Fear & Greed indices derived from configured risks, news severity, and simulation — "
            "not market Fear & Greed or MSIL trading sentiment."
        ),
        "scale_note": "0 = low, 100 = high for each index. Sentiment label compares greed vs fear.",
        "maruti_suzuki": maruti_payload,
        "suppliers": supplier_rows,
        "bulletins": build_fear_greed_bulletins(
            news,
            maruti=maruti_payload,
            suppliers=supplier_rows,
            cfg=cfg,
        ),
    }
