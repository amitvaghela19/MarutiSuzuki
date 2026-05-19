from typing import Any

from backend.config.models import AppConfig, PartConfig
from backend.utils.countries import country_name


def _primary_id(part: PartConfig) -> str:
    if part.primary_supplier_id:
        return part.primary_supplier_id
    return part.supplier_ids[0] if part.supplier_ids else ""


def _alternate_ids(part: PartConfig) -> list[str]:
    primary = _primary_id(part)
    return [s for s in part.supplier_ids if s != primary]


def _supplier_row(sup: Any, risk: float | None = None) -> dict:
    row = {
        "id": sup.id,
        "name": sup.name,
        "country": sup.country,
        "country_name": country_name(sup.country),
        "lead_time_days": sup.lead_time_days,
        "commodities": sup.commodities,
    }
    if risk is not None:
        row["risk_score"] = round(risk, 1)
    return row


def build_sourcing_matrix(
    cfg: AppConfig,
    supplier_risks: dict[str, float] | None = None,
    recommendations: list[dict] | None = None,
) -> dict:
    """Primary supplier, approved alternates, and mitigation options per part."""
    supplier_risks = supplier_risks or {}
    rec_by_part = {r["part_id"]: r for r in (recommendations or [])}
    sup_map = {s.id: s for s in cfg.suppliers}

    rows: list[dict] = []
    for part in cfg.parts:
        primary_id = _primary_id(part)
        alt_ids = _alternate_ids(part)
        primary = sup_map.get(primary_id)
        alternates = [sup_map[aid] for aid in alt_ids if aid in sup_map]
        rec = rec_by_part.get(part.id)

        rows.append(
            {
                "part_id": part.id,
                "part_name": part.name,
                "category": part.category,
                "vehicle_system": part.vehicle_system,
                "criticality": part.criticality,
                "main_commodity": part.main_commodity,
                "primary_supplier": _supplier_row(
                    primary,
                    supplier_risks.get(primary_id) if primary else None,
                )
                if primary
                else None,
                "alternate_suppliers": [
                    _supplier_row(s, supplier_risks.get(s.id)) for s in alternates
                ],
                "alternative_solutions": part.alternative_solutions,
                "recommended_allocation": rec.get("allocation") if rec else None,
                "allocation_mode": rec.get("allocation_mode") if rec else None,
                "allocation_rationale": rec.get("rationale") if rec else None,
            }
        )

    # Reverse index: supplier -> parts (primary vs alternate)
    supplier_roles: dict[str, dict] = {}
    for s in cfg.suppliers:
        supplier_roles[s.id] = {
            "supplier": _supplier_row(s, supplier_risks.get(s.id)),
            "primary_for_parts": [],
            "alternate_for_parts": [],
        }
    for row in rows:
        pid = row["primary_supplier"]["id"] if row["primary_supplier"] else None
        if pid and pid in supplier_roles:
            supplier_roles[pid]["primary_for_parts"].append(
                {"part_id": row["part_id"], "part_name": row["part_name"]}
            )
        for alt in row["alternate_suppliers"]:
            if alt["id"] in supplier_roles:
                supplier_roles[alt["id"]]["alternate_for_parts"].append(
                    {"part_id": row["part_id"], "part_name": row["part_name"]}
                )

    return {
        "disclaimer": (
            "Synthetic supplier names and sourcing playbooks for demo only — not MSIL "
            "approved vendor lists or contract allocations."
        ),
        "parts": rows,
        "suppliers_index": list(supplier_roles.values()),
    }
