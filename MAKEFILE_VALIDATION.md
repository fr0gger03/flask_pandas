# Makefile Validation Report

## Issues Found and Fixed

### 1. Missing `--build` Flags
**Problem:** `make prod-up`, `make dev`, and `make dhi-up` were missing the `--build` flag, causing Docker to reuse existing images instead of rebuilding with the correct Dockerfile for each environment.

**Impact:** 
- Production might use dev image (wrong Dockerfile, wrong build target)
- Development might use stale image
- Environment-specific configurations not applied

**Fixed:**
```makefile
# BEFORE
prod-up:
	./deploy.sh production up -d

# AFTER
prod-up:
	./deploy.sh production up -d --build
```

### 2. Added Rebuild Targets
**Added:** `dev-rebuild` and `prod-rebuild` targets for forcing complete rebuilds with `--force-recreate`.

**Usage:**
```bash
make dev-rebuild    # Force rebuild local environment
make prod-rebuild   # Force rebuild production environment
```

## How Each Environment Uses Different Dockerfiles

### Local Development (`make dev`)
```bash
./deploy.sh local up --build
```
**Uses:**
- `compose.yaml` (base configuration)
- `compose.override.yaml` (automatically loaded by Docker Compose)
- **Dockerfile:** `Dockerfile` with **target: test**
- **Build context:** Uses dev build target with Flask debug mode
- **Port:** 80:5001
- **Includes:** Hot-reload, Adminer, source volume mounts

### Production (`make prod-up`)
```bash
./deploy.sh production up -d --build
```
**Uses:**
- `compose.yaml` (base configuration)
- `compose.production.yaml` (explicitly specified via `-f` flag)
- **Dockerfile:** `Dockerfile.production` (completely different file!)
- **Gunicorn:** Production WSGI server instead of Flask dev server
- **Port:** 8000:8000
- **Includes:** Resource limits, health checks, persistent volumes
- **1Password:** Secret injection via `op run`

### DHI (`make dhi-up`)
```bash
./deploy.sh dhi up -d --build
```
**Uses:**
- `compose.yaml` (base configuration)
- `compose.dhi.yaml` (explicitly specified via `-f` flag)
- **Dockerfile:** Depends on compose.dhi.yaml configuration

## Docker Compose File Loading

### Local (Automatic Override)
```bash
docker compose --env-file="envs/local.env" up --build
```
Docker Compose automatically loads:
1. `compose.yaml` (base)
2. `compose.override.yaml` (if present, auto-loaded)

### Production/DHI (Explicit Override)
```bash
op run --env-file="envs/production.env" -- \
    docker compose -f compose.yaml -f compose.production.yaml up -d --build
```
Explicitly specifies both files:
1. `compose.yaml` (base)
2. `compose.production.yaml` (production overrides)

## Validation Commands

### Verify Correct Dockerfile is Used
```bash
# Check production build uses Dockerfile.production
docker compose -f compose.yaml -f compose.production.yaml config | grep dockerfile

# Check local build uses Dockerfile with test target
docker compose config | grep -A 3 "build:"
```

### Verify Images are Rebuilt
```bash
# Before running
docker images | grep parser

# Run make command
make prod-up

# After - should see new image timestamp
docker images | grep parser
```

### Verify Correct Container Configuration
```bash
# Check production container
docker compose -f compose.yaml -f compose.production.yaml ps
docker inspect workload_parser_app_prod | grep -A 10 "Env"

# Check local container
docker compose ps
docker inspect flask_pandas-app-1 | grep -A 10 "Env"
```

## Critical Differences Between Environments

| Aspect | Local (dev) | Production (prod) |
|--------|-------------|-------------------|
| **Dockerfile** | `Dockerfile` | `Dockerfile.production` |
| **Build Target** | `test` | N/A (separate file) |
| **Server** | Flask dev server | Gunicorn |
| **Port** | 80:5001 | 8000:8000 |
| **Hot Reload** | Yes (volume mounts) | No |
| **Debug Mode** | Enabled | Disabled |
| **Resource Limits** | None | 2GB RAM, 1 CPU |
| **Health Check** | None | curl to /health |
| **Secrets** | Direct in .env | 1Password injection |
| **Adminer** | Included | Not included |

## Best Practices

### Always Rebuild When Switching Environments
```bash
# Wrong - might use cached image from wrong environment
docker compose up -d

# Right - forces rebuild with correct Dockerfile
make prod-up
```

### Use Rebuild for Major Changes
```bash
# When changing dependencies, Dockerfile, or after merge
make dev-rebuild
make prod-rebuild
```

### Verify Configuration Before Deploying
```bash
# Check what Docker Compose will use (doesn't start services)
./deploy.sh production config

# Verify 1Password secrets are injected correctly
op run --env-file=envs/production.env -- env | grep SECRET_KEY
```

## Troubleshooting

### Issue: Production uses development server
**Cause:** Missing `--build` flag, reused dev image  
**Solution:** Run `make prod-rebuild` to force rebuild with Dockerfile.production

### Issue: Code changes not reflected
**Cause:** Image not rebuilt  
**Solution:** 
- Local: Ensure hot-reload is working (volume mounts in compose.override.yaml)
- Production: Run `make prod-rebuild` to rebuild image

### Issue: Different environment variables in container
**Cause:** Wrong .env file loaded  
**Solution:** Verify `./deploy.sh <env>` uses correct envs/${env}.env file

### Issue: Port conflicts
**Cause:** Local uses port 80, production uses 8000  
**Solution:** Ensure previous environment is stopped: `make dev-down` before `make prod-up`

## Summary

✅ **Fixed:** All Makefile targets now use `--build` flag  
✅ **Added:** Rebuild targets with `--force-recreate`  
✅ **Validated:** Each environment uses correct Dockerfile  
✅ **Documented:** Clear separation between dev and prod builds  

The Makefile now ensures:
1. Local development always uses `Dockerfile` with `test` target
2. Production always uses `Dockerfile.production` with Gunicorn
3. All environments rebuild on each deployment to avoid stale images
4. Explicit rebuild commands available for major changes
