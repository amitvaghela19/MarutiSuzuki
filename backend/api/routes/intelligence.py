from fastapi import APIRouter

from backend.analytics.ai_hub import build_ai_models_payload
from backend.analytics.command_signals import build_command_signals
from backend.analytics.digital_twin import build_digital_twin
from backend.analytics.disruption_history import build_disruption_history_payload
from backend.config.loader import load_config

router = APIRouter(tags=["intelligence"])


@router.get("/ai/models")
def ai_models():
    cfg = load_config()
    return build_ai_models_payload(cfg)


@router.get("/digital-twin/status")
def digital_twin_status():
    cfg = load_config()
    return build_digital_twin(cfg)


@router.get("/command/signals")
def command_signals():
    cfg = load_config()
    return build_command_signals(
        cfg,
        news=[],
        country_risk=[],
        supplier_risk=[],
        recs=[],
    )


@router.get("/disruptions/history")
def disruptions_history():
    return build_disruption_history_payload()
