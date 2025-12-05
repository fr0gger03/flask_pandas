#!/bin/bash
# Switch active environment by symlinking .env file
# Usage: ./switch-env.sh <environment>

set -e

ENV=$1

if [ -z "$ENV" ]; then
    echo "Usage: ./switch-env.sh <environment>"
    echo ""
    echo "Available environments:"
    ls -1 envs/*.env 2>/dev/null | sed 's/envs\///' | sed 's/.env$//'
    exit 1
fi

if [ ! -f "envs/${ENV}.env" ]; then
    echo "Error: Environment file envs/${ENV}.env not found"
    exit 1
fi

# Remove existing .env symlink or file
if [ -L ".env" ] || [ -f ".env" ]; then
    rm .env
fi

# Create symlink
ln -s "envs/${ENV}.env" .env

echo "Switched to ${ENV} environment"
echo "Active environment: .env -> envs/${ENV}.env"