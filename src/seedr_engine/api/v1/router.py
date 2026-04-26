from __future__ import annotations

from fastapi import APIRouter

from seedr_engine.api.v1.endpoints.generate import router as generate_router
from seedr_engine.api.v1.endpoints.health import router as health_router

v1_router = APIRouter()

v1_router.include_router(health_router)
v1_router.include_router(generate_router)
