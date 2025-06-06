FROM python:3.13.23-alpine AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Tell uv to use the system Python
ENV UV_PYTHON_PREFERENCE=only-system
# Set Flask app location
ENV FLASK_APP=app.py

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
RUN uv sync --frozen --no-dev

# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

COPY parser/ .
# RUN chown -R appuser:appuser .  && chmod -R 1777 .
RUN chown -R appuser:appuser /app && \
    chown -R appuser:appuser /tmp/uv-cache 2>/dev/null || true

USER appuser
EXPOSE 5000

# FROM base AS test
# CMD [ "python", "-m" , "flask", "run", "--debug", "--host=0.0.0.0"]

# FROM base AS prod
# CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]

FROM base AS test
# Include dev dependencies for test
USER root
RUN uv sync --frozen
# Fix permissions again
RUN chown -R appuser:appuser /app && \
    chown -R appuser:appuser /tmp/uv-cache 2>/dev/null || true
USER appuser
CMD ["uv", "run", "flask", "run", "--debug", "--host=0.0.0.0"]

FROM base AS prod
CMD ["uv", "run", "flask", "run", "--host=0.0.0.0"]
