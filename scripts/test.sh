#!/bin/bash
# Run tests with test environment

# Load test environment
set -a
source envs/test.env
set +a

# Ensure dependencies are synced
uv sync --frozen

# Run pytest with all arguments passed through
uv run python -m pytest "$@"
