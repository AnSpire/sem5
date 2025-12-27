FROM python:3.12-slim AS builder

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir uv


COPY pyproject.toml uv.lock ./


RUN uv sync --frozen



FROM python:3.12-slim

WORKDIR /app


COPY --from=builder /app/.venv /app/.venv


COPY . .


ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
