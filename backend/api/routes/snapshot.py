import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.settings import settings

router = APIRouter(tags=["snapshot"])


@router.get("/snapshot/latest")
def latest_snapshot():
    path = settings.snapshots_dir / "latest.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No analysis run yet. POST /api/run-analysis first.")
    return json.loads(path.read_text(encoding="utf-8"))
