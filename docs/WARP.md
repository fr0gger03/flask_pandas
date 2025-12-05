# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Flask web application that ingests and processes large Excel files (up to 10GB) containing VMware workload data from RVTools or LiveOptics. The application uses Pandas for data transformation and PostgreSQL for storage, supporting multi-user project management with authentication.

## Development Environment

### Quick Start - Local Development

Start the development environment:
```bash
docker compose --env-file envs/local.env up --build
```

For interactive development with hot-reload:
```bash
docker compose --env-file envs/local.env watch
```

Access the application at http://localhost

Teardown:
```bash
docker compose --env-file envs/local.env down -v
```

### Production Deployment

Start production environment:
```bash
docker compose --env-file envs/production.env -f compose.yaml -f compose.production.yaml up --build
```

For production with Nginx (recommended for large file uploads):
```bash
docker compose --env-file envs/production.env -f compose.nginx.yml up -d
```

## Testing

### Run All Tests

```bash
# Activate virtual environment first
uv sync --frozen

# Run complete test suite with coverage
uv run pytest

# Or use pytest directly if in activated venv
pytest
```

The test suite uses testcontainers to spin up an ephemeral PostgreSQL container for each test session.

### Run Specific Tests

```bash
# Run tests by marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"

# Run specific test file
uv run pytest tests/test_routes.py

# Run specific test function
uv run pytest tests/test_routes.py::test_home_page

# Run with verbose output
uv run pytest -v

# Show test coverage for specific module
uv run pytest --cov=parser.transform
```

### Coverage Reports

Coverage is automatically generated during test runs:
- Terminal report: Shows with `--cov-report=term-missing`
- HTML report: Generated in `htmlcov/` directory
- XML report: Generated as `coverage.xml`

Open HTML coverage report:
```bash
open htmlcov/index.html
```

## Environment Configuration

### Environment Files

The project uses environment-specific files in the `envs/` directory:
- `local.env` - Development settings (gitignored)
- `production.env` - Production settings (gitignored, use 1Password for secrets)
- `.env.template` - Template with all required variables

**Required Environment Variables:**
- `FLASK_ENV` - Environment name (development, production)
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key for sessions
- `UPLOAD_FOLDER` - Directory for uploaded files
- `MAX_CONTENT_LENGTH` - Max file upload size (default: 10737418240 = 10GB)
- `WTF_CSRF_ENABLED` - CSRF protection toggle
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_APP_PASSWORD` - Database credentials

### 1Password Integration

Production secrets should use 1Password CLI references:
```bash
SECRET_KEY=op://Private/flask-pandas-production/SECRET_KEY
DATABASE_URL=op://Private/flask-pandas-production/DATABASE_URL
```

User has 1Password CLI installed and configured.

## Architecture

### Application Structure

```
parser/                     # Main application package
├── app.py                 # Flask app factory with extensions (db, bcrypt, login)
├── config.py              # Configuration classes (Dev, Production, Testing)
├── models.py              # SQLAlchemy models (User, Project, Workload)
├── routes.py              # Blueprint with all HTTP endpoints
├── forms.py               # WTForms for validation
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template with navigation
│   └── pages/            # Page templates
├── static/               # CSS, JS, images
├── sql/                  # Database initialization scripts
└── transform/            # Data processing modules
    ├── data_validation.py      # Excel file type detection
    ├── transform_lova.py       # LiveOptics conversion
    └── transform_rvtools.py    # RVTools conversion
```

### Key Architectural Patterns

**Application Factory Pattern**: `create_app()` in `app.py` constructs the Flask application with optional config override, enabling different configurations for testing vs. production.

**Blueprint Architecture**: Single blueprint (`bp`) in `routes.py` handles all routes with `pages` as the endpoint prefix. All routes are registered under this namespace (e.g., `pages.login`, `pages.dashboard`).

**Multi-Tenancy Data Model**: Three-tier hierarchy:
- `User` → `Project` (one-to-many)
- `Project` → `Workload` (one-to-many)
- Cascade deletes ensure data integrity

**Authentication Flow**: Flask-Login with bcrypt password hashing. Protected routes use `@login_required` decorator. Session protection set to "strong" mode.

**Large File Processing**: Supports up to 10GB Excel files with:
- 1-hour timeout in Gunicorn
- Context managers for memory-efficient Pandas operations
- Chunked reading where possible
- Testcontainers for isolated testing with PostgreSQL

### Data Processing Pipeline

1. **Upload**: User uploads Excel file via `UploadFileForm`
2. **Validation**: `filetype_validation()` detects RVTools vs LiveOptics format by sheet names
3. **Transformation**: 
   - `rvtools_conversion()` - Extracts from vInfo, vDisk, vPartition sheets
   - `lova_conversion()` - Extracts from VMs and VM Performance sheets
4. **Normalization**: Both converters produce same schema (vmId, vmName, vCpu, vRam, storage metrics, IOPS, etc.)
5. **Database Insert**: Workloads linked to Project via foreign key
6. **Display**: Project and workload views with calculated statistics

### Database Schema

**users_tb**: id, username, password (bcrypt hashed)
**projects_tb**: pid, userid (FK), projectname
**workloads_tb**: vmid, pid (FK), mobid, cluster, virtualdatacenter, os, os_name, vmstate, vcpu, vmname, vram, ip_addresses, vinfo_provisioned, vinfo_used, vmdktotal, vmdkused, readiops, writeiops, peakreadiops, peakwriteiops, readthroughput, writethroughput, peakreadthroughput, peakwritethroughput

All storage and memory values stored in GB. IOPS and throughput stored as Numeric(12,6).

## Common Commands

### Package Management

```bash
# Install all dependencies including dev dependencies
uv sync --frozen

# Install only production dependencies (used in Dockerfile)
uv sync --frozen --no-dev

# Add new package
uv add <package-name>

# Add dev-only package
uv add --dev <package-name>
```

### Database Operations

```bash
# Access PostgreSQL in running container
docker compose --env-file envs/local.env exec db psql -U inventorydbuser -d inventorydb

# Run SQL script
docker compose --env-file envs/local.env exec -T db psql -U inventorydbuser -d inventorydb < migration.sql

# View database logs
docker compose --env-file envs/local.env logs db

# Reset database (destructive)
docker compose --env-file envs/local.env down -v
docker compose --env-file envs/local.env up -d db
```

### Docker Operations

```bash
# View running containers
docker compose --env-file envs/local.env ps

# View logs for specific service
docker compose --env-file envs/local.env logs -f app

# Rebuild single service
docker compose --env-file envs/local.env build app

# Access app container shell
docker compose --env-file envs/local.env exec app /bin/sh

# Check resource usage
docker stats
```

### Flask Commands

```bash
# Run Flask shell with app context
docker compose --env-file envs/local.env exec app uv run flask shell

# Check routes
docker compose --env-file envs/local.env exec app uv run flask routes
```

## File Upload Considerations

- Max file size: 10GB (configurable via `MAX_CONTENT_LENGTH`)
- Supported formats: .xls, .xlsx
- Expected file types:
  - **RVTools**: Must have sheets: vInfo, vCPU, vMemory, vDisk, vPartition, etc. (27 sheets)
  - **LiveOptics**: Must have sheets: Details, ESX Hosts, VMs, VM Performance, etc. (10 sheets)
- Files validated by sheet name matching before processing
- Processing timeout: 1 hour (3600 seconds)
- Uses context managers (`with pd.ExcelFile()`) for memory efficiency

## Important Notes

- CSRF protection enabled by default (disabled in tests via `WTF_CSRF_ENABLED=False`)
- User passwords are bcrypt hashed before storage
- All routes check user ownership before allowing access to projects/workloads (via `.filter_by(userid=current_user.id)`)
- The `compose.override.yaml` is automatically loaded for local development
- Test fixtures create unique usernames/projects using UUID to avoid conflicts
- Storage values converted from MB/MiB to GB during transformation
- Workload model has computed properties: `total_storage_gb`, `used_storage_gb`, `storage_utilization_percent`
