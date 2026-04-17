FROM python:3.13-slim AS base
WORKDIR /app
RUN pip install uv

FROM base AS builder
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM base AS runtime
RUN adduser --disabled-password --gecos "" appuser
COPY --from=builder /app/.venv .venv
COPY app/ app/
COPY ui/ ui/
COPY alembic/ alembic/
COPY alembic.ini .
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
