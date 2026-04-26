from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ColumnSchema(BaseModel):
    """Represents a single column in a database table schema."""

    name: str = Field(..., description="Column name.")
    type: str = Field(..., description="SQL data type, e.g. 'varchar(100)', 'integer'.")
    nullable: bool = Field(default=True, description="Whether the column allows NULL values.")


class TableSchema(BaseModel):
    """Represents the schema of a single database table."""

    table_name: str = Field(..., description="Name of the database table.")
    columns: list[ColumnSchema] = Field(
        ..., min_length=1, description="List of column definitions."
    )


class GenerateRequest(BaseModel):
    """Request body for POST /api/v1/generate."""

    model_config = {"populate_by_name": True}

    instruction: str = Field(
        ...,
        min_length=1,
        description="Natural-language instruction describing the desired seed data.",
    )
    table_schema: TableSchema = Field(
        ...,
        alias="schema",
        description="Database table schema.",
    )
    row_count: int = Field(
        default=10,
        ge=1,
        description="Number of rows to generate.",
    )

    @model_validator(mode="after")
    def instruction_not_blank(self) -> "GenerateRequest":
        if not self.instruction.strip():
            raise ValueError("instruction must not be blank.")
        return self

