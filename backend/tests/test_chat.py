import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.chat.context import build_snapshot_context, build_system_prompt
from backend.chat.ollama import strip_reasoning_tags
from backend.main import app


def test_strip_reasoning_tags():
    open_t = "<" + "think" + ">"
    close_t = "<" + "/" + "think" + ">"
    raw = open_t + "reasoning here" + close_t + "Final answer."
    assert strip_reasoning_tags(raw) == "Final answer."


def test_build_system_prompt_without_snapshot():
    prompt = build_system_prompt(None)
    assert "No analysis run" in build_snapshot_context(None)
    assert "CONNECT THE DOTS" in prompt


@pytest.mark.asyncio
async def test_ollama_status_mock():
    from backend.chat.ollama import ollama_status

    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json = lambda: {"models": [{"name": "deepseek-r1:latest"}]}

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("backend.chat.ollama.httpx.AsyncClient", return_value=mock_client):
        status = await ollama_status()
    assert status["available"] is True
    assert status["model_ready"] is True


def test_chat_status_endpoint_mock():
    client = TestClient(app)
    with patch(
        "backend.api.routes.chat.ollama_status",
        new_callable=AsyncMock,
        return_value={
            "available": True,
            "model_ready": True,
            "configured_model": "deepseek-r1:latest",
            "base_url": "http://127.0.0.1:11434",
            "models": ["deepseek-r1:latest"],
        },
    ):
        r = client.get("/api/chat/status")
    assert r.status_code == 200
    assert r.json()["model_ready"] is True


def test_chat_non_stream_mock():
    client = TestClient(app)
    with (
        patch(
            "backend.api.routes.chat.ollama_status",
            new_callable=AsyncMock,
            return_value={
                "available": True,
                "model_ready": True,
                "configured_model": "deepseek-r1:latest",
                "base_url": "http://127.0.0.1:11434",
                "models": [],
            },
        ),
        patch(
            "backend.api.routes.chat.chat_complete",
            new_callable=AsyncMock,
            return_value={"content": "Hello from mock", "model": "deepseek-r1:latest"},
        ),
        patch("backend.api.routes.chat.load_latest_snapshot", return_value=None),
        patch("backend.api.routes.chat.build_live_enrichment", new_callable=AsyncMock, return_value=""),
    ):
        r = client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": False,
            },
        )
    assert r.status_code == 200
    assert r.json()["message"]["content"] == "Hello from mock"
