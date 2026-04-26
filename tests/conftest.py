from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure config loading never requires a real .env / environment."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    monkeypatch.setenv("MAX_ROWS_PER_REQUEST", "100")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("ENVIRONMENT", "development")


def _make_anthropic_response(payload: dict[str, Any]) -> MagicMock:
    """Build a fake Anthropic message response containing *payload* as JSON text."""
    content_block = MagicMock()
    content_block.text = json.dumps(payload)
    response = MagicMock()
    response.content = [content_block]
    return response


@pytest.fixture
def anthropic_mock() -> MagicMock:
    """Return a mock that replaces ``anthropic.AsyncAnthropic``."""
    mock_client = MagicMock()
    mock_client.messages = MagicMock()
    mock_client.messages.create = AsyncMock()
    return mock_client


@pytest.fixture
async def async_client(anthropic_mock: MagicMock) -> AsyncGenerator[AsyncClient, None]:
    """Return an HTTPX AsyncClient wired to the FastAPI app.

    The Anthropic SDK is patched so no real API calls are made.
    """
    with patch(
        "seedr_engine.services.ai_service.anthropic.AsyncAnthropic",
        return_value=anthropic_mock,
    ):
        from seedr_engine.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client


@pytest.fixture
def sample_generate_payload() -> dict[str, Any]:
    """A valid generate request payload."""
    return {
        "instruction": "populate with Spanish names",
        "schema": {
            "table_name": "customers",
            "columns": [
                {"name": "id", "type": "integer", "nullable": False},
                {"name": "first_name", "type": "varchar(100)", "nullable": False},
                {"name": "last_name", "type": "varchar(100)", "nullable": False},
                {"name": "email", "type": "varchar(255)", "nullable": False},
                {"name": "created_at", "type": "timestamp", "nullable": False},
            ],
        },
        "row_count": 2,
    }


@pytest.fixture
def sample_ai_response() -> dict[str, Any]:
    """A valid AI response payload that matches the generate request above."""
    return {
        "table_name": "customers",
        "rows": [
            {
                "id": 1,
                "first_name": "Alejandro",
                "last_name": "García",
                "email": "alejandro.garcia@example.com",
                "created_at": "2024-03-15T10:30:00Z",
            },
            {
                "id": 2,
                "first_name": "Sofía",
                "last_name": "Martínez",
                "email": "sofia.martinez@example.com",
                "created_at": "2024-03-16T09:00:00Z",
            },
        ],
    }


def make_anthropic_response(payload: dict[str, Any]) -> MagicMock:
    """Public alias used across test modules."""
    return _make_anthropic_response(payload)
