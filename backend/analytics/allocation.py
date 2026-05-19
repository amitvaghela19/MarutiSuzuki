"""Part-level supplier allocation — variable splits, not a fixed 60/40 default."""

from __future__ import annotations

from typing import Any

from backend.config.models import AppConfig, PartConfig

MIN_DUAL_SHARE = 0.08  # below this, treat as single-source


def _normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        return weights
    return {k: round(v / total, 3) for k, v in weights.items()}


def compute_part_allocation(
    cfg: AppConfig,
    part: PartConfig,
    sorted_suppliers: list[tuple[str, int]],
    supplier_risks: dict[str, float],
    max_stockout: float,
) -> tuple[dict[str, float], list[str], str]:
    """
    Returns (allocation weights, driver strings, mode).
    mode: single_source | dual_source | multi_source | emergency_shift
    """
    if not sorted_suppliers:
        return {}, ["no qualified suppliers in MCDM ranking"], "unconfigured"

    primary = sorted_suppliers[0][0]
    alternates = [sid for sid, _ in sorted_suppliers[1:] if sid != primary]
    primary_risk = supplier_risks.get(primary, 50.0)
    drivers: list[str] = []

    stockout_limit = cfg.thresholds.stockout_probability_limit
    high_risk = cfg.thresholds.high_risk
    emergency = cfg.thresholds.emergency_override

    # Single-source: low risk and simulation OK
    if (
        max_stockout <= stockout_limit
        and primary_risk < high_risk
    ):
        drivers.append("single_source: incumbent risk and stockout probability within limits")
        return {primary: 1.0}, drivers, "single_source"

    if not alternates:
        drivers.append("single_source: no alternate supplier configured")
        return {primary: 1.0}, drivers, "single_source"

    alternate = alternates[0]
    alt_risk = supplier_risks.get(alternate, 50.0)
    crit = part.criticality / 5.0

    # Primary share: higher when primary is lower-risk; lower when primary is stressed
    if primary_risk >= emergency:
        # Shift volume toward alternate under emergency
        primary_pct = max(0.52, min(0.72, 0.68 - (primary_risk - emergency) / 120))
        drivers.append("emergency_shift: primary risk above emergency threshold")
        mode = "emergency_shift"
    elif max_stockout > stockout_limit:
        # Simulation-driven dual: more alternate when stockout worse
        primary_pct = max(0.55, min(0.82, 0.78 - max_stockout * 0.35 + (alt_risk - primary_risk) / 250))
        drivers.append(
            f"dual_source: scenario stockout P={max_stockout:.0%} exceeds {stockout_limit:.0%} limit"
        )
        mode = "dual_source"
    elif primary_risk >= high_risk:
        # Risk-driven partial dual without full simulation trigger
        primary_pct = max(0.62, min(0.88, 0.82 - (primary_risk - high_risk) / 80))
        drivers.append(f"high_risk: primary score {primary_risk:.1f} ≥ {high_risk}")
        mode = "dual_source"
    else:
        # Mild hedge only for high-criticality parts
        if part.criticality >= 4:
            primary_pct = 0.88
            drivers.append("hedge: optional minor alternate share for criticality ≥ 4")
            mode = "dual_source"
        else:
            drivers.append("single_source: alternates available but metrics do not require split")
            return {primary: 1.0}, drivers, "single_source"

    # Criticality nudges toward more diversification when already dual-sourcing
    if mode != "single_source":
        primary_pct = max(0.50, min(0.92, primary_pct - crit * 0.06))

    allocation: dict[str, float] = {
        primary: round(primary_pct, 3),
        alternate: round(1.0 - primary_pct, 3),
    }

    # Three-way split only for critical parts, high stockout, and 2+ alternates
    if (
        len(alternates) >= 2
        and part.criticality >= 4
        and max_stockout > stockout_limit + 0.1
    ):
        third = alternates[1]
        third_share = min(0.12, max(0.05, (max_stockout - stockout_limit) * 0.25))
        take_from_primary = third_share * 0.6
        take_from_alt = third_share * 0.4
        allocation[primary] = max(MIN_DUAL_SHARE, allocation[primary] - take_from_primary)
        allocation[alternate] = max(MIN_DUAL_SHARE, allocation[alternate] - take_from_alt)
        allocation[third] = round(third_share, 3)
        allocation = _normalize(allocation)
        drivers.append(f"multi_source: tertiary supplier {third} for critical SKU")
        mode = "multi_source"

    # Collapse near-single-source splits
    alt_share = 1.0 - allocation.get(primary, 1.0)
    if len(allocation) == 2 and alt_share < MIN_DUAL_SHARE:
        drivers.append("single_source: computed alternate share below minimum dual threshold")
        return {primary: 1.0}, drivers, "single_source"

    allocation = _normalize(allocation)
    return allocation, drivers, mode


def format_allocation_labels(
    allocation: dict[str, float],
    sup_by_id: dict[str, Any],
) -> str:
    parts: list[str] = []
    for sid, pct in sorted(allocation.items(), key=lambda x: -x[1]):
        name = sup_by_id[sid].name if sid in sup_by_id else sid
        parts.append(f"{name}: {pct * 100:.0f}%")
    return " · ".join(parts)
