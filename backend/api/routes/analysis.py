import asyncio

from fastapi import APIRouter, HTTPException

from backend.analytics.pipeline import run_full_analysis

router = APIRouter(tags=["analysis"])

_analysis_lock = asyncio.Lock()


@router.post("/run-analysis")
async def run_analysis():
    if _analysis_lock.locked():
        raise HTTPException(
            status_code=409,
            detail="Analysis already in progress. Wait for it to finish or restart the API.",
        )
    async with _analysis_lock:
        try:
            return await run_full_analysis()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
