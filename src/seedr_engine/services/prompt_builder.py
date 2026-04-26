from __future__ import annotations

import json

from seedr_engine.models.requests import GenerateRequest
from seedr_engine.models.responses import GenerateResponse


def build_system_prompt() -> str:
    """Return the system prompt that instructs Claude how to behave."""
    return (
        "You are a database seed-data generator.\n"
        "Your task is to produce realistic, synthetic rows for a database table.\n\n"
        "Rules you MUST follow:\n"
        "1. Honour every column name and SQL type constraint from the schema provided.\n"
        "2. Respect nullability: never produce NULL for a non-nullable column.\n"
        "3. Apply the user's instruction to the relevant columns only; leave other columns "
        "unaffected.\n"
        "4. Respect SQL type length constraints (e.g. a varchar(10) value must be ≤ 10 "
        "characters).\n"
        "5. Return ONLY a valid JSON object — no prose, no markdown fences, no extra keys.\n"
        "6. The JSON object must have exactly two keys:\n"
        '   - "table_name": the table name (string)\n'
        '   - "rows": an array of objects, one per row, where each object maps column names '
        "to values.\n"
    )


def build_user_prompt(request: GenerateRequest) -> str:
    """Return the user-facing prompt from a GenerateRequest."""
    columns_description = "\n".join(
        f"  - {col.name} ({col.type}, {'NOT NULL' if not col.nullable else 'nullable'})"
        for col in request.table_schema.columns
    )

    schema_json = json.dumps(
        {
            "table_name": request.table_schema.table_name,
            "columns": [col.model_dump() for col in request.table_schema.columns],
        },
        indent=2,
    )

    return (
        f"Instruction: {request.instruction}\n\n"
        f"Table: {request.table_schema.table_name}\n"
        f"Columns:\n{columns_description}\n\n"
        f"Full schema (JSON):\n{schema_json}\n\n"
        f"Generate exactly {request.row_count} rows.\n"
        "Return ONLY the JSON object described in the system prompt."
    )
