from __future__ import annotations

from fastapi import APIRouter

from seedr_engine.models.requests import GenerateRequest
from seedr_engine.models.responses import GenerateResponse
from seedr_engine.services.ai_service import generate_seed_data

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse, summary="Generate seed data")
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Accept a natural-language instruction and database schema, then return
    generated rows suitable for seeding the specified table.

    This endpoint does NOT persist any data — it returns the generated rows to
    the caller.
    """
    return await generate_seed_data(request)
