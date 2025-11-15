# Multi-stage build for minimal final image
FROM --platform=$TARGETPLATFORM ghcr.io/astral-sh/uv:latest AS uv

FROM --platform=$TARGETPLATFORM python:3.11-slim AS builder

# Install uv for faster dependency management
COPY --from=uv /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files and README (needed for package metadata)
COPY pyproject.toml uv.lock* README.md ./

# Copy source code (needed for building the package)
COPY src/ ./src/

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev

# Install the package itself in editable mode so uvx can find it
RUN uv pip install -e .

# Install mcp-proxy
RUN uv pip install mcp-proxy

# Final stage - minimal runtime image
FROM --platform=$TARGETPLATFORM python:3.11-slim

# Install uv in final image (needed for uvx)
COPY --from=uv /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code and pyproject.toml
COPY src/ ./src/
COPY pyproject.toml ./
COPY README.md ./

# Create a simple wrapper script for the MCP server
RUN echo '#!/bin/sh\nexec python -m intervals_icu_mcp.server' > /usr/local/bin/run-mcp-server && \
    chmod +x /usr/local/bin/run-mcp-server

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Expose HTTP/SSE port
EXPOSE 8080

# Health check - verify HTTP endpoint is responding
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080').read()" || exit 1

# Run the MCP server through mcp-proxy with HTTP/SSE transport
# Using a wrapper script to avoid argument parsing issues
ENTRYPOINT ["mcp-proxy", "--port=8080", "--host=0.0.0.0", "--pass-environment", "run-mcp-server"]
