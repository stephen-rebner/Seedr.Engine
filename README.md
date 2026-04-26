# Seedr.Engine

AI-powered database seed data generator. Accepts natural-language prompts and a database schema,
then returns structured rows suitable for seeding database tables — powered by Anthropic's Claude.

---

## Prerequisites

- Python 3.12+
- An [Anthropic API key](https://console.anthropic.com/)
- Docker & Docker Compose (optional, for containerised deployment)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/stephen-rebner/Seedr.Engine.git
cd Seedr.Engine
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your `ANTHROPIC_API_KEY`:

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-6
MAX_ROWS_PER_REQUEST=100
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## Running Locally

```bash
uvicorn seedr_engine.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at <http://localhost:8000>.
Interactive docs: <http://localhost:8000/docs>

---

## Running with Docker

```bash
docker-compose up --build
```

This reads environment variables from your `.env` file and maps port 8000.

---

## API Reference

### `GET /api/v1/health`

Returns the service health status.

**Response**
```json
{ "status": "ok" }
```

---

### `POST /api/v1/generate`

Generates seed data rows from a natural-language instruction and table schema.

**Request body**
```json
{
  "instruction": "populate this customer records table with Spanish names",
  "schema": {
    "table_name": "customers",
    "columns": [
      { "name": "id",         "type": "integer",      "nullable": false },
      { "name": "first_name", "type": "varchar(100)", "nullable": false },
      { "name": "last_name",  "type": "varchar(100)", "nullable": false },
      { "name": "email",      "type": "varchar(255)", "nullable": false },
      { "name": "created_at", "type": "timestamp",    "nullable": false }
    ]
  },
  "row_count": 10
}
```

**Response**
```json
{
  "table_name": "customers",
  "rows": [
    {
      "id": 1,
      "first_name": "Alejandro",
      "last_name": "García",
      "email": "alejandro.garcia@example.com",
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

---

## Running Tests

```bash
pytest
```

Tests use a mocked Anthropic SDK — no real API calls are made.

---

## Project Structure

```
seedr-engine/
  src/
    seedr_engine/
      main.py                  ← FastAPI app factory + exception handler
      api/v1/
        router.py              ← mounts all v1 sub-routers
        endpoints/
          generate.py          ← POST /api/v1/generate
          health.py            ← GET /api/v1/health
      core/
        config.py              ← pydantic-settings configuration
        exceptions.py          ← custom exception classes
      models/
        requests.py            ← Pydantic request models
        responses.py           ← Pydantic response models
      services/
        ai_service.py          ← Anthropic SDK integration
        prompt_builder.py      ← builds system + user prompts
  tests/
    conftest.py                ← fixtures, TestClient, Anthropic mock
    test_generate.py
    test_health.py
    test_prompt_builder.py
  Dockerfile
  docker-compose.yml
  pyproject.toml
  .env.example
```