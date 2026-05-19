from typing import Any

import numpy as np

from backend.analytics.mcdm.ahp import derive_weights
from backend.analytics.mcdm.topsis import topsis_rank
from backend.config.models import AppConfig


def _passes_gates(supplier: Any, gates: dict) -> bool:
    if gates.get("require_iso9001") and not supplier.capability_flags.get("iso9001"):
        return False
    max_lt = gates.get("max_lead_time_days")
    if max_lt and supplier.lead_time_days > max_lt:
        return False
    return True


def run_mcdm(
    cfg: AppConfig,
    part_id: str,
    supplier_ids: list[str],
    country_risks: dict[str, float],
    supplier_risks: dict[str, float],
) -> tuple[list[dict], dict[str, int], bool]:
    suppliers = {s.id: s for s in cfg.suppliers if s.id in supplier_ids}
    eligible = [sid for sid in supplier_ids if sid in suppliers and _passes_gates(suppliers[sid], cfg.mcdm.gates)]
    if not eligible:
        eligible = list(supplier_ids)

    criteria = cfg.mcdm.criteria
    direct = [c.weight or 0 for c in criteria]
    weights = derive_weights(cfg.mcdm.ahp_pairwise, direct if any(direct) else None)
    if not weights:
        weights = [1 / len(criteria)] * len(criteria)
    w = np.array(weights)

    rows = []
    matrix = []
    for sid in eligible:
        s = suppliers[sid]
        row = []
        for c in criteria:
            if c.id == "cost":
                row.append(s.cost_index)
            elif c.id == "lead_time":
                row.append(float(s.lead_time_days))
            elif c.id == "country_risk":
                row.append(country_risks.get(s.country, 50.0))
            elif c.id == "quality":
                row.append(1.0 if s.capability_flags.get("iso9001") else 0.0)
            elif c.id == "ev_ready":
                row.append(1.0 if s.capability_flags.get("ev_ready") else 0.0)
            else:
                row.append(supplier_risks.get(sid, 50.0))
        matrix.append(row)
    mat = np.array(matrix, dtype=float)
    directions = [c.direction for c in criteria]
    closeness, ranks = topsis_rank(mat, w, directions)

    detail_rows = []
    rank_map = {}
    for i, sid in enumerate(eligible):
        rank_map[sid] = int(ranks[i])
        for j, c in enumerate(criteria):
            detail_rows.append(
                {
                    "supplier_id": sid,
                    "part_id": part_id,
                    "criterion": c.id,
                    "raw": float(mat[i, j]),
                    "normalized": float(mat[i, j]),
                    "weight": float(w[j]),
                    "score": float(closeness[i]),
                    "rank": int(ranks[i]),
                }
            )

    # sensitivity: perturb weights ±10%
    stable = True
    if len(eligible) > 1:
        base_order = sorted(eligible, key=lambda x: rank_map[x])
        for delta in (-0.1, 0.1):
            w2 = w * (1 + delta)
            w2 = w2 / w2.sum()
            _, ranks2 = topsis_rank(mat, w2, directions)
            order2 = sorted(eligible, key=lambda x: int(ranks2[list(eligible).index(x)]))
            if order2 != base_order:
                stable = False
                break

    return detail_rows, rank_map, stable
