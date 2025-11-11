# Multi-Environment Docker Setup with 1Password
## Implementation Plan

---

## Overview

This plan restructures the project to support multiple environments (local, production, DHI) with:
- Centralized environment file management
- 1Password secret management integration
- Isolated test configuration
- Clean Docker Compose structure

---

## Phase 1: Restructure Environment Files

### 1.1 Create Environment Directory Structure

```bash
mkdir -p envs
```

### 1.2 Create Base Template File

Create `envs/.env.template` with all variables documented and placeholder values (no secrets).

**Action Items:**
- [ ] Copy current `.env.production.template` as starting point
- [ ] Document all environment variables with comments
- [ ] Use placeholder values like `your-secret-here`
- [ ] Include sections for: Flask, Database, Security, File Upload, Logging, Performance

### 1.3 Create Environment-Specific Files

Create three environment files:

**File: `envs/local.env`**
- Development settings
- Can include dev secrets (gitignored)
- Use localhost/docker service names
- Debug mode enabled

**File: `envs/production.env`**
- Production settings
- Use 1Password references for secrets
- Debug mode disabled
- Production database URLs

**File: `envs/dhi.env`**
- DHI environment settings
- Use 1Password references for secrets
- DHI-specific configurations

**Action Items:**
- [ ] Create `envs/local.env` with development values
- [ ] Create `envs/production.env` with 1Password references
- [ ] Create `envs/dhi.env` with 1Password references

### 1.4 Integrate 1Password Secret References

Replace sensitive values with 1Password references:

```bash
# Instead of:
SECRET_KEY=actual-secret-here

# Use:
SECRET_KEY=op://vault-name/item-name/field-name
```

**Example 1Password references:**
```bash
SECRET_KEY=op://Private/flask-pandas-production/SECRET_KEY
POSTGRES_PASSWORD=op://Private/flask-pandas-production/POSTGRES_PASSWORD
DATABASE_URL=op://Private/flask-pandas-production/DATABASE_URL
```

**Action Items:**
- [ ] Identify all sensitive variables
- [ ] Create 1Password reference syntax for each
- [ ] Document vault and item names

### 1.5 Update .gitignore

Add to `.gitignore`:

```gitignore
# Environment files (keep template only)
envs/*.env
!envs/.env.template
.env
.env.*
!.env.template
```

**Action Items:**
- [ ] Update `.gitignore`
- [ ] Verify existing `.env` files won't be committed

---

## Phase 2: Refactor Docker Compose Files

### 2.1 Create Base compose.yaml

Extract common configuration shared across all environments:

**Should include:**
- Service definitions (db, app, adminer)
- Common environment variables (non-sensitive)
- Base volumes and networks
- Service dependencies
- Health checks

**Should NOT include:**
- Environment-specific ports
- Environment-specific build targets
- Hardcoded secrets
- Environment-specific volume paths

**Action Items:**
- [ ] Review current `compose.yaml`
- [ ] Extract only common elements
- [ ] Replace hardcoded values with `${VAR_NAME}`
- [ ] Test that it requires environment file to work

### 2.2 Create Environment Override Files

Split environment-specific configs into separate files:

**File: `compose.override.yaml`**
- Local development overrides
- Auto-loaded by Docker Compose
- Development build target
- Port mappings for local access
- Hot-reload configuration

**File: `compose.production.yaml`**
- Production-specific config
- Production build target
- Resource limits
- Production logging
- No debug tools

**File: `compose.dhi.yaml`**
- DHI environment overrides
- DHI-specific Dockerfile
- DHI networking configuration

**Action Items:**
- [ ] Create `compose.override.yaml` from current `compose.yaml`
- [ ] Create `compose.production.yaml` from current `docker-compose.production.yml`
- [ ] Create `compose.dhi.yaml` from current `docker-compose.dhi.yaml`
- [ ] Remove all redundant config (keep only differences from base)

### 2.3 Remove Hardcoded Secrets

Replace all hardcoded values with environment variable references:

**Before:**
```yaml
environment:
  - SECRET_KEY=your-secret-key
  - DATABASE_URL=postgresql://user:password@db:5432/db
```

**After:**
```yaml
environment:
  - SECRET_KEY=${SECRET_KEY}
  - DATABASE_URL=${DATABASE_URL}
```

**Action Items:**
- [ ] Find all hardcoded secrets in compose files
- [ ] Replace with `${VAR_NAME}` syntax
- [ ] Verify variables exist in environment files

### 2.4 Clean Up Old Files

Move deprecated files to backup directory:

```bash
mkdir -p .deprecated
mv docker-compose.*.yaml .deprecated/
mv docker-compose.*.yml .deprecated/
mv .env.production .deprecated/
mv .env.production.template .deprecated/
```

**Action Items:**
- [ ] Create `.deprecated` directory
- [ ] Move old compose files
- [ ] Move old env files
- [ ] Update `.gitignore` to include `.deprecated/`

---

## Phase 2.5: Update Testing Infrastructure

### 2.5.1 Create Test Environment File

Create `envs/test.env`:

```bash
# Test environment - used by pytest
TESTING=True
FLASK_ENV=testing
SECRET_KEY=test-secret-key-not-for-production
DATABASE_URL=will-be-overridden-by-testcontainer
UPLOAD_FOLDER=tests/fixtures/uploads
MAX_CONTENT_LENGTH=1073741824
WTF_CSRF_ENABLED=False
PYTHONUNBUFFERED=1
```

**Action Items:**
- [ ] Create `envs/test.env`
- [ ] Include all required test variables
- [ ] Use safe default values (no real secrets)

### 2.5.2 Update conftest.py

Modify `tests/conftest.py` to load test environment:

**Add to top of file:**
```python
import os
from dotenv import load_dotenv
from pathlib import Path

# Load test environment at module level
test_env_path = Path(__file__).parent.parent / 'envs' / 'test.env'
if test_env_path.exists():
    load_dotenv(test_env_path, override=False)

# Rest of conftest.py remains the same...
```

**Key points:**
- Load environment once per test session
- `override=False` prevents overwriting test fixture values
- Test fixtures still control DATABASE_URL via testcontainer

**Action Items:**
- [ ] Add dotenv import and loading to `tests/conftest.py`
- [ ] Test that existing fixtures still work
- [ ] Verify DATABASE_URL is still overridden by testcontainer

### 2.5.3 Update parser/config.py

Ensure test config doesn't load from environment:

**Modify load_dotenv() call:**
```python
# At top of config.py
from dotenv import load_dotenv

# Load .env but don't override existing environment variables
load_dotenv(override=False)
```

**Ensure TestingConfig is isolated:**
```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = None  # Set by test fixtures
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    UPLOAD_FOLDER = 'tests/fixtures/uploads'
    # Don't inherit environment-loaded values
```

**Action Items:**
- [ ] Update `load_dotenv(override=False)` in `parser/config.py`
- [ ] Review `TestingConfig` class
- [ ] Ensure test config is isolated

### 2.5.4 Create Test Runner Script

Create `scripts/test.sh`:

```bash
#!/bin/bash
# Run tests with test environment

# Load test environment
set -a
source envs/test.env
set +a

# Run pytest with all arguments passed through
pytest "$@"
```

Make executable:
```bash
chmod +x scripts/test.sh
```

**Action Items:**
- [ ] Create `scripts/` directory
- [ ] Create `scripts/test.sh`
- [ ] Make script executable
- [ ] Test running: `./scripts/test.sh`

### 2.5.5 Update pytest.ini (Optional)

Add environment configuration to `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
python_paths = 
    .
    parser
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=parser
    --cov-report=term-missing
    --cov-report=html
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**Action Items:**
- [ ] Review current `pytest.ini`
- [ ] Keep existing configuration
- [ ] Document test environment usage in comments

### 2.5.6 Verify Test Isolation

**What should NOT change:**
- ✅ testcontainers setup (still creates isolated postgres)
- ✅ Test fixtures (still override DATABASE_URL)
- ✅ Test data isolation (each test gets clean state)
- ✅ All existing tests should pass

**What SHOULD change:**
- ✅ Tests load consistent env vars from `envs/test.env`
- ✅ No dependency on `.env` being present
- ✅ Explicit test configuration separate from dev/prod

**Action Items:**
- [ ] Run full test suite: `./scripts/test.sh`
- [ ] Verify all tests pass
- [ ] Check coverage report still generates
- [ ] Test with `.env` absent
- [ ] Test with `.env` present (should still use test config)

### 2.5.7 Test Validation Commands

```bash
# Run all tests
./scripts/test.sh

# Run with markers
./scripts/test.sh -m unit
./scripts/test.sh -m integration
./scripts/test.sh -m "not slow"

# Run specific file
./scripts/test.sh tests/test_database.py

# Run with coverage
./scripts/test.sh --cov=parser --cov-report=html

# Verify clean environment
unset DATABASE_URL SECRET_KEY
./scripts/test.sh
```

**Action Items:**
- [ ] Test all commands above
- [ ] Document any failures
- [ ] Verify coverage output

---

## Phase 3: 1Password Integration

### 3.1 Create 1Password Vault Items

Create items in 1Password (use your preferred vault):

**Item: `flask-pandas-local`**
- Type: API Credential or Secure Note
- Fields:
  - SECRET_KEY
  - POSTGRES_PASSWORD
  - DATABASE_URL

**Item: `flask-pandas-production`**
- Type: API Credential or Secure Note
- Fields:
  - SECRET_KEY
  - POSTGRES_PASSWORD
  - DATABASE_URL

**Item: `flask-pandas-dhi`**
- Type: API Credential or Secure Note
- Fields:
  - SECRET_KEY
  - POSTGRES_PASSWORD
  - DATABASE_URL

**Item: `flask-pandas-test` (optional, for CI/CD)**
- Type: API Credential or Secure Note
- Fields:
  - SECRET_KEY (test key)
  - CI_DATABASE_URL (if needed)

**Action Items:**
- [ ] Open 1Password
- [ ] Create vault items for each environment
- [ ] Generate secure random values for SECRET_KEY
- [ ] Store database credentials
- [ ] Note vault and item names for reference syntax

### 3.2 Test 1Password CLI

Verify CLI is installed and authenticated:

```bash
# Check installation
op --version

# Sign in (if not already signed in)
op signin

# Test retrieving a secret
op item get "flask-pandas-production" --fields SECRET_KEY

# Test full item retrieval
op item get "flask-pandas-production"
```

**Action Items:**
- [ ] Verify `op` command is available
- [ ] Sign in to 1Password: `op signin`
- [ ] Test retrieving each secret
- [ ] Document any authentication issues

### 3.3 Update Environment Files with 1Password References

Update `envs/production.env` and `envs/dhi.env`:

**Example `envs/production.env`:**
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=op://Private/flask-pandas-production/SECRET_KEY
POSTGRES_PASSWORD=op://Private/flask-pandas-production/POSTGRES_PASSWORD
DATABASE_URL=op://Private/flask-pandas-production/DATABASE_URL
UPLOAD_FOLDER=parser/input/
MAX_CONTENT_LENGTH=10737418240
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

**Action Items:**
- [ ] Replace secrets in `envs/production.env`
- [ ] Replace secrets in `envs/dhi.env`
- [ ] Keep `envs/local.env` with direct values (for convenience)
- [ ] Test 1Password references resolve correctly

### 3.4 Create Deployment Helper Script

Create `scripts/load-env.sh`:

```bash
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

# Run docker compose with 1Password secret injection
op run --env-file="envs/${ENV}.env" -- \
    docker compose -f compose.yaml -f compose.${ENV}.yaml "$@"
```

Make executable:
```bash
chmod +x scripts/load-env.sh
```

**Action Items:**
- [ ] Create `scripts/load-env.sh`
- [ ] Make script executable
- [ ] Test with local environment
- [ ] Test with production environment (dry run)

### 3.5 Create Test CI Script with 1Password

Create `scripts/test-ci.sh`:

```bash
#!/bin/bash
# Run tests in CI with 1Password secrets (if needed)

set -e

echo "Running tests with 1Password integration..."

# Check if 1Password CLI is available
if command -v op > /dev/null 2>&1; then
    echo "Using 1Password for secret injection..."
    op run --env-file="envs/test.env" -- pytest "$@"
else
    echo "1Password CLI not found, using local environment..."
    set -a
    source envs/test.env
    set +a
    pytest "$@"
fi
```

Make executable:
```bash
chmod +x scripts/test-ci.sh
```

**Action Items:**
- [ ] Create `scripts/test-ci.sh`
- [ ] Make script executable
- [ ] Test locally
- [ ] Document for CI/CD setup

---

## Phase 4: Create Deployment Scripts

### 4.1 Create Main Deployment Script

Create `deploy.sh`:

```bash
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

# Check compose file exists
if [ ! -f "compose.${ENV}.yaml" ]; then
    echo "Error: Compose file compose.${ENV}.yaml not found"
    exit 1
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
    # Local environment - direct load
    docker compose --env-file="envs/${ENV}.env" \
        -f compose.yaml -f compose.${ENV}.yaml "$@"
fi
```

Make executable:
```bash
chmod +x deploy.sh
```

**Action Items:**
- [ ] Create `deploy.sh`
- [ ] Make script executable
- [ ] Test with local: `./deploy.sh local up`
- [ ] Test with production (dry run): `./deploy.sh production config`

### 4.2 Create Environment Switcher Script

Create `switch-env.sh`:

```bash
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
```

Make executable:
```bash
chmod +x switch-env.sh
```

**Action Items:**
- [ ] Create `switch-env.sh`
- [ ] Make script executable
- [ ] Test switching: `./switch-env.sh local`
- [ ] Verify symlink created: `ls -la .env`

### 4.3 Create Makefile (Optional)

Create `Makefile`:

```makefile
.PHONY: help dev prod-up prod-down dhi-up dhi-down test test-ci clean

help:
	@echo "Flask Pandas Project - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start local development environment"
	@echo "  make dev-down         - Stop local development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod-up          - Start production environment"
	@echo "  make prod-down        - Stop production environment"
	@echo "  make prod-logs        - View production logs"
	@echo ""
	@echo "DHI:"
	@echo "  make dhi-up           - Start DHI environment"
	@echo "  make dhi-down         - Stop DHI environment"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run test suite"
	@echo "  make test-ci          - Run tests with 1Password (CI mode)"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Remove containers and volumes"

dev:
	./deploy.sh local up

dev-down:
	./deploy.sh local down

prod-up:
	./deploy.sh production up -d

prod-down:
	./deploy.sh production down

prod-logs:
	./deploy.sh production logs -f

dhi-up:
	./deploy.sh dhi up -d

dhi-down:
	./deploy.sh dhi down

test:
	./scripts/test.sh

test-ci:
	./scripts/test-ci.sh

test-coverage:
	./scripts/test.sh --cov=parser --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

clean:
	docker compose down -v
	rm -rf htmlcov .pytest_cache .coverage
```

**Action Items:**
- [ ] Create `Makefile`
- [ ] Test each target
- [ ] Update targets as needed

---

## Phase 5: Documentation

### 5.1 Update README.md

Add or update sections:

**Section: Environment Setup**
```markdown
## Environment Setup

This project supports multiple environments: local, production, and DHI.

### Prerequisites

1. Docker and Docker Compose
2. 1Password CLI (for production/DHI)
3. Python 3.11+ (for local development)

### Initial Setup

1. Copy environment template:
   ```bash
   cp envs/.env.template envs/local.env
   ```

2. Update `envs/local.env` with your local settings

3. For production/DHI, configure 1Password items (see below)

### 1Password Configuration

Create items in 1Password for production and DHI environments:

- Item name: `flask-pandas-production`
- Fields: SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL

Update `envs/production.env` and `envs/dhi.env` with references:
```bash
SECRET_KEY=op://Private/flask-pandas-production/SECRET_KEY
```

### Switching Environments

```bash
# Switch to local
./switch-env.sh local

# Switch to production
./switch-env.sh production
```
```

**Section: Deployment**
```markdown
## Deployment

### Local Development

```bash
# Start services
./deploy.sh local up

# Or use Makefile
make dev
```

### Production

```bash
# Sign in to 1Password
op signin

# Start services
./deploy.sh production up -d

# View logs
./deploy.sh production logs -f app
```

### Available Commands

```bash
./deploy.sh <env> up        # Start services
./deploy.sh <env> down      # Stop services
./deploy.sh <env> ps        # List services
./deploy.sh <env> logs -f   # Follow logs
./deploy.sh <env> exec app bash  # Shell into container
```
```

**Section: Testing**
```markdown
## Testing

### Run Tests

```bash
# Run all tests
./scripts/test.sh

# Run specific markers
./scripts/test.sh -m unit
./scripts/test.sh -m integration

# Run with coverage
./scripts/test.sh --cov=parser --cov-report=html
```

### Test Environment

Tests use isolated configuration from `envs/test.env`. Test database is managed by testcontainers.
```

**Action Items:**
- [ ] Add Environment Setup section
- [ ] Add Deployment section
- [ ] Add Testing section
- [ ] Update any outdated information

### 5.2 Create DEPLOYMENT.md

Create comprehensive deployment documentation:

```markdown
# Deployment Guide

## Table of Contents
1. Environment Variables
2. 1Password Vault Structure
3. Deployment Procedures
4. Rollback Procedures
5. Troubleshooting

## Environment Variables

[Document all environment variables, their purpose, and example values]

## 1Password Vault Structure

[Document vault organization, item names, field names]

## Deployment Procedures

### Production Deployment

[Step-by-step production deployment]

### DHI Deployment

[Step-by-step DHI deployment]

## Rollback Procedures

[How to rollback if deployment fails]

## Troubleshooting

[Common issues and solutions]
```

**Action Items:**
- [ ] Create `DEPLOYMENT.md`
- [ ] Document all environment variables
- [ ] Document 1Password structure
- [ ] Add deployment procedures
- [ ] Add rollback procedures
- [ ] Add troubleshooting section

### 5.3 Update Existing Guides

Update existing documentation files:

**File: `PRODUCTION_DEPLOYMENT_GUIDE.md`**
- [ ] Update deployment commands to use new scripts
- [ ] Add 1Password setup instructions
- [ ] Update environment file locations
- [ ] Update compose file names

**File: `LARGE_FILE_UPLOAD_GUIDE.md`**
- [ ] Update environment variable references
- [ ] Update deployment examples

**Action Items:**
- [ ] Review all existing `.md` files
- [ ] Update outdated commands
- [ ] Add references to new structure

### 5.4 Create TESTING.md

Create `TESTING.md`:

```markdown
# Testing Guide

## Overview

This project uses pytest with testcontainers for integration testing.

## Test Environment

Tests use `envs/test.env` for configuration. The test database is managed by testcontainers (PostgreSQL).

## Running Tests

### Locally

```bash
# All tests
./scripts/test.sh

# Specific markers
./scripts/test.sh -m unit
./scripts/test.sh -m integration
./scripts/test.sh -m "not slow"

# Specific file
./scripts/test.sh tests/test_database.py

# With coverage
./scripts/test.sh --cov=parser --cov-report=html
```

### In CI/CD

```bash
./scripts/test-ci.sh
```

## Writing Tests

[Guidelines for writing new tests]

## Test Fixtures

[Documentation of available fixtures]

## Troubleshooting

[Common test issues and solutions]
```

**Action Items:**
- [ ] Create `TESTING.md`
- [ ] Document test commands
- [ ] Document fixtures
- [ ] Add examples

---

## Phase 6: Testing & Validation

### 6.1 Test Local Environment

```bash
# Sign in to 1Password (if needed)
op signin

# Switch to local environment
./switch-env.sh local

# Start services
./deploy.sh local up

# Verify services are running
./deploy.sh local ps

# Test application
open http://localhost:80

# Check logs
./deploy.sh local logs app

# Stop services
./deploy.sh local down
```

**Action Items:**
- [ ] Start local environment
- [ ] Verify all services start
- [ ] Test application functionality
- [ ] Check database connection
- [ ] Verify file uploads work
- [ ] Stop services cleanly

### 6.2 Test Production Environment

**IMPORTANT:** Test in a safe environment first!

```bash
# Sign in to 1Password
op signin

# Verify 1Password items exist
op item get "flask-pandas-production"

# Test configuration (doesn't start services)
./deploy.sh production config

# Start services (add -d for detached)
./deploy.sh production up -d

# Verify services
./deploy.sh production ps

# Check logs
./deploy.sh production logs app

# Test application
curl http://localhost:8000/health

# Stop services
./deploy.sh production down
```

**Action Items:**
- [ ] Verify 1Password authentication
- [ ] Test config generation
- [ ] Start production services
- [ ] Verify secret injection worked
- [ ] Test application endpoints
- [ ] Check logs for errors
- [ ] Stop services

### 6.3 Test DHI Environment

```bash
# Sign in to 1Password
op signin

# Verify 1Password items exist
op item get "flask-pandas-dhi"

# Test configuration
./deploy.sh dhi config

# Start services
./deploy.sh dhi up -d

# Verify services
./deploy.sh dhi ps

# Stop services
./deploy.sh dhi down
```

**Action Items:**
- [ ] Start DHI environment
- [ ] Verify services start
- [ ] Test DHI-specific configuration
- [ ] Stop services

### 6.4 Test Suite Validation

```bash
# Test with clean environment
unset DATABASE_URL SECRET_KEY POSTGRES_PASSWORD
./scripts/test.sh

# Test specific markers
./scripts/test.sh -m unit
./scripts/test.sh -m integration
./scripts/test.sh -m "not slow"

# Test with coverage
./scripts/test.sh --cov=parser --cov-report=html

# Verify coverage report
open htmlcov/index.html

# Test CI script
./scripts/test-ci.sh
```

**Action Items:**
- [ ] Run full test suite
- [ ] Verify all tests pass
- [ ] Check coverage metrics
- [ ] Test with various markers
- [ ] Verify test isolation
- [ ] Check coverage report

### 6.5 Environment Switching Test

```bash
# Switch to local
./switch-env.sh local
ls -la .env  # Should point to envs/local.env

# Switch to production
./switch-env.sh production
ls -la .env  # Should point to envs/production.env

# Verify correct environment loads
cat .env | grep FLASK_ENV
```

**Action Items:**
- [ ] Test switching between environments
- [ ] Verify symlinks are created correctly
- [ ] Confirm environment values are different

### 6.6 Secret Security Validation

```bash
# Check git status
git status

# Verify .env files are ignored
git check-ignore .env envs/local.env envs/production.env envs/dhi.env

# Search for exposed secrets in git history
git log --all --full-history --source --  '*env*'

# Verify 1Password references resolve
op run --env-file=envs/production.env -- env | grep SECRET_KEY
```

**Action Items:**
- [ ] Verify no secrets in git
- [ ] Confirm .env files are gitignored
- [ ] Test 1Password reference resolution
- [ ] Scan for accidentally committed secrets

### 6.7 Makefile Testing (if created)

```bash
# Test each make target
make help
make dev
make dev-down
make test
make test-coverage
```

**Action Items:**
- [ ] Test all Makefile targets
- [ ] Verify commands work as expected

---

## Phase 7: Cleanup & Finalization

### 7.1 Archive Old Files

```bash
# Create deprecated directory
mkdir -p .deprecated

# Move old files
mv docker-compose.*.yaml .deprecated/ 2>/dev/null || true
mv docker-compose.*.yml .deprecated/ 2>/dev/null || true
mv .env.production .deprecated/ 2>/dev/null || true
mv .env.production.template .deprecated/ 2>/dev/null || true

# Update .gitignore to ignore deprecated
echo ".deprecated/" >> .gitignore
```

**Action Items:**
- [ ] Move old compose files
- [ ] Move old env files
- [ ] Update .gitignore
- [ ] Verify old files are not needed

### 7.2 Review Changes Before Committing

```bash
# Check what's staged
git status

# Review diff
git diff

# Review new files
git diff --cached

# Check for secrets
git diff | grep -i "password\|secret\|key"
```

**Action Items:**
- [ ] Review all changes
- [ ] Verify no secrets are being committed
- [ ] Check for sensitive data

### 7.3 Commit Changes

```bash
# Stage new structure
git add envs/
git add compose.yaml compose.override.yaml compose.production.yaml compose.dhi.yaml
git add scripts/
git add deploy.sh switch-env.sh
git add Makefile  # if created
git add .gitignore

# Stage test changes
git add tests/conftest.py
git add parser/config.py

# Stage documentation
git add README.md DEPLOYMENT.md TESTING.md
git add PRODUCTION_DEPLOYMENT_GUIDE.md LARGE_FILE_UPLOAD_GUIDE.md

# Stage deprecated moves
git add .deprecated/

# Commit
git commit -m "Refactor: Multi-environment setup with 1Password integration

- Restructured environment files into envs/ directory
- Created environment-specific Docker Compose overrides
- Integrated 1Password for secret management
- Isolated test configuration
- Added deployment and test runner scripts
- Updated documentation

Breaking changes:
- Old docker-compose.*.yaml files moved to .deprecated/
- .env files now in envs/ directory
- New deployment command: ./deploy.sh <env> <command>
"
```

**Action Items:**
- [ ] Stage all new files
- [ ] Write comprehensive commit message
- [ ] Commit changes
- [ ] Tag release (optional): `git tag -a v2.0.0 -m "Multi-environment refactor"`

### 7.4 Push Changes

```bash
# Push to remote
git push origin main

# Push tags (if created)
git push origin --tags
```

**Action Items:**
- [ ] Push changes to remote
- [ ] Verify CI/CD still works (if configured)

### 7.5 Final Verification

After pushing:

```bash
# Fresh clone test
cd /tmp
git clone <your-repo-url> test-clone
cd test-clone

# Verify structure
ls -la envs/
ls -la scripts/

# Test setup
cp envs/.env.template envs/local.env
# Edit envs/local.env with values
./deploy.sh local up

# Verify it works
curl http://localhost:80
```

**Action Items:**
- [ ] Test fresh clone
- [ ] Verify setup instructions work
- [ ] Test first-time developer experience

---

## Quick Reference

### Daily Development Commands

```bash
# Start local development
./deploy.sh local up

# Run tests
./scripts/test.sh

# View logs
./deploy.sh local logs -f app

# Stop services
./deploy.sh local down
```

### Production Deployment

```bash
# Sign in to 1Password
op signin

# Deploy
./deploy.sh production up -d

# Check status
./deploy.sh production ps

# View logs
./deploy.sh production logs -f app
```

### Environment Switching

```bash
# Switch environment
./switch-env.sh local
./switch-env.sh production
./switch-env.sh dhi
```

### Testing

```bash
# Run all tests
./scripts/test.sh

# Run specific tests
./scripts/test.sh tests/test_database.py
./scripts/test.sh -m unit
./scripts/test.sh -m integration

# With coverage
./scripts/test.sh --cov=parser
```

---

## Troubleshooting

### 1Password Issues

**Problem:** `op: command not found`
```bash
# Install 1Password CLI
# macOS:
brew install --cask 1password-cli

# Verify installation
op --version
```

**Problem:** `1Password CLI not signed in`
```bash
# Sign in
op signin

# Verify
op account list
```

**Problem:** Secret not found
```bash
# List items
op item list

# Get item details
op item get "flask-pandas-production"

# Check reference syntax
# Format: op://vault-name/item-name/field-name
```

### Docker Compose Issues

**Problem:** Service won't start
```bash
# Check logs
./deploy.sh <env> logs

# Verify config
./deploy.sh <env> config

# Check environment variables
./deploy.sh <env> exec app env
```

**Problem:** Environment variables not loading
```bash
# Verify env file exists
ls -la envs/<env>.env

# Check file is sourced
cat envs/<env>.env

# Test 1Password injection
op run --env-file=envs/<env>.env -- env | grep SECRET_KEY
```

### Test Issues

**Problem:** Tests fail after changes
```bash
# Verify test environment
cat envs/test.env

# Run with verbose output
./scripts/test.sh -vv

# Check database container
docker ps -a | grep postgres
```

**Problem:** Test database issues
```bash
# Clean up old containers
docker system prune -a

# Run single test
./scripts/test.sh tests/test_database.py::test_postgres_connection
```

---

## Checklist Summary

### Phase 1: Environment Files
- [ ] Create envs/ directory
- [ ] Create .env.template
- [ ] Create local.env
- [ ] Create production.env with 1Password refs
- [ ] Create dhi.env with 1Password refs
- [ ] Update .gitignore

### Phase 2: Docker Compose
- [ ] Refactor compose.yaml (base)
- [ ] Create compose.override.yaml (local)
- [ ] Create compose.production.yaml
- [ ] Create compose.dhi.yaml
- [ ] Remove hardcoded secrets
- [ ] Archive old files

### Phase 2.5: Testing
- [ ] Create envs/test.env
- [ ] Update tests/conftest.py
- [ ] Update parser/config.py
- [ ] Create scripts/test.sh
- [ ] Create scripts/test-ci.sh
- [ ] Verify test isolation
- [ ] Run full test suite

### Phase 3: 1Password
- [ ] Create 1Password items
- [ ] Test 1Password CLI
- [ ] Update env files with references
- [ ] Create scripts/load-env.sh
- [ ] Test secret injection

### Phase 4: Scripts
- [ ] Create deploy.sh
- [ ] Create switch-env.sh
- [ ] Create Makefile (optional)
- [ ] Make scripts executable
- [ ] Test all scripts

### Phase 5: Documentation
- [ ] Update README.md
- [ ] Create DEPLOYMENT.md
- [ ] Create TESTING.md
- [ ] Update existing guides

### Phase 6: Testing
- [ ] Test local environment
- [ ] Test production environment
- [ ] Test DHI environment
- [ ] Test suite validation
- [ ] Test environment switching
- [ ] Verify secret security

### Phase 7: Cleanup
- [ ] Archive old files
- [ ] Review changes
- [ ] Commit changes
- [ ] Push to remote
- [ ] Final verification

---

## Success Criteria

✅ All environments (local, production, dhi) work correctly
✅ 1Password integration successful
✅ All tests pass
✅ No secrets in git repository
✅ Documentation is complete and accurate
✅ Fresh clone setup works
✅ Team members can deploy to all environments

---

## Notes

- Keep this document updated as you progress
- Check off items as you complete them
- Document any issues or deviations
- Update troubleshooting section with new issues

---

**Last Updated:** [Date]
**Implemented By:** [Your Name]
**Status:** In Progress / Complete
