import random
import statistics
from typing import Any

import simpy

from backend.config.models import AppConfig


def _run_simpy_scenario(
    lead_time: float,
    demand_rate: float,
    capacity: float,
    horizon: float = 90.0,
) -> dict[str, float]:
    env = simpy.Environment()
    stock = 100.0
    stockouts = 0
    stockout_days = 0

    def production():
        nonlocal stock
        while True:
            yield env.timeout(max(0.5, lead_time))
            stock += capacity

    def consumption():
        nonlocal stock, stockouts, stockout_days
        while True:
            yield env.timeout(1.0)
            stock -= demand_rate
            if stock < 0:
                stockouts += 1
                stockout_days += 1
                stock = 0

    env.process(production())
    env.process(consumption())
    env.run(until=horizon)
    service_level = max(0.0, 100.0 * (1.0 - stockout_days / horizon))
    return {
        "stockouts": float(stockouts),
        "stockout_days": float(stockout_days),
        "final_stock": stock,
        "service_level_pct": service_level,
    }


def _strategy_params(
    strategy_id: str,
    split: list[float],
    base_lt: float,
    base_cap: float,
    base_demand: float,
) -> tuple[float, float, float]:
    """Return effective lead time, capacity, relative cost index."""
    if strategy_id == "dual_source":
        lt = base_lt * (0.55 * split[0] + 0.45 * split[1]) * 0.9
        cap = base_cap * 1.18
        cost = 1.08
        return lt, cap, cost
    return base_lt, base_cap, 1.0


def run_scenarios(
    cfg: AppConfig,
    supplier_risks: dict[str, float],
    seed: int = 42,
    monte_carlo_runs: int = 30,
) -> list[dict]:
    random.seed(seed)
    results: list[dict] = []
    avg_supplier_risk = (
        statistics.mean(supplier_risks.values()) if supplier_risks else 50.0
    )

    for sc in cfg.scenarios:
        shock = sc.shock
        lt_mult = float(shock.get("lead_time_multiplier", 1.0))
        cap_factor = float(shock.get("capacity_factor", 1.0))
        demand_mult = float(shock.get("demand_spike", 1.0))
        cost_pressure = float(shock.get("cost_pressure", 1.0))
        horizon = float(sc.duration_days or 90)
        risk_adj = 1.0 + (avg_supplier_risk - 50.0) / 200.0

        strategies = [
            ("single_source", [1.0]),
            ("dual_source", cfg.thresholds.dual_source_split),
            ("emergency_airfreight", [1.0]),
        ]

        for strategy_id, split in strategies:
            stockouts: list[float] = []
            stockout_days_list: list[float] = []
            service_levels: list[float] = []

            for _ in range(monte_carlo_runs):
                base_lt = 14.0 * lt_mult * risk_adj * random.uniform(0.88, 1.12)
                base_cap = 8.0 * cap_factor * random.uniform(0.9, 1.05)
                base_demand = 5.0 * demand_mult

                if strategy_id == "emergency_airfreight":
                    lt = max(3.0, base_lt * 0.35)
                    cap = base_cap * 0.85
                    cost = 1.45 * cost_pressure
                else:
                    lt, cap, cost = _strategy_params(
                        strategy_id, split, base_lt, base_cap, base_demand
                    )

                m = _run_simpy_scenario(lt, demand_rate=base_demand, capacity=cap, horizon=horizon)
                stockouts.append(m["stockouts"])
                stockout_days_list.append(m["stockout_days"])
                service_levels.append(m["service_level_pct"])

            avg_stockouts = statistics.mean(stockouts)
            p90_stockouts = sorted(stockouts)[int(0.9 * len(stockouts)) - 1]
            stockout_prob = sum(1 for s in stockouts if s > 0) / len(stockouts)
            avg_service = statistics.mean(service_levels)
            recovery_days = min(horizon, avg_stockouts * 2.5 + lt_mult * 3)

            results.append(
                {
                    "scenario_id": sc.id,
                    "scenario_name": sc.name,
                    "scenario_description": sc.description,
                    "severity": sc.severity,
                    "category": sc.category,
                    "duration_days": sc.duration_days,
                    "strategy_id": strategy_id,
                    "shock": shock,
                    "metrics": {
                        "avg_stockouts": round(avg_stockouts, 2),
                        "p90_stockouts": round(p90_stockouts, 2),
                        "stockout_probability": round(stockout_prob, 3),
                        "service_level_pct": round(avg_service, 1),
                        "recovery_days_est": round(recovery_days, 1),
                        "lead_time_multiplier": lt_mult,
                        "capacity_factor": cap_factor,
                        "demand_spike": demand_mult,
                        "cost_pressure": cost_pressure,
                        "relative_cost_index": round(
                            (1.45 if strategy_id == "emergency_airfreight" else 1.08 if strategy_id == "dual_source" else 1.0)
                            * cost_pressure,
                            2,
                        ),
                        "monte_carlo_runs": monte_carlo_runs,
                    },
                }
            )
    return results


def build_scenario_insights(cfg: AppConfig, sim_results: list[dict]) -> dict[str, Any]:
    """Aggregate simulation output for advanced Scenario Lab UI."""
    from backend.analytics.disruption_history import scenario_history_analogs

    history_by_scenario = scenario_history_analogs()
    catalog = []
    for s in cfg.scenarios:
        row = {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "severity": s.severity,
            "category": s.category,
            "duration_days": s.duration_days,
            "shock": s.shock,
        }
        analog = history_by_scenario.get(s.id)
        if analog:
            row.update(analog)
        catalog.append(row)

    by_scenario: dict[str, list[dict]] = {}
    for r in sim_results:
        by_scenario.setdefault(r["scenario_id"], []).append(r)

    baseline = by_scenario.get("BASELINE", [])
    baseline_dual = next((x for x in baseline if x["strategy_id"] == "dual_source"), None)
    baseline_stockout = (
        baseline_dual["metrics"]["stockout_probability"] if baseline_dual else 0.0
    )

    scenarios_out: list[dict] = []
    for sc in cfg.scenarios:
        rows = by_scenario.get(sc.id, [])
        if not rows:
            continue
        best = min(rows, key=lambda x: x["metrics"]["stockout_probability"])
        single = next((x for x in rows if x["strategy_id"] == "single_source"), None)
        dual = next((x for x in rows if x["strategy_id"] == "dual_source"), None)
        air = next((x for x in rows if x["strategy_id"] == "emergency_airfreight"), None)

        dual_benefit = 0.0
        if single and dual:
            dual_benefit = single["metrics"]["stockout_probability"] - dual["metrics"]["stockout_probability"]

        vs_baseline = 0.0
        if sc.id != "BASELINE" and dual:
            vs_baseline = dual["metrics"]["stockout_probability"] - baseline_stockout

        scenario_row = {
            "scenario_id": sc.id,
            "name": sc.name,
            "description": sc.description,
            "severity": sc.severity,
            "category": sc.category,
            "duration_days": sc.duration_days,
            "shock": sc.shock,
            "recommended_strategy": best["strategy_id"],
            "recommendation_reason": _recommendation_reason(best, dual_benefit),
            "dual_source_benefit": round(dual_benefit, 3),
            "vs_baseline_stockout_delta": round(vs_baseline, 3),
            "strategies": rows,
        }
        analog = history_by_scenario.get(sc.id)
        if analog:
            scenario_row.update(analog)
        scenarios_out.append(scenario_row)

    heatmap = []
    for sc_id, rows in by_scenario.items():
        for r in rows:
            heatmap.append(
                {
                    "scenario_id": sc_id,
                    "strategy_id": r["strategy_id"],
                    "stockout_probability": r["metrics"]["stockout_probability"],
                    "service_level_pct": r["metrics"]["service_level_pct"],
                }
            )

    return {
        "disclaimer": "SimPy Monte Carlo demo — illustrative disruption modeling, not MSIL production planning.",
        "monte_carlo_runs": sim_results[0]["metrics"]["monte_carlo_runs"] if sim_results else 30,
        "catalog": catalog,
        "scenarios": scenarios_out,
        "heatmap": heatmap,
        "strategy_legend": {
            "single_source": "100% volume to incumbent — lowest logistics cost",
            "dual_source": "Split volume across two qualified suppliers",
            "emergency_airfreight": "Expedited lane — lower stockout, highest cost",
        },
    }


def _recommendation_reason(best: dict, dual_benefit: float) -> str:
    sid = best["strategy_id"]
    prob = best["metrics"]["stockout_probability"]
    if sid == "dual_source" and dual_benefit > 0.05:
        return f"Dual sourcing cuts stockout risk by {(dual_benefit * 100):.0f} pts vs single source."
    if sid == "emergency_airfreight":
        return "Emergency lane minimizes stockouts for critical launch or safety stock recovery."
    if prob < 0.1:
        return "Single source remains adequate under this shock severity."
    return "Lowest simulated stockout probability among strategies."
