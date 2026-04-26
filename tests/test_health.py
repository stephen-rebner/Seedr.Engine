from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(async_client: AsyncClient) -> None:
    """GET /api/v1/health returns 200 with status 'ok'."""
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_content_type_is_json(async_client: AsyncClient) -> None:
    """GET /api/v1/health returns a JSON content-type header."""
    response = await async_client.get("/api/v1/health")

    assert "application/json" in response.headers["content-type"]
