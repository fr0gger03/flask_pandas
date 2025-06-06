# Flask Pandas Testing Suite

This directory contains the complete test suite for the flask_pandas project, adapted from the original python-web-demo project.

## Directory Structure

```
tests/
├── __init__.py                    # Makes tests directory a Python package
├── conftest.py                   # Pytest configuration and shared fixtures
├── pytest.ini                   # Pytest configuration file
├── test-requirements.txt         # Testing dependencies
├── README.md                     # This file
├── sql/
│   └── init-user-db.sh          # PostgreSQL database initialization script
├── test_files/                  # Test data files
│   ├── lova_expected_df.csv     # Expected output for LiveOptics transformation
│   ├── rvtools_expected_df.csv  # Expected output for RVTools transformation
│   ├── source_df.csv            # Source data for testing
│   ├── liveoptics_file_sample.xlsx    # [NEEDS TO BE COPIED] LiveOptics sample file
│   ├── rvtools_file_sample.xlsx       # [NEEDS TO BE COPIED] RVTools sample file
│   ├── bad_lova_file.xlsx            # [NEEDS TO BE COPIED] Invalid LiveOptics file
│   └── bad_rvtools_file.xlsx         # [NEEDS TO BE COPIED] Invalid RVTools file
└── Test Files:
    ├── test_app.py              # Main application route tests
    ├── test_database.py         # Database integration tests
    ├── test_routes.py           # Authentication and route tests
    ├── test_lova_transform.py   # LiveOptics transformation tests
    ├── test_rvtools_transform.py # RVTools transformation tests
    └── test_data_validation.py # Data validation tests
```

## Setup Instructions

### 1. Install Testing Dependencies

From the project root directory:

```bash
pip install -r tests/test-requirements.txt
```

Or add the testing requirements to your main requirements.txt file.

### 2. Copy Excel Test Files

**IMPORTANT**: You need to copy the Excel test files from the original python-web-demo project:

```bash
# From the original project tests/test_files/ directory, copy these files:
cp /path/to/python-web-demo/tests/test_files/liveoptics_file_sample.xlsx tests/test_files/
cp /path/to/python-web-demo/tests/test_files/rvtools_file_sample.xlsx tests/test_files/
cp /path/to/python-web-demo/tests/test_files/bad_lova_file.xlsx tests/test_files/
cp /path/to/python-web-demo/tests/test_files/bad_rvtools_file.xlsx tests/test_files/
```

### 3. Docker Requirements

The tests use testcontainers to spin up a PostgreSQL database. You need:
- Docker installed and running
- Docker daemon accessible to your user

### 4. Environment Setup

Ensure your project structure matches:
```
flask_pandas/
├── parser/
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── config.py
│   └── transform/
│       ├── data_validation.py
│       ├── transform_lova.py
│       └── transform_rvtools.py
└── tests/
    └── [test files as described above]
```

## Running Tests

### Run All Tests
```bash
# From project root
pytest tests/

# Or with more verbose output
pytest -v tests/
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_lova_transform.py tests/test_rvtools_transform.py tests/test_data_validation.py

# Integration tests only  
pytest tests/test_database.py tests/test_routes.py

# Application tests only
pytest tests/test_app.py
```

### Run Individual Test Files
```bash
pytest tests/test_app.py
pytest tests/test_database.py
pytest tests/test_routes.py
```

### Run Specific Tests
```bash
pytest tests/test_app.py::test_home_route
pytest tests/test_database.py::test_user_creation
```

## Key Changes from Original Tests

### Import Statement Updates
- Changed `from src.app import app` to `from app import create_app, db, bcrypt`
- Updated `from src.transform_lova import lova_conversion` to `from transform.transform_lova import lova_conversion`
- Updated `from src.transform_rvtools import rvtools_conversion` to `from transform.transform_rvtools import rvtools_conversion`
- Updated model imports to `from models import User, Project, Workload`

### Application Factory Pattern
- Updated tests to work with the application factory pattern used in flask_pandas
- Added proper app context management in fixtures

### Test Structure Improvements
- Separated concerns into logical test files
- Added comprehensive fixtures in conftest.py
- Improved test isolation with proper database rollbacks
- Added skip decorators for tests requiring missing Excel files

### New Test Coverage
- Added tests for new models (Project, Workload)
- Added tests for authentication flows
- Added tests for file upload functionality
- Added comprehensive data validation tests

## Test Categories

### Unit Tests
- `test_lova_transform.py`: Tests LiveOptics data transformation logic
- `test_rvtools_transform.py`: Tests RVTools data transformation logic  
- `test_data_validation.py`: Tests file type validation logic

### Integration Tests
- `test_database.py`: Tests database operations and relationships
- `test_routes.py`: Tests authentication and protected routes

### Application Tests  
- `test_app.py`: Tests basic Flask application routes and functionality

## Troubleshooting

### Common Issues

1. **Docker not running**: Ensure Docker daemon is running before tests
2. **Missing test files**: Copy Excel files from original project as described above
3. **Import errors**: Ensure you're running tests from the project root directory
4. **Database connection issues**: Check that PostgreSQL testcontainer can start

### Test Skipping
Some tests will be skipped if Excel test files are not present. This is expected behavior until you copy the files from the original project.

### Performance
Integration tests using testcontainers may take longer to run due to Docker container startup time.

## Coverage

To run tests with coverage reporting:

```bash
pip install pytest-cov
pytest --cov=parser tests/
```

This will show code coverage for the parser module.
