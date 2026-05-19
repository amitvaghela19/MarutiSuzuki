"""Live tyre / MRF / Gulf disruption brief for command center and parts catalog."""

from __future__ import annotations

from typing import Any

from backend.analytics.disruption_history import GULF_SCENARIO_ID, TIRE_PART_ID

GULF_COUNTRIES = ("AE", "SA")
TIRE_SUPPLIER_IDS = ("SUP-IN-TIRE", "SUP-AE-GULF-CHEM", "SUP-SA-CARBON")


def _gulf_news_hits(news: list[dict]) -> list[dict]:
    keys = (
        "red sea",
        "gulf",
        "middle east",
        "mrf",
        "tyre",
        "tire",
        "synthetic rubber",
        "carbon black",
        "petrochemical",
    )
    out: list[dict] = []
    for n in news:
        blob = f"{n.get('title', '')} {n.get('summary', '')}".lower()
        if any(k in blob for k in keys):
            out.append(n)
    return out[:5]


def build_tire_disruption_brief(
    cfg: Any,
    *,
    supplier_risks: dict[str, float] | None = None,
    country_risks: dict[str, float] | None = None,
    news: list[dict] | None = None,
    sim_results: list[dict] | None = None,
) -> dict[str, Any]:
    supplier_risks = supplier_risks or {}
    country_risks = country_risks or {}
    news = news or []

    part = next((p for p in cfg.parts if p.id == TIRE_PART_ID), None)
    mrf = next((s for s in cfg.suppliers if s.id == "SUP-IN-TIRE"), None)
    gulf_suppliers = [s for s in cfg.suppliers if s.id in ("SUP-AE-GULF-CHEM", "SUP-SA-CARBON")]

    mrf_score = supplier_risks.get("SUP-IN-TIRE", 0)
    gulf_scores = {s.id: supplier_risks.get(s.id, 0) for s in gulf_suppliers}
    country_ae = country_risks.get("AE", 0)
    country_sa = country_risks.get("SA", 0)

    gulf_sim: dict | None = None
    rubber_sim: dict | None = None
    if sim_results:
        for r in sim_results:
            sid = r.get("scenario_id")
            if sid == GULF_SCENARIO_ID:
                gulf_sim = r
            elif sid == "RUBBER-SHOCK":
                rubber_sim = r

    news_hits = _gulf_news_hits(news)
    stress_level = "low"
    if mrf_score >= 65 or max(gulf_scores.values(), default=0) >= 60:
        stress_level = "high"
    elif mrf_score >= 50 or country_ae >= 50 or country_sa >= 50 or news_hits:
        stress_level = "elevated"
    if gulf_sim:
        p = (gulf_sim.get("metrics") or {}).get("stockout_probability", 0)
        if p >= 0.35:
            stress_level = "high"

    bullets: list[str] = []
    if mrf:
        bullets.append(
            f"Primary OEM tyre partner in demo: {mrf.name} (India) — risk score {mrf_score:.0f}/100."
        )
    if gulf_suppliers:
        bullets.append(
            "Tier-2 feedstock modeled via UAE / Saudi petrochemical corridors (synthetic rubber, carbon black)."
        )
    if country_ae or country_sa:
        bullets.append(
            f"Gulf country exposure: UAE {country_ae:.0f}, Saudi Arabia {country_sa:.0f} (risk index)."
        )
    if gulf_sim:
        p = (gulf_sim.get("metrics") or {}).get("stockout_probability", 0)
        bullets.append(
            f"Scenario “{gulf_sim.get('scenario_name', GULF_SCENARIO_ID)}”: "
            f"stockout probability {p:.0%} in latest simulation."
        )
    elif rubber_sim:
        p = (rubber_sim.get("metrics") or {}).get("stockout_probability", 0)
        bullets.append(
            f"ASEAN rubber shock scenario stockout probability {p:.0%} — alternate lane to watch."
        )
    if news_hits:
        bullets.append(f"{len(news_hits)} recent headline(s) mention Gulf / tyre / rubber themes.")

    return {
        "disclaimer": (
            "Synthetic demo aligned to real-world themes (MRF-class OEM tyres, Gulf feedstock routes). "
            "Not a live crisis forecast unless news ingest scores it."
        ),
        "part_id": TIRE_PART_ID,
        "part_name": part.name if part else "OEM tire set",
        "stress_level": stress_level,
        "headline": (
            "MRF / Gulf tyre supply watch"
            if stress_level != "low"
            else "Tyre supply chain — baseline watch"
        ),
        "summary": (
            "Indian OEM tyres (MRF programme) depend on domestic finishing plus imported "
            "synthetic rubber and carbon black often routed through Gulf petrochemical hubs "
            "and Red Sea shipping lanes."
        ),
        "bullets": bullets,
        "mrf_supplier": {
            "id": mrf.id if mrf else "SUP-IN-TIRE",
            "name": mrf.name if mrf else "MRF Tyres India",
            "risk_score": mrf_score,
        },
        "gulf_feedstock": [
            {
                "id": s.id,
                "name": s.name,
                "country": s.country,
                "risk_score": gulf_scores.get(s.id, 0),
            }
            for s in gulf_suppliers
        ],
        "gulf_country_scores": {"AE": country_ae, "SA": country_sa},
        "related_scenario_id": GULF_SCENARIO_ID,
        "related_history_id": "MSIL-DEMO-GULF-TIRE",
        "news_hits": [
            {
                "title": n.get("title", ""),
                "summary": (n.get("summary") or "")[:280],
                "severity": n.get("severity"),
            }
            for n in news_hits
        ],
        "navigate_to": "parts",
        "navigate_part_id": TIRE_PART_ID,
    }
