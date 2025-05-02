# Backend Testing

This directory contains automated tests for the Flask backend application using `pytest`.

## Overview

The testing setup includes:

-   **Pytest:** The core testing framework.
-   **Coverage.py:** For measuring code coverage.
-   **Fixtures (`conftest.py`):** Reusable setup code (e.g., `client` for making requests, `app_context`).
-   **Markers (`../pytest.ini`):** For categorizing tests (`api`, `unit`, `slow`, `rbac`).
-   **Configuration (`.coveragerc`, `../pytest.ini`):** Settings for coverage and pytest.
-   **Test Runner (`run_coverage.py`):** A convenient script to run tests with various coverage reporting options.

## Running Tests

All test commands should be run from the **`backend/`** directory.

### Using the Test Runner Script (Recommended)

The `run_coverage.py` script provides a flexible way to run tests and generate coverage reports.

```bash
# Navigate to the backend directory
cd backend

# Activate your virtual environment if needed
# source ../.venv/bin/activate

# Run all tests and show terminal coverage report + HTML report
python build/tests/run_coverage.py

# Run only API tests and generate HTML report
python build/tests/run_coverage.py --api

# Run only unit tests and generate HTML report
python build/tests/run_coverage.py --unit

# Run only role-based access control tests and generate HTML report
python build/tests/run_coverage.py --rbac

# Run only slow tests and generate HTML report
python build/tests/run_coverage.py --slow

# Generate XML and JSON reports (useful for CI)
python build/tests/run_coverage.py --xml --json

# Combine options: Run only unit tests, generate XML report
python build/tests/run_coverage.py --unit --xml

# Show help for the script
python build/tests/run_coverage.py --help
```

Coverage reports are generated in the `backend/build/tests/` directory (e.g., `htmlcov/`, `coverage.xml`, `coverage.json`).

### Running Tests Directly with Pytest

You can also invoke `pytest` directly.

```bash
# Navigate to the backend directory
cd backend

# Activate your virtual environment if needed
# source ../.venv/bin/activate

# Run all tests defined in pytest.ini (looks in build/tests/)
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run specific test groups using markers
python -m pytest -m api
python -m pytest -m unit
python -m pytest -m slow
python -m pytest -m rbac

# Run tests and generate terminal coverage report (using .coveragerc)
python -m coverage run --rcfile=build/tests/.coveragerc -m pytest
python -m coverage report --rcfile=build/tests/.coveragerc

# Run tests and generate HTML coverage report
python -m coverage run --rcfile=build/tests/.coveragerc -m pytest
python -m coverage html --rcfile=build/tests/.coveragerc
```

## Test Files and Structure

-   `conftest.py`: Contains shared pytest fixtures (`client`, `app_context`). These are automatically available to test functions.
-   `test_api.py`: Integration tests for the Flask API endpoints.
-   `test_auth.py`: Tests focused on user registration, login, and JWT token handling.
-   `test_database.py`: Unit tests for database helper functions or interactions.
-   `test_db_utils.py`: Utilities used by `conftest.py` to set up/tear down the test database.
-   `test_role_based_access.py`: Tests for role-based access control functionality.
-   `debug_utils.py`: Helper functions for debugging database/environment issues.
-   `run_coverage.py`: The enhanced test runner script.
-   `.coveragerc`: Configuration file for `coverage.py`.
-   `../pytest.ini`: Main configuration file for `pytest`, defining markers and test paths.

## Adding New Tests

1.  Decide if it's an API integration test, a unit test, etc.
2.  Create or choose the appropriate `test_*.py` file within this directory (`build/tests/`).
3.  Define test functions named `test_*`.
4.  Use fixtures from `conftest.py` as function arguments (e.g., `def test_my_endpoint(client):`).
5.  Use standard `assert` statements to check conditions.
6.  Add relevant markers (`@pytest.mark.api`, `@pytest.mark.unit`, `@pytest.mark.slow`, `@pytest.mark.rbac`) to categorize the test, ensuring they are defined in `../pytest.ini`.

```python
# Example test in test_api.py
import pytest
import json

@pytest.mark.api
def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
```

## Role-Based Access Control Testing

The `test_role_based_access.py` file contains tests specifically focused on the role-based access control functionality:

### Authentication and Token Tests
- Test JWT token generation with role information
- Verify role is included in the token payload
- Test different roles (admin vs. regular user)

### Admin Endpoint Access Tests
- Test that admin-only endpoints (`/api/admin/users`) can only be accessed by admins
- Verify 403 Forbidden responses for non-admin users
- Test authentication requirements (401 responses for missing tokens)

### Post Management Tests
- Test post creation permissions (admin-only)
- Test ownership-based access control for post editing
- Test admin override for editing any post
- Test post deletion functionality (admin-only)

### Admin User Creation
- Test the admin user creation script
- Verify role assignment and persistence

To create test admin users from the command line:

```bash
# From the backend directory
python scripts/admin_scripts/create_admin.py testadmin securepassword

# Or use the convenience script
./scripts/admin_scripts/make_admin.sh testadmin securepassword

# To ensure admin users persist through database resets
python scripts/admin_scripts/ensure_admin.py
```

These tests use both the `@pytest.mark.api` and `@pytest.mark.rbac` markers, allowing them to be run either with all API tests or separately using the `--rbac` option.

## Debugging

For debugging database issues or examining the test database state, you can use the `debug_utils.py` module:

```python
from tests.debug_utils import debug_database

# Debug the default database
debug_database()

# Debug a specific database file
debug_database('/path/to/database.db')
``` 