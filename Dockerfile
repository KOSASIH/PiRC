# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM python:3.11-slim@sha256:6d99c8d7a5b6f9c5a8b8c8d7a5b6f9c5a8b8c8d7a5b6f9c5a8b8c8d7a5b6f9c5 as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 pirc && \
    adduser --system --uid 1001 --ingroup pirc pirc

# Copy pyproject.toml and poetry.lock first
COPY --chown=pirc:pirc pyproject.toml poetry.lock* ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==1.8.2 && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    poetry cache clear --no-interaction pypi && \
    rm -rf ~/.cache

# Copy source code
COPY --chown=pirc:pirc src/ ./src/

# Create runtime directories
RUN mkdir -p /app/data /app/logs && \
    chown -R pirc:pirc /app

USER pirc

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import redis.asyncio; redis.asyncio.from_url('redis://localhost').ping()"

EXPOSE 8080 9090
CMD ["python", "-m", "pirc.main"]
