"""Synthetic digital twin state for manufacturing plants."""

from __future__ import annotations

import hashlib
from typing import Any

from backend.config.loader import _load_yaml
from backend.settings import settings


def _load_twin_meta() -> dict:
    return _load_yaml(settings.config_dir / "digital_twin.yaml")


def _plant_metrics(plant_id: str, part_count: int, run_seed: str) -> dict:
    h = int(hashlib.md5(f"{run_seed}:{plant_id}".encode()).hexdigest()[:8], 16)
    base = 0.55 + (h % 400) / 1000
    return {
        "throughput_units_per_hour": int(180 + (h % 120)),
        "buffer_days_of_supply": round(4.5 + (h % 80) / 20, 1),
        "oee_pct": round(base * 100, 1),
        "quality_ppm": int(80 + (h % 60)),
        "energy_kwh_per_unit": round(12.5 + (h % 30) / 10, 2),
        "parts_on_line": part_count,
        "status": "nominal" if base > 0.72 else "constrained",
    }


def build_digital_twin(
    cfg: Any,
    *,
    supplier_risks: dict[str, float] | None = None,
    run_id: str | None = None,
) -> dict:
    meta = _load_twin_meta()
    supplier_risks = supplier_risks or {}
    seed = run_id or "baseline"
    plants_out: list[dict] = []

    for plant in cfg.plants:
        parts = plant.parts_used or []
        metrics = _plant_metrics(plant.id, len(parts), seed)
        bottlenecks: list[dict] = []
        for pid in parts[:3]:
            part = next((p for p in cfg.parts if p.id == pid), None)
            if not part:
                continue
            sup_id = getattr(part, "primary_supplier_id", None) or (
                part.supplier_ids[0] if part.supplier_ids else None
            )
            risk = supplier_risks.get(sup_id, 40.0) if sup_id else 40.0
            if risk > 50:
                bottlenecks.append(
                    {
                        "part_id": pid,
                        "part_name": part.name,
                        "supplier_id": sup_id,
                        "risk_score": round(risk, 1),
                    }
                )

        plants_out.append(
            {
                "id": plant.id,
                "name": plant.name,
                "location": plant.location,
                "metrics": metrics,
                "bottlenecks": bottlenecks,
                "lines": [
                    {
                        "id": f"{plant.id}-L1",
                        "name": "Main assembly",
                        "utilization_pct": metrics["oee_pct"],
                    },
                    {
                        "id": f"{plant.id}-L2",
                        "name": "Sub-assembly / kitting",
                        "utilization_pct": round(metrics["oee_pct"] * 0.92, 1),
                    },
                ],
            }
        )

    network_health = (
        "green"
        if all(p["metrics"]["status"] == "nominal" for p in plants_out)
        else "amber"
    )

    return {
        "disclaimer": meta.get("disclaimer", ""),
        "sensor_types": meta.get("sensor_types", []),
        "network_health": network_health,
        "plants": plants_out,
        "global_kpis": {
            "total_plants": len(plants_out),
            "avg_oee_pct": round(
                sum(p["metrics"]["oee_pct"] for p in plants_out) / max(len(plants_out), 1),
                1,
            ),
            "plants_constrained": sum(
                1 for p in plants_out if p["metrics"]["status"] == "constrained"
            ),
        },
    }
