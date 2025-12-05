#!/bin/bash
# Run tests in CI with 1Password secrets (if needed)

set -e

echo "Running tests with 1Password integration..."

# Ensure dependencies are synced
echo "Syncing dependencies with uv..."
uv sync --frozen

# Check if 1Password CLI is available
if command -v op > /dev/null 2>&1; then
    echo "Using 1Password for secret injection..."
    op run --env-file="envs/test.env" -- uv run python -m pytest "$@"
else
    echo "1Password CLI not found, using local environment..."
    set -a
    source envs/test.env
    set +a
    uv run python -m pytest "$@"
fi
