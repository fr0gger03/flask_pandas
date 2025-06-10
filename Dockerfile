FROM python:3.13-alpine AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Tell uv to use the system Python
ENV UV_PYTHON_PREFERENCE=only-system
# Set Flask app location
ENV FLASK_APP=parser/app.py

# Set uv cache directory to a writable location
ENV UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (as root to avoid permission issues)
# excludes dev dependencies
RUN uv sync --frozen --no-dev

# Copy application code and tests
COPY ./parser ./parser

RUN chown -R appuser:appuser /app && \
chown -R appuser:appuser /tmp/uv-cache 2>/dev/null || true

EXPOSE 5001

FROM base AS test
# USER root
# Include dev dependencies for test
# COPY ./tests ./tests
# RUN uv sync --frozen

# Fix permissions again
# RUN chown -R appuser:appuser /app && \
# chown -R appuser:appuser /tmp/uv-cache 2>/dev/null || true
# USER appuser
CMD ["uv", "run", "flask", "run", "--debug", "--host=0.0.0.0"]

FROM base AS prod
USER appuser
CMD ["uv", "run", "flask", "run", "--host=0.0.0.0"]
