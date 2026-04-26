from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from seedr_engine.api.v1.router import v1_router
from seedr_engine.core.config import settings
from seedr_engine.core.exceptions import SeedrEngineError

logging.basicConfig(level=settings.log_level)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="Seedr Engine",
        description="AI service that generates structured seed data for database tables.",
        version="0.1.0",
    )

    application.include_router(v1_router, prefix="/api/v1")

    @application.exception_handler(SeedrEngineError)
    async def seedr_engine_error_handler(
        request: Request, exc: SeedrEngineError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": exc.title,
                "status": exc.status_code,
                "detail": exc.detail,
            },
        )

    return application


app = create_app()
