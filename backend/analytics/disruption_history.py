"""Curated public disruption timeline for MSIL educational context."""

from __future__ import annotations

from typing import Any

from backend.config.loader import _load_yaml
from backend.settings import settings

TIRE_PART_ID = "PART-TIRE"
CHIP_SCENARIO_ID = "CHIP-SHORTAGE"
GULF_SCENARIO_ID = "ME-GULF-TIRE"
RUBBER_COMMODITY = "rubber"


def load_disruption_history_raw() -> dict:
    return _load_yaml(settings.config_dir / "supply_disruptions_history.yaml")


def scenario_history_analogs() -> dict[str, dict[str, Any]]:
    """Map scenario_id -> primary historical incident label for Scenario Lab."""
    out: dict[str, dict[str, Any]] = {}
    for inc in load_disruption_history_raw().get("incidents") or []:
        sid = inc.get("related_scenario_id")
        if not sid or sid in out:
            continue
        out[sid] = {
            "related_history_id": inc.get("id"),
            "historical_analog": f"{inc.get('year', '')} — {inc.get('title', '')}".strip(" —"),
        }
    return out


def _chip_stockout_high(sim_results: list[dict] | None) -> bool:
    if not sim_results:
        return False
    for r in sim_results:
        if r.get("scenario_id") != CHIP_SCENARIO_ID:
            continue
        p = (r.get("metrics") or {}).get("stockout_probability", 0)
        if p >= 0.3:
            return True
    return False


def _gulf_rubber_stress(
    sim_results: list[dict] | None,
    commodity_risks: dict[str, float] | None,
) -> bool:
    if commodity_risks and commodity_risks.get(RUBBER_COMMODITY, 0) >= 55:
        return True
    if not sim_results:
        return False
    for r in sim_results:
        sid = r.get("scenario_id")
        if sid not in (GULF_SCENARIO_ID, "RUBBER-SHOCK"):
            continue
        p = (r.get("metrics") or {}).get("stockout_probability", 0)
        if p >= 0.28:
            return True
    return False


def _live_analog_for_incident(
    incident: dict,
    *,
    sim_results: list[dict] | None,
    commodity_risks: dict[str, float] | None,
) -> bool:
    related = incident.get("related_scenario_id")
    if related == CHIP_SCENARIO_ID and _chip_stockout_high(sim_results):
        return True
    if related in (GULF_SCENARIO_ID, "RUBBER-SHOCK") and _gulf_rubber_stress(
        sim_results, commodity_risks
    ):
        return True
    if incident.get("id") == "MSIL-DEMO-GULF-TIRE" and _gulf_rubber_stress(
        sim_results, commodity_risks
    ):
        return True
    return False


def build_disruption_history_payload(
    *,
    sim_results: list[dict] | None = None,
    commodity_risks: dict[str, float] | None = None,
) -> dict[str, Any]:
    raw = load_disruption_history_raw()
    incidents = list(raw.get("incidents") or [])
    enriched: list[dict] = []
    analog_count = 0
    for inc in incidents:
        row = dict(inc)
        analog = _live_analog_for_incident(
            inc, sim_results=sim_results, commodity_risks=commodity_risks
        )
        row["live_analog"] = analog
        if analog:
            analog_count += 1
        enriched.append(row)

    years = [i.get("year") for i in enriched if i.get("year")]
    timeline_summary = (
        f"{len(enriched)} documented episodes from {min(years)} to {max(years)} "
        "— public sources, educational context for sourcing teams."
    )
    if analog_count:
        timeline_summary += (
            f" {analog_count} episode(s) rhyme with stress in the current analysis run."
        )

    return {
        "disclaimer": raw.get("disclaimer", "").strip(),
        "incidents": enriched,
        "timeline_summary": timeline_summary,
        "analog_count": analog_count,
    }
