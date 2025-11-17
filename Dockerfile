FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv first
RUN pip install --no-cache-dir uv

# Copy dependency files and README (needed for package metadata)
COPY pyproject.toml uv.lock* README.md ./

# Copy source code (needed for building the package)
COPY src/ ./src/

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev

# Install the package itself in editable mode so the module can be imported
RUN uv pip install -e .

# Install mcpo
RUN uv pip install mcpo

# Set environment variables to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Run mcpo with the intervals_icu_mcp server
CMD ["mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "python", "-m", "intervals_icu_mcp.server"]