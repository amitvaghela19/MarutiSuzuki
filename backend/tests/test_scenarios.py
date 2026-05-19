from backend.analytics.simulation import build_scenario_insights, run_scenarios
from backend.config.loader import load_config


def test_run_scenarios_three_strategies():
    cfg = load_config()
    results = run_scenarios(cfg, {}, monte_carlo_runs=5)
    assert len(results) == len(cfg.scenarios) * 3
    strategies = {r["strategy_id"] for r in results}
    assert "emergency_airfreight" in strategies
    assert results[0]["metrics"]["service_level_pct"] >= 0


def test_scenario_insights_structure():
    cfg = load_config()
    results = run_scenarios(cfg, {"SUP-IN-STEEL": 55.0}, monte_carlo_runs=5)
    insights = build_scenario_insights(cfg, results)
    assert len(insights["catalog"]) == len(cfg.scenarios)
    assert insights["scenarios"]
    assert insights["heatmap"]
    assert insights["scenarios"][0]["recommended_strategy"]
