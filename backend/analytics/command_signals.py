"""Prioritized operational signals for command center."""

from __future__ import annotations

from typing import Any


def _news_severity_label(raw: int) -> str:
    """Map classifier scale 1–5 to signal severity."""
    if raw >= 5:
        return "critical"
    if raw >= 4:
        return "high"
    if raw >= 2:
        return "medium"
    return "low"


def _news_why(article: dict, raw_severity: int, risk_type: str) -> str:
    parts = [
        f"Headline matched supply-chain risk rules ({risk_type}, severity {raw_severity}/5).",
    ]
    if article.get("summary"):
        parts.append(str(article["summary"])[:400])
    cc = article.get("country_code")
    if cc:
        parts.append(f"Geography hint: {cc}.")
    return " ".join(parts)


def build_command_signals(
    cfg: Any,
    *,
    news: list[dict],
    country_risk: list[tuple],
    supplier_risk: list[tuple],
    recs: list[dict],
    sim_results: list[dict] | None = None,
    tire_brief: dict | None = None,
) -> dict:
    signals: list[dict] = []
    priority = 0

    if tire_brief and tire_brief.get("stress_level") in ("elevated", "high"):
        priority += 1
        sev = "high" if tire_brief["stress_level"] == "high" else "medium"
        bullets = tire_brief.get("bullets") or []
        why = bullets[0] if bullets else tire_brief.get("summary", "")
        signals.append(
            {
                "id": "TIRE-GULF",
                "priority": priority,
                "severity": sev,
                "category": "commodity",
                "title": tire_brief.get("headline", "MRF / Gulf tyre supply chain"),
                "detail": (tire_brief.get("summary") or "")[:320],
                "why": why,
                "entity_id": tire_brief.get("part_id", "PART-TIRE"),
                "action": "Open Parts catalog",
                "navigate_to": "parts",
            }
        )

    for sid, score, _ in sorted(supplier_risk, key=lambda x: -x[1])[:5]:
        if score < 55:
            break
        priority += 1
        sup = next((s for s in cfg.suppliers if s.id == sid), None)
        signals.append(
            {
                "id": f"SUP-{sid}",
                "priority": priority,
                "severity": "high" if score >= 70 else "medium",
                "category": "supplier",
                "title": f"Supplier risk elevated: {sup.name if sup else sid}",
                "detail": f"Composite risk score {score:.1f}. Review dual-source and safety stock.",
                "why": (
                    f"Supplier {sup.name if sup else sid} scored {score:.1f}/100 in the latest "
                    "risk model (lead time, geography, commodity exposure, and news overlap)."
                ),
                "entity_id": sid,
                "action": "Open suppliers",
                "navigate_to": "suppliers",
            }
        )

    for code, score, _ in sorted(country_risk, key=lambda x: -x[1])[:3]:
        if score < 50:
            break
        priority += 1
        signals.append(
            {
                "id": f"CTY-{code}",
                "priority": priority,
                "severity": "high" if score >= 65 else "medium",
                "category": "geopolitical",
                "title": f"Country exposure: {code}",
                "detail": f"Country risk index {score:.1f}. Check alternate geography sourcing.",
                "why": (
                    f"Country {code} risk index {score:.1f}/100 driven by geopolitical, logistics, "
                    "and supplier concentration in the latest run."
                ),
                "entity_id": code,
                "action": "View command center",
                "navigate_to": "dashboard",
            }
        )

    for idx, n in enumerate(news[:8]):
        raw_sev = int(n.get("severity") or 1)
        if raw_sev < 2:
            continue
        risk_type = n.get("risk_type", "general")
        severity = _news_severity_label(raw_sev)
        priority += 1
        signals.append(
            {
                "id": f"NEWS-{idx}",
                "priority": priority,
                "severity": severity,
                "category": "news",
                "title": (n.get("title") or "Headline")[:120],
                "detail": f"{risk_type.replace('_', ' ').title()} risk · severity {raw_sev}/5",
                "why": _news_why(n, raw_sev, risk_type),
                "summary": (n.get("summary") or "")[:500],
                "risk_type": risk_type,
                "news_index": idx,
                "entity_id": str(idx),
                "action": "Read why",
                "navigate_to": "dashboard",
            }
        )

    if sim_results:
        worst = max(
            sim_results,
            key=lambda r: r.get("metrics", {}).get("stockout_probability", 0),
        )
        p = worst.get("metrics", {}).get("stockout_probability", 0)
        if p >= 0.25:
            priority += 1
            signals.append(
                {
                    "id": "SIM-WORST",
                    "priority": priority,
                    "severity": "critical" if p >= 0.45 else "high",
                    "category": "scenario",
                    "title": f"Scenario stress: {worst.get('scenario_name', worst.get('scenario_id'))}",
                    "detail": f"Stockout probability {p:.0%} under {worst.get('strategy_id', 'strategy')}.",
                    "why": (
                        f"Monte Carlo simulation flagged {p:.0%} stockout probability for "
                        f"{worst.get('scenario_name', worst.get('scenario_id'))} under strategy "
                        f"{worst.get('strategy_id', 'strategy')} — highest among scored scenarios."
                    ),
                    "entity_id": worst.get("scenario_id"),
                    "action": "Open Scenario Lab",
                    "navigate_to": "scenarios",
                }
            )

    for rec in recs[:3]:
        alt = rec.get("alternate_supplier_ids") or []
        if len(alt) < 1:
            priority += 1
            signals.append(
                {
                    "id": f"PART-{rec['part_id']}",
                    "priority": priority,
                    "severity": "medium",
                    "category": "sourcing",
                    "title": f"Single-source exposure: {rec['part_name']}",
                    "detail": "No qualified alternate in config — mitigation playbook required.",
                    "why": (
                        f"Part {rec['part_name']} has no configured alternate supplier; allocation "
                        "relies on a single source in the current recommendation set."
                    ),
                    "entity_id": rec["part_id"],
                    "action": "Explain allocation",
                    "navigate_to": "why",
                }
            )

    signals.sort(key=lambda s: ({"critical": 0, "high": 1, "medium": 2, "low": 3}[s["severity"]], s["priority"]))

    return {
        "total": len(signals),
        "critical_count": sum(1 for s in signals if s["severity"] == "critical"),
        "high_count": sum(1 for s in signals if s["severity"] == "high"),
        "signals": signals[:20],
        "autopilot_mode": "advisory",
        "last_refresh_note": "Signals recomputed on each analysis run",
    }
