from __future__ import annotations

import json

import pytest

from seedr_engine.models.requests import ColumnSchema, GenerateRequest, TableSchema
from seedr_engine.services.prompt_builder import build_system_prompt, build_user_prompt


@pytest.fixture
def sample_request() -> GenerateRequest:
    return GenerateRequest(
        instruction="populate with Spanish names",
        table_schema=TableSchema(
            table_name="customers",
            columns=[
                ColumnSchema(name="id", type="integer", nullable=False),
                ColumnSchema(name="first_name", type="varchar(100)", nullable=False),
                ColumnSchema(name="email", type="varchar(255)", nullable=True),
            ],
        ),
        row_count=5,
    )


def test_system_prompt_contains_key_instructions() -> None:
    """The system prompt includes the critical rules Claude must follow."""
    prompt = build_system_prompt()

    assert "database seed-data generator" in prompt.lower() or "seed-data generator" in prompt
    assert "nullable" in prompt.lower()
    assert "JSON" in prompt
    assert "table_name" in prompt
    assert "rows" in prompt


def test_user_prompt_contains_instruction(sample_request: GenerateRequest) -> None:
    """The user prompt embeds the caller's instruction."""
    prompt = build_user_prompt(sample_request)

    assert sample_request.instruction in prompt


def test_user_prompt_contains_table_name(sample_request: GenerateRequest) -> None:
    """The user prompt includes the table name."""
    prompt = build_user_prompt(sample_request)

    assert "customers" in prompt


def test_user_prompt_contains_column_names(sample_request: GenerateRequest) -> None:
    """The user prompt lists all column names."""
    prompt = build_user_prompt(sample_request)

    for col in sample_request.table_schema.columns:
        assert col.name in prompt


def test_user_prompt_contains_row_count(sample_request: GenerateRequest) -> None:
    """The user prompt specifies the required row count."""
    prompt = build_user_prompt(sample_request)

    assert str(sample_request.row_count) in prompt


def test_user_prompt_schema_is_valid_json_embedded(sample_request: GenerateRequest) -> None:
    """The user prompt embeds the schema as valid JSON."""
    prompt = build_user_prompt(sample_request)

    # Extract the JSON block — it starts after "Full schema (JSON):\n"
    marker = "Full schema (JSON):\n"
    start = prompt.index(marker) + len(marker)
    # Everything from the marker until the next "\n\n" section separator
    json_block = prompt[start:].split("\n\nGenerate exactly")[0].strip()

    parsed = json.loads(json_block)
    assert parsed["table_name"] == "customers"
    assert len(parsed["columns"]) == 3


def test_user_prompt_not_nullable_column_marked_correctly(
    sample_request: GenerateRequest,
) -> None:
    """NOT NULL columns are clearly indicated in the prompt."""
    prompt = build_user_prompt(sample_request)

    assert "NOT NULL" in prompt
