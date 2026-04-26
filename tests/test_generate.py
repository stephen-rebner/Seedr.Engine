from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import make_anthropic_response


@pytest.mark.asyncio
async def test_generate_success(
    async_client: AsyncClient,
    anthropic_mock: MagicMock,
    sample_generate_payload: dict[str, Any],
    sample_ai_response: dict[str, Any],
) -> None:
    """POST /api/v1/generate returns 200 with generated rows on a happy path."""
    anthropic_mock.messages.create.return_value = make_anthropic_response(sample_ai_response)

    response = await async_client.post("/api/v1/generate", json=sample_generate_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["table_name"] == "customers"
    assert len(body["rows"]) == 2
    assert body["rows"][0]["first_name"] == "Alejandro"


@pytest.mark.asyncio
async def test_generate_row_limit_exceeded(
    async_client: AsyncClient,
    sample_generate_payload: dict[str, Any],
) -> None:
    """POST /api/v1/generate returns 400 when row_count exceeds the maximum."""
    payload = {**sample_generate_payload, "row_count": 9999}

    response = await async_client.post("/api/v1/generate", json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["status"] == 400
    assert "maximum" in body["detail"].lower()


@pytest.mark.asyncio
async def test_generate_invalid_request_missing_instruction(
    async_client: AsyncClient,
    sample_generate_payload: dict[str, Any],
) -> None:
    """POST /api/v1/generate returns 422 when required fields are missing."""
    payload = {**sample_generate_payload}
    del payload["instruction"]

    response = await async_client.post("/api/v1/generate", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_ai_service_returns_malformed_json(
    async_client: AsyncClient,
    anthropic_mock: MagicMock,
    sample_generate_payload: dict[str, Any],
) -> None:
    """POST /api/v1/generate returns 502 when Claude returns non-JSON content."""
    content_block = type("Block", (), {"text": "this is not json"})()
    mock_response = type("Resp", (), {"content": [content_block]})()
    anthropic_mock.messages.create.return_value = mock_response

    response = await async_client.post("/api/v1/generate", json=sample_generate_payload)

    assert response.status_code == 502
    body = response.json()
    assert body["status"] == 502


@pytest.mark.asyncio
async def test_generate_ai_service_returns_missing_keys(
    async_client: AsyncClient,
    anthropic_mock: MagicMock,
    sample_generate_payload: dict[str, Any],
) -> None:
    """POST /api/v1/generate returns 502 when Claude JSON is missing required keys."""
    anthropic_mock.messages.create.return_value = make_anthropic_response(
        {"unexpected_key": "value"}
    )

    response = await async_client.post("/api/v1/generate", json=sample_generate_payload)

    assert response.status_code == 502
