from __future__ import annotations


class SeedrEngineError(Exception):
    """Base exception for all Seedr Engine domain errors."""

    status_code: int = 500
    title: str = "Internal Server Error"

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class BadRequestError(SeedrEngineError):
    """Raised when the request is invalid or cannot be processed."""

    status_code = 400
    title = "Bad Request"


class AIServiceError(SeedrEngineError):
    """Raised when the AI service returns an unexpected or malformed response."""

    status_code = 502
    title = "Bad Gateway"


class RowLimitExceededError(BadRequestError):
    """Raised when the requested row count exceeds the configured maximum."""

    def __init__(self, requested: int, maximum: int) -> None:
        super().__init__(
            f"Requested {requested} rows but the maximum allowed is {maximum}."
        )
