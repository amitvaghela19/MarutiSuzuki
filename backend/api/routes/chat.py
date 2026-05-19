"""Supply-chain assistant chat (Ollama / DeepSeek R1)."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.chat.context import build_system_prompt, load_latest_snapshot
from backend.chat.enrichment import build_live_enrichment
from backend.chat.ollama import chat_complete, chat_stream, ollama_status
from backend.settings import settings

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    stream: bool = True
    include_snapshot: bool = True


@router.get("/chat/status")
async def chat_status():
    return await ollama_status()


@router.post("/chat")
async def chat(req: ChatRequest):
    status = await ollama_status()
    if not status.get("available"):
        raise HTTPException(
            status_code=503,
            detail=status.get("error") or "Ollama is not running. Start it with: ollama serve",
        )
    if not status.get("model_ready"):
        raise HTTPException(
            status_code=503,
            detail=status.get("hint") or f"Model {status.get('configured_model')} not found in Ollama",
        )

    snapshot = load_latest_snapshot() if req.include_snapshot else None
    last_user = next(
        (m.content for m in reversed(req.messages) if m.role == "user"),
        "",
    )
    live = ""
    if req.include_snapshot and settings.chat_live_enrichment_enabled:
        try:
            live = await build_live_enrichment(last_user, snapshot)
        except Exception:
            live = ""
    system = build_system_prompt(snapshot, last_user, live)
    ollama_messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for m in req.messages:
        if m.role == "system":
            continue
        ollama_messages.append({"role": m.role, "content": m.content})

    if not any(m["role"] == "user" for m in ollama_messages):
        raise HTTPException(status_code=400, detail="At least one user message is required")

    if req.stream:

        async def event_gen():
            try:
                async for chunk in chat_stream(ollama_messages):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as exc:
                yield f"data: {json.dumps({'error': str(exc), 'done': True})}\n\n"

        return StreamingResponse(
            event_gen(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    try:
        result = await chat_complete(ollama_messages)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc

    return {
        "message": {"role": "assistant", "content": result["content"]},
        "model": result.get("model"),
        "has_snapshot": snapshot is not None,
    }
