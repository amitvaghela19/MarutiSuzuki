from fastapi import APIRouter

from backend.config.loader import load_config
from backend.db.repository import Repository
from backend.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/health/data-sources")
def data_sources_health():
    repo = Repository()
    return {"providers": repo.get_health_all()}


@router.get("/health/config")
def config_health():
    cfg = load_config()
    return {
        "suppliers": len(cfg.suppliers),
        "parts": len(cfg.parts),
        "scenarios": len(cfg.scenarios),
        "config_dir": str(settings.config_dir),
    }
