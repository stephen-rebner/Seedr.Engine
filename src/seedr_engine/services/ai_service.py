from __future__ import annotations

import json
import logging

import anthropic

from seedr_engine.core.config import settings
from seedr_engine.core.exceptions import AIServiceError, RowLimitExceededError
from seedr_engine.models.requests import GenerateRequest
from seedr_engine.models.responses import GenerateResponse
from seedr_engine.services.prompt_builder import build_system_prompt, build_user_prompt

logger = logging.getLogger(__name__)


async def generate_seed_data(request: GenerateRequest) -> GenerateResponse:
    """Call Claude to generate seed data and return a validated GenerateResponse.

    Raises:
        RowLimitExceededError: if row_count exceeds the configured maximum.
        AIServiceError: if Claude returns malformed or unexpected data.
    """
    if request.row_count > settings.max_rows_per_request:
        raise RowLimitExceededError(
            requested=request.row_count,
            maximum=settings.max_rows_per_request,
        )

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(request)

    logger.debug("Sending prompt to Claude model '%s'.", settings.claude_model)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        message = await client.messages.create(
            model=settings.claude_model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.APIError as exc:
        logger.error("Anthropic API error: %s", exc)
        raise AIServiceError(f"Anthropic API call failed: {exc}") from exc

    raw_text = message.content[0].text if message.content else ""

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Claude returned non-JSON content: %s", raw_text)
        raise AIServiceError("Claude returned content that is not valid JSON.") from exc

    if "table_name" not in data or "rows" not in data:
        raise AIServiceError(
            "Claude response is missing required keys 'table_name' and/or 'rows'."
        )

    if not isinstance(data["rows"], list):
        raise AIServiceError("Claude response 'rows' field is not a list.")

    try:
        return GenerateResponse(table_name=data["table_name"], rows=data["rows"])
    except Exception as exc:
        raise AIServiceError(f"Failed to parse Claude response into expected model: {exc}") from exc
