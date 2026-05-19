"""Enriched parts catalog with suppliers, risk, and rationale."""

from __future__ import annotations

from typing import Any

from backend.config.models import AppConfig
from backend.utils.countries import country_name


def build_enriched_parts_catalog(
    cfg: AppConfig,
    *,
    supplier_risks: dict[str, float] | None = None,
    supplier_components: dict[str, dict] | None = None,
    recommendations: list[dict] | None = None,
    part_rankings: dict[str, dict[str, int]] | None = None,
) -> dict:
    supplier_risks = supplier_risks or {}
    supplier_components = supplier_components or {}
    recommendations = recommendations or []
    part_rankings = part_rankings or {}
    rec_by_part = {r["part_id"]: r for r in recommendations}
    sup_by_id = {s.id: s for s in cfg.suppliers}

    parts_out: list[dict] = []
    by_category: dict[str, list] = {}

    for part in cfg.parts:
        rec = rec_by_part.get(part.id)
        allocation_mode = rec.get("allocation_mode") if rec else None
        ranks = part_rankings.get(part.id, {})
        suppliers_detail: list[dict] = []
        for sid in part.supplier_ids:
            sup = sup_by_id.get(sid)
            if not sup:
                continue
            risk = supplier_risks.get(sid)
            suppliers_detail.append(
                {
                    "id": sid,
                    "name": sup.name,
                    "country": sup.country,
                    "country_name": country_name(sup.country),
                    "lead_time_days": sup.lead_time_days,
                    "trust_tier": sup.trust_tier,
                    "is_primary": sid == part.primary_supplier_id,
                    "topsis_rank": ranks.get(sid),
                    "risk_score": round(risk, 2) if risk is not None else None,
                    "risk_components": supplier_components.get(sid),
                    "reference_url": sup.reference_url,
                }
            )
        suppliers_detail.sort(
            key=lambda x: (
                0 if x["is_primary"] else 1,
                x["topsis_rank"] if x["topsis_rank"] is not None else 999,
            )
        )

        composite_risk = None
        if supplier_risks and part.supplier_ids:
            scores = [supplier_risks[s] for s in part.supplier_ids if s in supplier_risks]
            if scores:
                w = part.criticality / 5.0
                composite_risk = round(
                    (sum(scores) / len(scores)) * (0.7 + 0.3 * w), 2
                )

        row = {
            **part.model_dump(),
            "suppliers": suppliers_detail,
            "supplier_count": len(suppliers_detail),
            "composite_risk_score": composite_risk,
            "recommendation": rec,
            "allocation_mode": allocation_mode,
            "why_summary": _why_summary(
                part, rec, suppliers_detail, composite_risk, allocation_mode
            ),
            "alternative_solutions": part.alternative_solutions,
        }
        parts_out.append(row)
        by_category.setdefault(part.category, []).append(row)

    return {
        "total": len(parts_out),
        "categories": sorted(by_category.keys()),
        "by_category": by_category,
        "parts": parts_out,
    }


def _why_summary(
    part: Any,
    rec: dict | None,
    suppliers: list[dict],
    composite_risk: float | None,
    allocation_mode: str | None = None,
) -> str:
    bits: list[str] = []
    if composite_risk is not None:
        bits.append(f"Composite exposure risk {composite_risk:.1f}/100")
    if rec:
        mode = allocation_mode or rec.get("allocation_mode") or "unknown"
        alloc = rec.get("allocation") or {}
        if mode == "single_source" or (
            len(alloc) == 1 and next(iter(alloc.values())) >= 0.99
        ):
            primary = next((s for s in suppliers if s.get("is_primary")), suppliers[0] if suppliers else None)
            if primary:
                bits.append(f"Single source: 100% to {primary['name']}")
        elif alloc:
            named = ", ".join(
                f"{next((s['name'] for s in suppliers if s['id'] == k), k)}: {v:.0%}"
                for k, v in sorted(alloc.items(), key=lambda x: -x[1])
            )
            bits.append(f"Split ({mode.replace('_', ' ')}): {named}")
        drivers = (rec.get("rationale") or {}).get("drivers") or []
        if drivers:
            bits.append("; ".join(str(d) for d in drivers[:2]))
    elif suppliers:
        primary = next((s for s in suppliers if s.get("is_primary")), suppliers[0])
        bits.append(f"Primary source {primary['name']} ({primary.get('country_name', '')})")
    if part.criticality >= 4:
        bits.append(f"Criticality {part.criticality}/5 — prioritize dual-source")
    return ". ".join(bits) if bits else "Run analysis for allocation rationale and live risk scores."
