from typing import Any

from backend.analytics.allocation import compute_part_allocation
from backend.config.models import AppConfig


def build_recommendations(
    cfg: AppConfig,
    part_ranks: dict[str, dict[str, int]],
    supplier_risks: dict[str, float],
    sim_results: list[dict],
) -> list[dict]:
    recs = []
    stockout_by_scenario: dict[str, float] = {}
    for r in sim_results:
        if r["strategy_id"] == "dual_source":
            stockout_by_scenario[r["scenario_id"]] = r["metrics"]["stockout_probability"]

    max_stockout = max(stockout_by_scenario.values()) if stockout_by_scenario else 0.0
    sup_by_id = {s.id: s for s in cfg.suppliers}

    for part in cfg.parts:
        ranks = part_ranks.get(part.id, {})
        if not ranks:
            continue
        sorted_sups = sorted(ranks.items(), key=lambda x: x[1])
        primary = sorted_sups[0][0]
        alternate = sorted_sups[1][0] if len(sorted_sups) > 1 else primary

        allocation, drivers, mode = compute_part_allocation(
            cfg, part, sorted_sups, supplier_risks, max_stockout
        )

        primary_risk = supplier_risks.get(primary, 50.0)
        alt_risk = supplier_risks.get(alternate, 50.0)

        rationale = {
            "primary": primary,
            "topsis_rank": ranks.get(primary),
            "drivers": drivers,
            "allocation_mode": mode,
            "max_scenario_stockout": round(max_stockout, 3),
        }

        primary_name = sup_by_id.get(primary).name if primary in sup_by_id else primary
        alternate_name = sup_by_id.get(alternate).name if alternate in sup_by_id else alternate
        rationale["primary_name"] = primary_name
        rationale["alternate_name"] = alternate_name
        rationale["alternate_supplier_ids"] = [sid for sid, _ in sorted_sups[1:]]
        rationale["alternative_solutions"] = part.alternative_solutions

        recs.append(
            {
                "part_id": part.id,
                "part_name": part.name,
                "allocation": allocation,
                "allocation_mode": mode,
                "rationale": rationale,
                "supplier_risks": {
                    sid: supplier_risks.get(sid, 50.0)
                    for sid in allocation
                },
                "primary_supplier_id": primary,
                "alternate_supplier_ids": rationale["alternate_supplier_ids"],
                "alternative_solutions": part.alternative_solutions,
            }
        )
    return recs
