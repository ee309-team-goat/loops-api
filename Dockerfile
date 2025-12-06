# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the project
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Runtime stage
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Create non-root user FIRST (before COPY --chown)
RUN useradd -m -u 1000 app

# Copy the application from builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Set PYTHONPATH to include src directory
ENV PYTHONPATH="/app/src"

# Switch to non-root user
USER app

# Expose port (Cloud Run uses PORT env var, default 8000)
EXPOSE 8000

# Cloud Run sets PORT env var, default to 8000
ENV PORT=8000

# Run the application with uvicorn
# Use shell form to allow $PORT expansion
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
