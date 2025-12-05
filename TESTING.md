# Testing Guide

## Table of Contents
1. [Overview](#overview)
2. [Test Environment](#test-environment)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Writing Tests](#writing-tests)
6. [Test Fixtures](#test-fixtures)
7. [Coverage Reports](#coverage-reports)
8. [Continuous Integration](#continuous-integration)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This project uses **pytest** with **testcontainers** for comprehensive testing. The test suite includes:

- **Unit tests**: Test individual functions and components
- **Integration tests**: Test interactions between components
- **Database tests**: Test database operations using isolated PostgreSQL containers
- **Flask tests**: Test routes, forms, and authentication

### Test Statistics
- **Framework**: pytest 7.4+
- **Database**: testcontainers-postgres
- **Coverage Tool**: pytest-cov
- **Target Coverage**: 90%+
- **Test Count**: 100+ tests

---

## Test Environment

### Environment Configuration

Tests use an isolated configuration from `envs/test.env`:

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

**Key Points**:
- `TESTING=True` enables test mode in Flask
- `DATABASE_URL` is overridden by testcontainers
- `WTF_CSRF_ENABLED=False` disables CSRF for easier testing
- Separate `UPLOAD_FOLDER` for test fixtures

### Test Isolation

Each test run gets:
1. **Fresh PostgreSQL container** - Isolated database via testcontainers
2. **Clean database schema** - Migrations applied automatically
3. **Isolated environment** - No interference from `.env` files
4. **Fresh Flask application** - New app instance per test session

---

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Or use the script directly
./scripts/test.sh
```

### Basic Commands

```bash
# Run all tests with verbose output
./scripts/test.sh -v

# Run all tests with very verbose output
./scripts/test.sh -vv

# Run specific test file
./scripts/test.sh tests/test_database.py

# Run specific test function
./scripts/test.sh tests/test_database.py::test_postgres_connection

# Run specific test class
./scripts/test.sh tests/test_auth.py::TestAuth
```

### Using Test Markers

```bash
# Run only unit tests
./scripts/test.sh -m unit

# Run only integration tests
./scripts/test.sh -m integration

# Run all except slow tests
./scripts/test.sh -m "not slow"

# Combine markers
./scripts/test.sh -m "unit and not slow"
```

### Coverage Reports

```bash
# Run tests with coverage
make test-coverage

# Or using script
./scripts/test.sh --cov=parser --cov-report=html

# View HTML coverage report
open htmlcov/index.html

# Terminal coverage report
./scripts/test.sh --cov=parser --cov-report=term-missing
```

### Debugging Tests

```bash
# Show print statements
./scripts/test.sh -s

# Drop into debugger on failure
./scripts/test.sh --pdb

# Show local variables on failure
./scripts/test.sh -l

# Stop at first failure
./scripts/test.sh -x

# Show slowest 10 tests
./scripts/test.sh --durations=10
```

### Test Collection

```bash
# Show what tests would run (don't execute)
./scripts/test.sh --collect-only

# Show test hierarchy
./scripts/test.sh --collect-only -q
```

---

## Test Structure

### Directory Layout

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test data and resources
│   └── uploads/             # Test upload directory
├── test_auth.py             # Authentication tests
├── test_database.py         # Database connection tests
├── test_models.py           # SQLAlchemy model tests
├── test_routes.py           # Flask route tests
├── test_forms.py            # WTForms tests
└── test_utils.py            # Utility function tests
```

### Test Naming Conventions

- **Files**: `test_*.py` or `*_test.py`
- **Classes**: `Test*` (e.g., `TestAuth`, `TestDatabase`)
- **Functions**: `test_*` (e.g., `test_login`, `test_database_connection`)

### Available Markers

```python
@pytest.mark.unit           # Unit tests (fast, isolated)
@pytest.mark.integration    # Integration tests (slower, multi-component)
@pytest.mark.slow           # Slow tests (>1 second)
```

---

## Writing Tests

### Basic Test Example

```python
def test_homepage(client):
    """Test that homepage loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data
```

### Using Fixtures

```python
def test_user_creation(db_session):
    """Test creating a user in the database."""
    from parser.models import User
    
    # Create user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Verify user exists
    found_user = db_session.query(User).filter_by(username='testuser').first()
    assert found_user is not None
    assert found_user.email == 'test@example.com'
    assert found_user.check_password('password123')
```

### Testing Routes

```python
def test_login_route(client, db_session):
    """Test user login functionality."""
    from parser.models import User
    
    # Create test user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome testuser' in response.data
```

### Testing File Uploads

```python
from io import BytesIO

def test_file_upload(client, authenticated_user):
    """Test file upload functionality."""
    data = {
        'file': (BytesIO(b'test file content'), 'test.xlsx')
    }
    
    response = client.post(
        '/upload',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'Upload successful' in response.data
```

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_password_hashing():
    """Test password hashing utility."""
    from parser.models import User
    
    user = User(username='test')
    user.set_password('secret123')
    
    assert user.check_password('secret123')
    assert not user.check_password('wrong')

@pytest.mark.integration
@pytest.mark.slow
def test_complex_workflow(client, db_session):
    """Test complete user workflow."""
    # ... complex test taking >1 second
```

---

## Test Fixtures

### Available Fixtures

#### Application Fixtures

##### `app`
Creates a Flask application instance configured for testing.

```python
def test_app_config(app):
    """Test app configuration."""
    assert app.config['TESTING'] is True
```

##### `client`
Provides a Flask test client for making requests.

```python
def test_homepage(client):
    """Test homepage route."""
    response = client.get('/')
    assert response.status_code == 200
```

#### Database Fixtures

##### `postgres_container`
Starts a PostgreSQL testcontainer (session-scoped).

```python
# Used internally, typically don't use directly
```

##### `db_url`
Provides the database URL for the test container.

```python
def test_database_url(db_url):
    """Test database URL is available."""
    assert 'postgresql://' in db_url
```

##### `db_session`
Provides a SQLAlchemy session for database tests.

```python
def test_create_record(db_session):
    """Test creating a database record."""
    from parser.models import User
    user = User(username='test')
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

#### Authentication Fixtures

##### `test_user`
Creates a test user in the database.

```python
def test_user_exists(test_user, db_session):
    """Test that test user exists."""
    from parser.models import User
    user = db_session.query(User).filter_by(username='testuser').first()
    assert user is not None
```

##### `authenticated_user`
Creates a test user and logs them in.

```python
def test_protected_route(client, authenticated_user):
    """Test accessing protected route."""
    response = client.get('/dashboard')
    assert response.status_code == 200
```

### Custom Fixtures

Create custom fixtures in `tests/conftest.py`:

```python
import pytest

@pytest.fixture
def sample_dataframe():
    """Provide a sample pandas DataFrame for testing."""
    import pandas as pd
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'Chicago']
    })

@pytest.fixture
def temp_upload_dir(tmp_path):
    """Provide a temporary upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir
```

Use custom fixtures:

```python
def test_dataframe_processing(sample_dataframe):
    """Test processing a dataframe."""
    assert len(sample_dataframe) == 3
    assert 'name' in sample_dataframe.columns

def test_file_save(temp_upload_dir):
    """Test saving file to temp directory."""
    test_file = temp_upload_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
```

---

## Coverage Reports

### Generating Coverage

```bash
# HTML report (recommended)
make test-coverage
open htmlcov/index.html

# Terminal report
./scripts/test.sh --cov=parser --cov-report=term

# Terminal with missing lines
./scripts/test.sh --cov=parser --cov-report=term-missing

# Multiple formats
./scripts/test.sh --cov=parser --cov-report=html --cov-report=term
```

### Coverage Configuration

Coverage is configured in `pytest.ini`:

```ini
[pytest]
addopts = 
    --cov=parser
    --cov-report=term-missing
    --cov-report=html
```

### Coverage Goals

- **Overall**: 90%+ coverage
- **Critical paths**: 100% coverage (auth, data processing)
- **Routes**: 95%+ coverage
- **Models**: 95%+ coverage
- **Utilities**: 85%+ coverage

### Excluding Code from Coverage

Use `# pragma: no cover` for code that shouldn't be tested:

```python
def debug_function():  # pragma: no cover
    """Only used during development."""
    print("Debug info")

if __name__ == '__main__':  # pragma: no cover
    app.run()
```

---

## Continuous Integration

### CI/CD Testing

For automated testing in CI/CD pipelines:

```bash
# Run tests with 1Password integration
make test-ci

# Or use script directly
./scripts/test-ci.sh
```

### CI/CD Configuration Example

**GitHub Actions** (`.github/workflows/test.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --frozen
      
      - name: Run tests
        run: ./scripts/test.sh --cov=parser --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Troubleshooting

### Common Issues

#### Tests Fail to Start

```bash
# Problem: testcontainer won't start
# Solution: Check Docker is running
docker ps

# Ensure Docker daemon is accessible
docker info

# Clean up old containers
docker system prune -f
```

#### Import Errors

```bash
# Problem: "ModuleNotFoundError: No module named 'parser'"
# Solution: Sync dependencies
uv sync --frozen

# Verify Python path
./scripts/test.sh --collect-only
```

#### Database Connection Errors

```bash
# Problem: "could not connect to server"
# Solution: Ensure testcontainer is starting
./scripts/test.sh -vv -s

# Check if PostgreSQL container is running
docker ps | grep postgres

# Try with fresh containers
docker stop $(docker ps -q)
./scripts/test.sh
```

#### Tests Pass Locally but Fail in CI

```bash
# Problem: Environment differences
# Solution: Check test environment file
cat envs/test.env

# Verify no dependency on local .env
rm .env
./scripts/test.sh

# Check Python version matches CI
python --version
```

#### Slow Tests

```bash
# Find slowest tests
./scripts/test.sh --durations=10

# Run only fast tests
./scripts/test.sh -m "not slow"

# Skip integration tests during development
./scripts/test.sh -m unit
```

#### Fixture Not Found

```bash
# Problem: "fixture 'xyz' not found"
# Solution: Check conftest.py has the fixture
grep -r "def xyz" tests/conftest.py

# Verify fixture scope is correct
./scripts/test.sh --fixtures
```

#### Coverage Report Not Generated

```bash
# Ensure coverage plugin is installed
uv sync --frozen

# Generate explicitly
./scripts/test.sh --cov=parser --cov-report=html

# Check for .coverage file
ls -la .coverage

# Clean and regenerate
rm -rf htmlcov .coverage
make test-coverage
```

---

## Best Practices

### Test Organization

1. **One test per function**: Keep tests focused and simple
2. **Descriptive names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests consistently
4. **Fixtures for setup**: Use fixtures instead of setup/teardown
5. **Markers for categorization**: Mark tests appropriately

### Test Data

1. **Use fixtures**: Create reusable test data
2. **Avoid hardcoding**: Use factories or builders
3. **Minimal data**: Create only what's needed for the test
4. **Clean up**: Fixtures handle cleanup automatically

### Assertions

```python
# Good: Specific assertions
assert response.status_code == 200
assert 'email' in form.errors
assert user.is_authenticated

# Bad: Vague assertions
assert response
assert form
assert user
```

### Testing Asynchronous Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test asynchronous functionality."""
    result = await some_async_function()
    assert result is not None
```

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-flask Documentation](https://pytest-flask.readthedocs.io/)
- [testcontainers-python Documentation](https://testcontainers-python.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Last Updated**: 2025-12-05  
**Maintained By**: Tom Twyman  
**Version**: 2.0.0
