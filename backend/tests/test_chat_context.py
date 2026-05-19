"""Rich chat context must include quantified tyre/MRF data when present in snapshot."""

from backend.chat.context import build_snapshot_context, build_system_prompt

_SNAPSHOT_STUB = {
    "run_id": "50373b22-87fd-430d-8e20-3473ded07f92",
    "generated_at": "2026-05-17T12:00:00+00:00",
    "supplier_risks": [
        {
            "id": "SUP-IN-TIRE",
            "score": 21.1,
            "components": {"country_risk": 28.5, "commodity_risk": 13.1, "lead_time": 10},
        },
        {
            "id": "SUP-AE-GULF-CHEM",
            "score": 39.0,
            "components": {"country_risk": 40, "commodity_risk": 15, "lead_time": 32},
        },
    ],
    "suppliers": [
        {
            "id": "SUP-IN-TIRE",
            "name": "MRF Tyres India (OEM contract)",
            "country": "IN",
            "country_name": "India",
            "city": "Chennai",
            "lead_time_days": 10,
            "commodities": ["rubber", "tires"],
        },
        {
            "id": "SUP-AE-GULF-CHEM",
            "name": "Gulf Petrochemical Feedstock (UAE corridor)",
            "country": "AE",
            "country_name": "United Arab Emirates",
            "lead_time_days": 32,
            "commodities": ["rubber", "chemicals"],
        },
    ],
    "recommendations": [
        {
            "part_id": "PART-TIRE",
            "part_name": "OEM tire set",
            "allocation": {"SUP-IN-TIRE": 0.428, "SUP-MY-RUBBER": 0.452, "SUP-TH-RUBBER": 0.12},
            "allocation_mode": "multi_source",
            "primary_supplier_id": "SUP-IN-TIRE",
            "rationale": {
                "drivers": ["dual_source: scenario stockout P=100% exceeds 25% limit"],
                "max_scenario_stockout": 1.0,
                "topsis_rank": 1,
            },
            "supplier_risks": {"SUP-IN-TIRE": 21.1, "SUP-MY-RUBBER": 19.3},
            "alternative_solutions": [
                "Gulf (UAE / Saudi) synthetic rubber & carbon black — Red Sea routing risk"
            ],
        }
    ],
    "sim_results": [
        {
            "scenario_id": "ME-GULF-TIRE",
            "scenario_name": "Middle East / Gulf tyre supply shock",
            "strategy_id": "dual_source",
            "metrics": {
                "stockout_probability": 1.0,
                "service_level_pct": 45.0,
                "recovery_days_est": 50,
                "lead_time_multiplier": 2.25,
            },
        }
    ],
    "tire_disruption_brief": {
        "stress_level": "high",
        "headline": "MRF / Gulf tyre supply watch",
        "summary": "MRF programme + Gulf feedstock.",
        "bullets": ["stockout probability 100% in Gulf scenario"],
        "mrf_supplier": {"id": "SUP-IN-TIRE", "name": "MRF Tyres India", "risk_score": 21.1},
        "gulf_feedstock": [{"id": "SUP-AE-GULF-CHEM", "name": "Gulf Petrochemical", "risk_score": 39}],
    },
    "fear_greed": {
        "maruti_suzuki": {
            "id": "MARUTI-SZKI",
            "fear_index": 47,
            "greed_index": 52,
            "sentiment_label": "Neutral",
            "drivers": ["Simulation stockout stress: 100%"],
        },
        "suppliers": [
            {
                "id": "SUP-IN-TIRE",
                "fear_index": 30,
                "greed_index": 55,
                "sentiment_label": "Greed",
                "part_exposure_weight": 2.1,
                "drivers": ["Rubber commodity stable"],
            }
        ],
    },
}


def test_tire_context_includes_quantified_metrics():
    ctx = build_snapshot_context(_SNAPSHOT_STUB, "What is MRF Gulf tyre risk?")
    assert "SUP-IN-TIRE" in ctx
    assert "21.1" in ctx
    assert "ME-GULF-TIRE" in ctx
    assert "stockout_P=100%" in ctx
    assert "0.428" in ctx or "42.8%" in ctx or "SUP-IN-TIRE: 42.8%" in ctx
    assert "MRF / Gulf tyre supply watch" in ctx


def test_system_prompt_forbids_empty_hand_waving():
    prompt = build_system_prompt(_SNAPSHOT_STUB, "MRF tyres", "LIVE: Yahoo Finance MRF.NS: ₹100000")
    assert "NEVER say" in prompt and "data not provided" in prompt
    assert "TYRE / MRF / GULF" in prompt
    assert "Yahoo Finance" in prompt
