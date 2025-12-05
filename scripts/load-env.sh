#!/bin/bash
# Load environment and inject 1Password secrets
# Usage: ./scripts/load-env.sh <environment> <docker-compose-args>

set -e

ENV=${1:-local}
shift  # Remove first argument

if [ ! -f "envs/${ENV}.env" ]; then
    echo "Error: Environment file envs/${ENV}.env not found"
    exit 1
fi

echo "Loading ${ENV} environment with 1Password..."

# Check if 1Password CLI is authenticated
if ! op account list > /dev/null 2>&1; then
    echo "Error: 1Password CLI not signed in. Run: op signin"
    exit 1
fi

# Determine which compose file to use
if [ "$ENV" = "local" ]; then
    # For local, use compose.override.yaml (or let it auto-load)
    COMPOSE_FILES="-f compose.yaml -f compose.override.yaml"
else
    # For other environments, use compose.<env>.yaml
    COMPOSE_FILES="-f compose.yaml -f compose.${ENV}.yaml"
fi

# Run docker compose with 1Password secret injection
op run --env-file="envs/${ENV}.env" -- \
    docker compose $COMPOSE_FILES "$@"
