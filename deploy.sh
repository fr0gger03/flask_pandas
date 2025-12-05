#!/bin/bash
# Main deployment script
# Usage: ./deploy.sh <environment> <command>
# Example: ./deploy.sh production up -d

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Validate arguments
if [ $# -lt 2 ]; then
    echo "Usage: ./deploy.sh <environment> <command>"
    echo ""
    echo "Environments: local, production, dhi"
    echo "Commands: up, down, ps, logs, etc."
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh local up"
    echo "  ./deploy.sh production up -d"
    echo "  ./deploy.sh production logs -f app"
    exit 1
fi

ENV=$1
shift

VALID_ENVS=("local" "production" "dhi")
if [[ ! " ${VALID_ENVS[@]} " =~ " ${ENV} " ]]; then
    echo "Error: Invalid environment '${ENV}'"
    echo "Valid environments: ${VALID_ENVS[*]}"
    exit 1
fi

# Check environment file exists
if [ ! -f "envs/${ENV}.env" ]; then
    echo "Error: Environment file envs/${ENV}.env not found"
    exit 1
fi

# Check compose file exists (skip for local as it uses compose.override.yaml)
if [ "$ENV" != "local" ]; then
    if [ ! -f "compose.${ENV}.yaml" ]; then
        echo "Error: Compose file compose.${ENV}.yaml not found"
        exit 1
    fi
fi

echo "Deploying ${ENV} environment..."

# Check 1Password CLI for non-local environments
if [ "$ENV" != "local" ]; then
    if ! command -v op > /dev/null 2>&1; then
        echo "Error: 1Password CLI not found"
        echo "Install from: https://1password.com/downloads/command-line/"
        exit 1
    fi
    
    if ! op account list > /dev/null 2>&1; then
        echo "Error: 1Password CLI not signed in"
        echo "Run: op signin"
        exit 1
    fi
    
    # Use 1Password to inject secrets
    op run --env-file="envs/${ENV}.env" -- \
        docker compose -f compose.yaml -f compose.${ENV}.yaml "$@"
else
    # Local environment - uses compose.override.yaml automatically
    docker compose --env-file="envs/${ENV}.env" "$@"
fi
