# Stage 1: builder
FROM python:3.13-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir hatchling

COPY README.md pyproject.toml ./
COPY src/ ./src/

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir .

# Stage 2: runtime
FROM python:3.13-slim AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /opt/venv /opt/venv
COPY src/ /app/src/

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

USER appuser

EXPOSE 8000

CMD ["uvicorn", "seedr_engine.main:app", "--host", "0.0.0.0", "--port", "8000"]
