# Python, Pandas, Flask - Working with data using Pandas and Flask

This application grew out of a previous project - the <a href=https://github.com/vmware-archive/vmware-cloud-sizer-companion-cli>VMware Cloud Sizer Companion CLI.</a>  I am using several of the functions in that project to ingest an Excel file, perform some transformations on the data using Pandas, and return some basic statistics.

The entire application has been 'containerized' so I may experiment with pushing to the cloud in a standardized way, and leverage CI/CD.

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

3. For production/DHI, configure 1Password items (see [DEPLOYMENT.md](DEPLOYMENT.md))

### 1Password Configuration

Create items in 1Password for production and DHI environments:

- Item name: `flask-pandas-production`
- Fields: `SECRET_KEY`, `POSTGRES_PASSWORD`, `DATABASE_URL`

Update `envs/production.env` and `envs/dhi.env` with references:
```bash
SECRET_KEY=op://Private/flask-pandas-production/SECRET_KEY
POSTGRES_PASSWORD=op://Private/flask-pandas-production/POSTGRES_PASSWORD
DATABASE_URL=op://Private/flask-pandas-production/DATABASE_URL
```

For complete setup instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Switching Environments

```bash
# Switch to local
./switch-env.sh local

# Switch to production
./switch-env.sh production

# Switch to DHI
./switch-env.sh dhi
```

---

## Deployment

### Local Development

```bash
# Start services
./deploy.sh local up

# Or use Makefile
make dev

# Stop services
make dev-down
```

### Production

```bash
# Sign in to 1Password
op signin

# Start services
./deploy.sh production up -d

# Or use Makefile
make prod-up

# View logs
make prod-logs

# Stop services
make prod-down
```

### Available Commands

```bash
./deploy.sh <env> up        # Start services
./deploy.sh <env> down      # Stop services
./deploy.sh <env> ps        # List services
./deploy.sh <env> logs -f   # Follow logs
./deploy.sh <env> exec app bash  # Shell into container
```

For complete deployment instructions, rollback procedures, and troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Testing

### Run Tests

```bash
# Run all tests
./scripts/test.sh

# Or use Makefile
make test

# Run specific markers
./scripts/test.sh -m unit
./scripts/test.sh -m integration

# Run with coverage
make test-coverage
```

### Test Environment

Tests use isolated configuration from `envs/test.env`. Test database is managed by testcontainers.

For complete testing documentation, fixtures, and troubleshooting, see [TESTING.md](TESTING.md).

