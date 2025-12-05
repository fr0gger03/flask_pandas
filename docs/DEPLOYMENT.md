# Deployment Guide

## Table of Contents
1. [Environment Variables](#environment-variables)
2. [1Password Vault Structure](#1password-vault-structure)
3. [Deployment Procedures](#deployment-procedures)
4. [Rollback Procedures](#rollback-procedures)
5. [Troubleshooting](#troubleshooting)

---

## Environment Variables

### Flask Configuration
- **FLASK_ENV**: Environment mode (`development`, `production`)
- **FLASK_DEBUG**: Enable/disable debug mode (`True`, `False`)
- **SECRET_KEY**: Secret key for session management and CSRF protection
  - Development: Any string value
  - Production: Strong random value (use 1Password reference)

### Database Configuration
- **POSTGRES_PASSWORD**: PostgreSQL root password
  - Development: Simple password
  - Production: Strong password (use 1Password reference)
- **DATABASE_URL**: Full database connection string
  - Format: `postgresql://username:password@host:port/database`
  - Development: `postgresql://parser:password@db:5432/parser`
  - Production: Use 1Password reference

### File Upload Configuration
- **UPLOAD_FOLDER**: Directory for uploaded files
  - Default: `parser/input/`
- **MAX_CONTENT_LENGTH**: Maximum upload size in bytes
  - Development: `1073741824` (1GB)
  - Production: `10737418240` (10GB)

### Security Configuration
- **WTF_CSRF_ENABLED**: Enable CSRF protection
  - Development: `True`
  - Production: `True`
  - Testing: `False`
- **WTF_CSRF_TIME_LIMIT**: CSRF token lifetime in seconds
  - Default: `3600` (1 hour)

### Logging Configuration
- **LOG_LEVEL**: Logging level
  - Development: `DEBUG`
  - Production: `INFO`
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Performance Configuration
- **PYTHONUNBUFFERED**: Disable Python output buffering
  - Recommended: `1`
- **PYTHONDONTWRITEBYTECODE**: Prevent `.pyc` file creation
  - Recommended: `1`

### Testing Configuration
- **TESTING**: Enable test mode
  - Testing: `True`
  - Others: `False`

---

## 1Password Vault Structure

### Prerequisites
1. Install 1Password CLI:
   ```bash
   # macOS
   brew install --cask 1password-cli
   
   # Verify installation
   op --version
   ```

2. Sign in to 1Password:
   ```bash
   op signin
   ```

### Vault Organization

#### Production Item: `flask-pandas-production`
Create this item in your 1Password vault with the following fields:

**Item Type**: API Credential or Secure Note

**Required Fields**:
- `SECRET_KEY`: Flask secret key for session management
  - Generate with: `python -c 'import secrets; print(secrets.token_hex(32))'`
- `POSTGRES_PASSWORD`: PostgreSQL database password
  - Generate with: `python -c 'import secrets; print(secrets.token_urlsafe(32))'`
- `DATABASE_URL`: Full PostgreSQL connection string
  - Format: `postgresql://parser:PASSWORD@db:5432/parser`

**Example Field Values**:
```
SECRET_KEY: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
POSTGRES_PASSWORD: xK9mP4vT2wQ8nL5jH3dR6fG1bV7cZ0
DATABASE_URL: postgresql://parser:xK9mP4vT2wQ8nL5jH3dR6fG1bV7cZ0@db:5432/parser
```

#### DHI Item: `flask-pandas-dhi`
Create this item for DHI environment with the same structure:

**Required Fields**:
- `SECRET_KEY`: Flask secret key (different from production)
- `POSTGRES_PASSWORD`: PostgreSQL password (different from production)
- `DATABASE_URL`: DHI database connection string

### 1Password Reference Syntax

In environment files, reference secrets using this format:
```bash
# Syntax: op://vault-name/item-name/field-name
SECRET_KEY=op://Private/flask-pandas-production/SECRET_KEY
POSTGRES_PASSWORD=op://Private/flask-pandas-production/POSTGRES_PASSWORD
DATABASE_URL=op://Private/flask-pandas-production/DATABASE_URL
```

### Verifying 1Password Setup

Test that references resolve correctly:
```bash
# Test individual secret retrieval
op item get "flask-pandas-production" --fields SECRET_KEY

# Test full environment file injection
op run --env-file=envs/production.env -- env | grep SECRET_KEY
```

---

## Deployment Procedures

### Local Development Deployment

Local deployment does NOT require 1Password CLI.

#### Method 1: Using Makefile
```bash
# Start development environment
make dev

# Stop development environment
make dev-down

# Rebuild and restart
make dev-rebuild
```

#### Method 2: Using deploy.sh
```bash
# Start services
./deploy.sh local up

# Start with rebuild
./deploy.sh local build --no-cache
./deploy.sh local up

# View logs
./deploy.sh local logs -f app

# Stop services
./deploy.sh local down
```

#### Method 3: Direct Docker Compose
```bash
# Start services
docker compose --env-file=envs/local.env up

# Start in background
docker compose --env-file=envs/local.env up -d

# Stop services
docker compose --env-file=envs/local.env down
```

### Production Deployment

Production deployment REQUIRES 1Password CLI and authentication.

#### Prerequisites Check
```bash
# 1. Verify 1Password CLI is installed
op --version

# 2. Sign in to 1Password
op signin

# 3. Verify authentication
op account list

# 4. Test secret retrieval
op item get "flask-pandas-production"
```

#### Method 1: Using Makefile (Recommended)
```bash
# Build and start production
make prod-up

# View logs
make prod-logs

# Stop production
make prod-down

# Rebuild and restart
make prod-rebuild
```

#### Method 2: Using deploy.sh
```bash
# Build images
./deploy.sh production build --no-cache

# Start services (detached)
./deploy.sh production up -d

# View logs
./deploy.sh production logs -f app

# Check service status
./deploy.sh production ps

# Stop services
./deploy.sh production down
```

#### Deployment Checklist
- [ ] 1Password CLI is installed and authenticated
- [ ] 1Password vault items exist with correct names
- [ ] Environment file `envs/production.env` exists
- [ ] Compose file `compose.production.yaml` exists
- [ ] Docker images are built: `./deploy.sh production build`
- [ ] Services start successfully: `./deploy.sh production up -d`
- [ ] Application is accessible (check logs/endpoints)
- [ ] Database connection is working
- [ ] File uploads are functional

### DHI Deployment

DHI deployment follows the same pattern as production.

#### Using Makefile
```bash
# Build and start DHI
make dhi-up

# Stop DHI
make dhi-down
```

#### Using deploy.sh
```bash
# Build and start
./deploy.sh dhi build --no-cache
./deploy.sh dhi up -d

# Check status
./deploy.sh dhi ps

# View logs
./deploy.sh dhi logs -f

# Stop services
./deploy.sh dhi down
```

### Environment Switching

Switch between environments using the `switch-env.sh` script:

```bash
# Switch to local
./switch-env.sh local

# Switch to production
./switch-env.sh production

# Switch to DHI
./switch-env.sh dhi

# Verify active environment
ls -la .env
cat .env | grep FLASK_ENV
```

**Note**: This creates a symlink `.env` pointing to the selected environment file. This is useful for tools that expect a `.env` file, but is NOT required for deployment scripts.

---

## Rollback Procedures

### Quick Rollback

If a deployment fails or causes issues, immediately rollback:

```bash
# 1. Stop current services
./deploy.sh production down

# 2. Checkout previous working commit
git log --oneline  # Find previous commit hash
git checkout <previous-commit-hash>

# 3. Rebuild and deploy
./deploy.sh production build --no-cache
./deploy.sh production up -d

# 4. Verify services
./deploy.sh production ps
./deploy.sh production logs -f app
```

### Database Rollback

If database migrations were applied:

```bash
# 1. Stop services
./deploy.sh production down

# 2. Restore database from backup
# (Assuming you have database backups)
docker compose --env-file=envs/production.env up -d db
docker exec -i flask-pandas-db psql -U parser < backup.sql

# 3. Deploy previous version
git checkout <previous-commit-hash>
./deploy.sh production build --no-cache
./deploy.sh production up -d
```

### Partial Rollback

If only application code needs rollback (no database changes):

```bash
# 1. Checkout previous version
git checkout <previous-commit-hash>

# 2. Rebuild only app service
./deploy.sh production build app --no-cache

# 3. Restart app service
./deploy.sh production up -d app

# 4. Verify
./deploy.sh production logs -f app
```

### Rolling Forward

If rollback fails, roll forward with a fix:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/<issue>

# 2. Make fixes
# ... edit files ...

# 3. Commit and deploy
git add .
git commit -m "Hotfix: <description>"
./deploy.sh production build --no-cache
./deploy.sh production up -d
```

---

## Troubleshooting

### 1Password Issues

#### Problem: `op: command not found`
```bash
# Solution: Install 1Password CLI
# macOS
brew install --cask 1password-cli

# Linux
curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
  sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | \
  sudo tee /etc/apt/sources.list.d/1password.list
sudo apt update && sudo apt install 1password-cli

# Verify
op --version
```

#### Problem: `1Password CLI not signed in`
```bash
# Solution: Sign in
op signin

# If you have multiple accounts
op signin --account <account-shorthand>

# Verify
op account list
```

#### Problem: `Secret reference not found`
```bash
# Diagnose: Check vault items
op item list

# Check specific item
op item get "flask-pandas-production"

# Verify field names
op item get "flask-pandas-production" --fields label

# Common issues:
# 1. Item name mismatch (case-sensitive)
# 2. Vault name incorrect
# 3. Field name typo

# Correct syntax:
# op://vault-name/item-name/field-name
```

#### Problem: `Permission denied` when running with 1Password
```bash
# Solution: Check item permissions
op item get "flask-pandas-production" --share-link

# Ensure your account has access to the vault and item
```

### Docker Compose Issues

#### Problem: Service won't start
```bash
# Check logs
./deploy.sh <env> logs

# Check specific service
./deploy.sh <env> logs app

# Check configuration syntax
./deploy.sh <env> config

# Validate environment variables
./deploy.sh <env> config | grep -A 20 environment
```

#### Problem: Environment variables not loading
```bash
# Verify env file exists
ls -la envs/<env>.env

# Check file contents
cat envs/<env>.env

# Test 1Password injection (production/DHI)
op run --env-file=envs/production.env -- env | grep SECRET_KEY

# Check inside running container
./deploy.sh <env> exec app env | grep SECRET_KEY
```

#### Problem: Port already in use
```bash
# Find process using port
lsof -i :80

# Stop conflicting service
docker ps
docker stop <container-id>

# Or use different port in compose file
```

#### Problem: Database connection failed
```bash
# Check database service is running
./deploy.sh <env> ps

# Check database logs
./deploy.sh <env> logs db

# Test database connection
./deploy.sh <env> exec db psql -U parser -d parser

# Verify DATABASE_URL is correct
./deploy.sh <env> exec app env | grep DATABASE_URL
```

### Build Issues

#### Problem: Build fails with package errors
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
./deploy.sh <env> build --no-cache

# Check Dockerfile syntax
docker compose -f compose.yaml -f compose.<env>.yaml config
```

#### Problem: `uv sync` fails in container
```bash
# Check Python version compatibility
docker compose exec app python --version

# Check uv installation
docker compose exec app uv --version

# Verify pyproject.toml and uv.lock are in sync
docker compose exec app uv sync --frozen
```

### Runtime Issues

#### Problem: Application returns 500 errors
```bash
# Check application logs
./deploy.sh <env> logs -f app

# Check Flask debug mode (should be False in production)
./deploy.sh <env> exec app env | grep FLASK_DEBUG

# Check for Python exceptions in logs
./deploy.sh <env> logs app | grep -i error
```

#### Problem: File uploads fail
```bash
# Check upload directory permissions
./deploy.sh <env> exec app ls -la parser/input/

# Check MAX_CONTENT_LENGTH setting
./deploy.sh <env> exec app env | grep MAX_CONTENT_LENGTH

# Check disk space
./deploy.sh <env> exec app df -h
```

#### Problem: CSRF token errors
```bash
# Check CSRF is enabled
./deploy.sh <env> exec app env | grep WTF_CSRF_ENABLED

# Check SECRET_KEY is set
./deploy.sh <env> exec app env | grep SECRET_KEY

# Verify SECRET_KEY is not changing between requests
# (Check if environment file is stable)
```

### Network Issues

#### Problem: Cannot access application
```bash
# Check container is running
./deploy.sh <env> ps

# Check port mappings
docker compose ps

# Test from inside container
./deploy.sh <env> exec app curl http://localhost:5000/health

# Check firewall rules (if remote deployment)
sudo ufw status
```

#### Problem: Database unreachable from app
```bash
# Check database service is running
./deploy.sh <env> ps db

# Check network connectivity
./deploy.sh <env> exec app ping db

# Verify database DNS resolution
./deploy.sh <env> exec app nslookup db
```

### Testing Issues

#### Problem: Tests fail after deployment changes
```bash
# Verify test environment
cat envs/test.env

# Run tests with verbose output
./scripts/test.sh -vv

# Run specific failing test
./scripts/test.sh tests/test_database.py::test_name -vv

# Check if testcontainer is starting
./scripts/test.sh -s  # Show stdout
```

#### Problem: Import errors in tests
```bash
# Ensure dependencies are synced
uv sync --frozen

# Check Python path
./scripts/test.sh -vv --collect-only

# Verify test configuration
cat pytest.ini
```

---

## Deployment Best Practices

### Pre-Deployment Checklist
- [ ] All tests passing: `make test`
- [ ] Code reviewed and approved
- [ ] Environment files updated with correct values
- [ ] 1Password items exist and accessible
- [ ] Database migrations tested
- [ ] Backup of production database created
- [ ] Deployment window scheduled
- [ ] Rollback procedure documented

### During Deployment
1. Announce deployment start
2. Create database backup
3. Deploy new version
4. Verify health checks pass
5. Monitor logs for errors
6. Test critical functionality
7. Announce deployment complete

### Post-Deployment
1. Monitor application logs
2. Check error rates
3. Verify database connections
4. Test file uploads
5. Check performance metrics
6. Document any issues
7. Update deployment log

---

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)
- [Flask Configuration Best Practices](https://flask.palletsprojects.com/en/latest/config/)
- [PostgreSQL Docker Documentation](https://hub.docker.com/_/postgres)

---

**Last Updated**: 2025-12-05  
**Maintained By**: Tom Twyman  
**Version**: 2.0.0
