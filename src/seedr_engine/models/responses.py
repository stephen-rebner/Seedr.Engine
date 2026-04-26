from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GenerateResponse(BaseModel):
    """Response body for POST /api/v1/generate."""

    table_name: str = Field(..., description="Name of the database table.")
    rows: list[dict[str, Any]] = Field(
        ..., description="Generated rows as a list of column-value mappings."
    )


class HealthResponse(BaseModel):
    """Response body for GET /api/v1/health."""

    status: str = Field(default="ok", description="Service health status.")
