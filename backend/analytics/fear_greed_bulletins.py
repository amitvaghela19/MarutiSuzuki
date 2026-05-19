"""Rich Fear & Greed bulletins — educational detail for news and index drivers."""

from __future__ import annotations

from typing import Any

from backend.config.models import AppConfig
from backend.utils.countries import country_name

_RISK_COPY: dict[str, dict[str, str]] = {
    "logistics": {
        "fear": (
            "Port delays, strikes, and lane closures tighten inbound parts flow. Fear rises "
            "because lead times become unpredictable and safety stock burns faster."
        ),
        "greed": (
            "Greed stays muted unless carriers discount capacity or plants clear backlog quickly — "
            "rare when logistics headlines are negative."
        ),
        "msil": (
            "Maruti Suzuki runs just-in-time across Gurgaon, Manesar, and Gujarat. A logistics "
            "shock on any lane can idle lines even when demand is healthy."
        ),
    },
    "supply": {
        "fear": (
            "Shortages and rationing signal that suppliers cannot meet call-offs. Fear spikes "
            "because allocation fights start for semiconductors, rubber, and stampings alike."
        ),
        "greed": (
            "Greed only lifts if the headline reflects oversupply or destocking — otherwise "
            "buyers pay premiums and margin pressure rises."
        ),
        "msil": (
            "MSIL volumes depend on thousands of SKUs arriving on schedule. Supply headlines "
            "often hit tier-2 clusters in Pune, Chennai, and ASEAN corridors first."
        ),
    },
    "natural_disaster": {
        "fear": (
            "Floods, cyclones, and earthquakes can destroy plant, port, or road capacity in days. "
            "Fear jumps because recovery timelines are uncertain."
        ),
        "greed": (
            "Greed may appear briefly if competitors are hit harder and MSIL gains share — but "
            "network damage usually hurts everyone in the region."
        ),
        "msil": (
            "North India monsoon flooding and coastal supplier outages are recurring themes in "
            "auto supply-chain war rooms."
        ),
    },
    "geopolitical": {
        "fear": (
            "Sanctions, conflicts, and shipping reroutes add compliance cost and delay. Fear "
            "reflects rerouted containers and restricted export lanes."
        ),
        "greed": (
            "Greed is low unless a shock creates arbitrage on alternate sourcing — often "
            "outweighed by insurance and freight surcharges."
        ),
        "msil": (
            "Gulf, Red Sea, and ASEAN trade lanes matter for rubber, electronics, and metals "
            "feeding Indian tyre and ECU programmes."
        ),
    },
    "commodity": {
        "fear": (
            "Rubber, steel, chips, and battery materials drive BOM cost. Fear rises when "
            "commodity prices spike or allocation letters circulate."
        ),
        "greed": (
            "Greed can rise when input prices fall or when long-term contracts lock in "
            "favorable terms — buyers feel margin relief."
        ),
        "msil": (
            "Commodity swings flow through MRF-class tyres, Suzuki powertrain content, and "
            "semiconductor-heavy trims on popular models."
        ),
    },
    "general": {
        "fear": (
            "Headlines that raise uncertainty push the fear leg of the index — even before "
            "production data confirms an impact."
        ),
        "greed": (
            "Without a clear positive catalyst, greed typically stays flat while planners wait "
            "for hard shipment data."
        ),
        "msil": (
            "Auto-sector sentiment in India still tracks passenger-vehicle dispatches and "
            "export order books for Suzuki parent coordination."
        ),
    },
}


def _severity_label(raw: int) -> str:
    if raw >= 5:
        return "critical"
    if raw >= 4:
        return "high"
    if raw >= 2:
        return "medium"
    return "low"


def _watch_list(risk_type: str, country: str | None) -> list[str]:
    base = [
        "Re-run analysis after major headlines to refresh fear & greed scores.",
        "Check Scenario lab for matching disruption templates (logistics, commodity, geopolitical).",
        "Review dual-source allocation on criticality-4/5 parts in Parts catalog.",
    ]
    if country:
        base.insert(0, f"Filter suppliers and news by {country_name(country)} exposure.")
    if risk_type == "commodity":
        base.insert(0, "Watch rubber, metals, and semiconductor commodity risk tiles on Command center.")
    elif risk_type == "logistics":
        base.insert(0, "Confirm port-to-plant lead times for ASEAN and EU stampings.")
    elif risk_type == "geopolitical":
        base.insert(0, "Map tier-2 feedstock routes (Gulf, Red Sea) on tyre and chemical parts.")
    return base[:5]


def _news_bulletin(n: dict, idx: int) -> dict[str, Any]:
    risk = (n.get("risk_type") or "general").lower()
    copy = _RISK_COPY.get(risk, _RISK_COPY["general"])
    sev = int(n.get("severity") or 1)
    country = n.get("country_code")
    title = (n.get("title") or "Supply-chain headline").strip()
    summary = (n.get("summary") or "").strip()

    overview = summary or (
        f"This headline was classified as {risk.replace('_', ' ')} risk at severity {sev}/5. "
        "It contributes to the demo news-pressure term in the Fear & Greed model — not a live "
        "trading signal."
    )
    if len(overview) < 120:
        overview += (
            " In plain terms: planners treat it as an early warning to validate inventory, "
            "alternate lanes, and supplier call-offs before line stoppages."
        )

    facts = [
        f"Risk type: {risk.replace('_', ' ').title()}",
        f"Severity score: {sev} / 5 (rule-based classifier on RSS/GDELT ingest)",
    ]
    if country:
        facts.append(f"Geography hint: {country_name(country)} ({country})")
    if n.get("published_at"):
        facts.append(f"Published: {n['published_at']}")

    return {
        "id": f"news-{idx}",
        "kind": "news",
        "title": title,
        "teaser": summary[:160] if summary else overview[:160],
        "severity": sev,
        "severity_label": _severity_label(sev),
        "risk_type": risk,
        "country_code": country,
        "source_url": n.get("url"),
        "source_label": n.get("source") or "News ingest",
        "published_at": n.get("published_at"),
        "detail": {
            "overview": overview,
            "fear_impact": copy["fear"],
            "greed_impact": copy["greed"],
            "msil_supply_chain": copy["msil"],
            "what_to_watch": _watch_list(risk, country),
            "key_facts": facts,
        },
    }


def _driver_bulletin(
    driver: str,
    idx: int,
    *,
    entity_name: str,
    fear: float,
    greed: float,
) -> dict[str, Any]:
    label = "Fear-heavy" if fear > greed + 10 else "Greed-heavy" if greed > fear + 10 else "Balanced"
    return {
        "id": f"driver-{idx}",
        "kind": "driver",
        "title": driver,
        "teaser": f"Index driver for {entity_name} — {label} ({fear:.0f} fear / {greed:.0f} greed).",
        "severity_label": "medium" if abs(fear - greed) < 20 else "high",
        "risk_type": "index_driver",
        "detail": {
            "overview": (
                f"This line appears in the Fear & Greed breakdown for {entity_name}. The demo "
                f"index compares fear ({fear:.0f}) and greed ({greed:.0f}) on a 0–100 scale. "
                f"Sentiment is {label.lower()}: negative drivers widen the fear leg; positive "
                "efficiency or cost drivers lift greed."
            ),
            "fear_impact": (
                "When this driver is elevated, procurement should assume longer recovery times, "
                "more safety-stock debates, and higher escalation to leadership on critical parts."
            ),
            "greed_impact": (
                "If greed drivers dominate for this supplier or OEM aggregate, it usually means "
                "relative stability on cost, capability, or simulation stockout — not market bullishness."
            ),
            "msil_supply_chain": (
                "For Maruti Suzuki, combine this driver with Command center signals and Parts "
                "catalog exposure weights. A single high-fear supplier on a criticality-5 part can "
                "move the OEM aggregate even when headline news is quiet."
            ),
            "what_to_watch": [
                "Compare this driver before and after the next analysis run.",
                "Open the supplier row in Fear & Greed table for country and exposure context.",
                "Cross-check matching ops signals on Command center.",
            ],
            "key_facts": [
                f"Entity: {entity_name}",
                f"Fear index: {fear:.0f}",
                f"Greed index: {greed:.0f}",
                f"Driver text: {driver}",
            ],
        },
    }


def _macro_bulletins(cfg: AppConfig | None) -> list[dict[str, Any]]:
    if not cfg:
        return []
    out: list[dict[str, Any]] = []
    themes = (cfg.company.supply_chain_themes or []) if cfg.company else []
    for i, theme in enumerate(themes[:4]):
        out.append(
            {
                "id": f"macro-theme-{i}",
                "kind": "macro",
                "title": f"MSIL supply theme: {theme[:80]}",
                "teaser": theme[:140],
                "severity_label": "medium",
                "risk_type": "strategic_theme",
                "detail": {
                    "overview": (
                        f"{theme} This theme is listed in the Maruti Suzuki company profile used "
                        "by the demo command center to frame long-horizon sourcing risks."
                    ),
                    "fear_impact": (
                        "Structural themes keep baseline fear from falling too low — they remind "
                        "planners that certain corridors (ASEAN rubber, chips, Gulf feedstock) stay "
                        "on the watchlist even between crises."
                    ),
                    "greed_impact": (
                        "When themes are stable and simulation stockouts are low, greed can recover "
                        "on the back of dual sourcing wins and localisation progress."
                    ),
                    "msil_supply_chain": (
                        "Use themes to prioritise Scenario lab runs and Enterprise disruption "
                        "history — they connect today's index to past Manesar, COVID, and chip episodes."
                    ),
                    "what_to_watch": [
                        "Enterprise → Disruption history for analog episodes.",
                        "Scenario lab for rubber, chip, and Gulf tyre shocks.",
                        "Parts catalog for criticality-5 exposure on related commodities.",
                    ],
                    "key_facts": ["Source: maruti_company.yaml supply_chain_themes"],
                },
            }
        )
    return out


def build_fear_greed_bulletins(
    news: list[dict],
    *,
    maruti: dict[str, Any],
    suppliers: list[dict[str, Any]],
    cfg: AppConfig | None = None,
    max_news: int = 14,
) -> list[dict[str, Any]]:
    sorted_news = sorted(
        news,
        key=lambda n: (int(n.get("severity") or 0), len(n.get("summary") or "")),
        reverse=True,
    )
    bulletins: list[dict[str, Any]] = []
    for idx, n in enumerate(sorted_news[:max_news]):
        bulletins.append(_news_bulletin(n, idx))

    for idx, d in enumerate(maruti.get("drivers") or []):
        bulletins.append(
            _driver_bulletin(
                d,
                1000 + idx,
                entity_name=maruti.get("name", "Maruti Suzuki"),
                fear=float(maruti.get("fear_index", 50)),
                greed=float(maruti.get("greed_index", 50)),
            )
        )

    top_fear = sorted(suppliers, key=lambda s: s.get("fear_index", 0), reverse=True)[:3]
    for sup in top_fear:
        sid = sup.get("id", "sup")
        for idx, d in enumerate((sup.get("drivers") or [])[:2]):
            bulletins.append(
                {
                    **_driver_bulletin(
                        d,
                        idx,
                        entity_name=sup.get("name", sid),
                        fear=float(sup.get("fear_index", 50)),
                        greed=float(sup.get("greed_index", 50)),
                    ),
                    "id": f"driver-{sid}-{idx}",
                }
            )

    bulletins.extend(_macro_bulletins(cfg))
    return bulletins
