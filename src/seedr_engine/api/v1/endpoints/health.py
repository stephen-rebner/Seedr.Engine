from __future__ import annotations

from fastapi import APIRouter

from seedr_engine.models.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """Return the health status of the service."""
    return HealthResponse(status="ok")
