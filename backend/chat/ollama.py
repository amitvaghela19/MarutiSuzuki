"""Ollama HTTP client for local free LLM chat."""

from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator
from typing import Any

import httpx

from backend.settings import settings

_OPEN_THINK = "<" + "think" + ">"
_CLOSE_THINK = "<" + "/" + "think" + ">"
_THINK_RE = re.compile(
    re.escape(_OPEN_THINK) + r".*?" + re.escape(_CLOSE_THINK),
    re.DOTALL | re.IGNORECASE,
)


def strip_reasoning_tags(text: str) -> str:
    """Remove DeepSeek-R1 style reasoning blocks from assistant text."""
    cleaned = _THINK_RE.sub("", text).strip()
    lower = cleaned.lower()
    if _OPEN_THINK in lower and _CLOSE_THINK not in lower:
        idx = lower.find(_OPEN_THINK)
        cleaned = cleaned[:idx].strip()
    return cleaned or text.strip()


async def ollama_status() -> dict[str, Any]:
    base = settings.ollama_base_url.rstrip("/")
    model = settings.ollama_model
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{base}/api/tags")
            r.raise_for_status()
            names = [m.get("name", "") for m in r.json().get("models", [])]
    except Exception as exc:
        return {
            "available": False,
            "base_url": base,
            "configured_model": model,
            "error": str(exc),
            "models": [],
        }

    model_ok = model in names or any(
        names and (model.split(":")[0] in n or n.startswith(model.split(":")[0]))
        for n in names
    )
    return {
        "available": True,
        "base_url": base,
        "configured_model": model,
        "model_ready": model_ok,
        "models": names,
        "hint": None
        if model_ok
        else f"Run: ollama pull {model.split(':')[0]}",
    }


async def chat_complete(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
) -> dict[str, Any]:
    base = settings.ollama_base_url.rstrip("/")
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
        r = await client.post(f"{base}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    content = (data.get("message") or {}).get("content", "")
    return {
        "content": strip_reasoning_tags(content),
        "raw_content": content,
        "model": data.get("model", payload["model"]),
        "done": data.get("done", True),
    }


async def chat_stream(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    base = settings.ollama_base_url.rstrip("/")
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": True,
    }
    buffer = ""
    finished = False
    async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
        async with client.stream("POST", f"{base}/api/chat", json=payload) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                piece = (chunk.get("message") or {}).get("content", "")
                if piece:
                    buffer += piece
                    yield {
                        "done": False,
                        "delta": piece,
                        "content": strip_reasoning_tags(buffer),
                    }
                if chunk.get("done"):
                    finished = True
                    yield {"done": True, "content": strip_reasoning_tags(buffer)}
            if buffer and not finished:
                yield {"done": True, "content": strip_reasoning_tags(buffer)}
