from fastapi.testclient import TestClient

from backend.analytics.disruption_history import (
    build_disruption_history_payload,
    load_disruption_history_raw,
    scenario_history_analogs,
)
from backend.analytics.tire_brief import build_tire_disruption_brief
from backend.config.loader import load_config
from backend.main import app


def test_history_yaml_loads():
    raw = load_disruption_history_raw()
    incidents = raw.get("incidents") or []
    assert len(incidents) >= 4
    required = {
        "id",
        "year",
        "title",
        "category",
        "summary",
        "impact_bullets",
        "supply_chain_lesson",
        "source_label",
        "source_url",
    }
    for inc in incidents:
        missing = required - set(inc.keys())
        assert not missing, f"{inc.get('id')} missing {missing}"


def test_build_disruption_history_payload():
    payload = build_disruption_history_payload()
    assert payload["disclaimer"]
    assert len(payload["incidents"]) >= 4
    assert "timeline_summary" in payload
    assert "live_analog" in payload["incidents"][0]


def test_scenario_history_analogs():
    analogs = scenario_history_analogs()
    assert "CHIP-SHORTAGE" in analogs
    assert analogs["CHIP-SHORTAGE"]["historical_analog"]


def test_tire_brief():
    cfg = load_config()
    brief = build_tire_disruption_brief(cfg)
    assert brief["part_id"] == "PART-TIRE"
    assert brief["mrf_supplier"]["name"]
    assert brief["stress_level"] in ("low", "elevated", "high")


def test_disruptions_history_api():
    client = TestClient(app)
    r = client.get("/api/disruptions/history")
    assert r.status_code == 200
    data = r.json()
    assert len(data["incidents"]) >= 4
