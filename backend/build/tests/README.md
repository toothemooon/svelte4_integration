# Backend Tests

This directory contains test code for the Flask backend using `pytest`.

## Running Tests

To run all tests:

1.  Navigate to the `backend` directory: `cd backend`
2.  Ensure your virtual environment is active and dependencies are installed (`pip install -r requirements.txt`).
3.  Run pytest, pointing it to this tests directory:
    ```bash
    python -m pytest build/tests/
    ```

## Running Tests with Coverage

To run tests and generate a coverage report:

1.  Navigate to the `backend` directory.
2.  Run pytest with the coverage flag, using the config file in this directory:
    ```bash
    python -m pytest --cov=. --cov-config=build/tests/.coveragerc build/tests/
    ```
    This command uses the settings in `.coveragerc` located within this `tests` directory.

3.  (Optional) To generate an HTML report after running the command above:
    ```bash
    python -m coverage html
    ```
    This will create an `htmlcov/` directory in the `backend` folder (as configured by default when no directory is specified in `.coveragerc`) with the detailed report.

## Test Organization

The tests are organized as follows:

-   `conftest.py`: Contains shared pytest fixtures (like the test `client`).
-   `test_*.py`: Files containing test functions (e.g., `test_api.py`).
-   `test_db_utils.py`: Utilities for setting up/tearing down test databases (used by fixtures).
-   `debug_utils.py`: Helper functions for debugging database/environment issues.
-   `.coveragerc`: Configuration for test coverage measurement.

## Adding New Tests

1.  Create a new file named `test_*.py` in this directory.
2.  Write test functions starting with `test_`.
3.  Use fixtures defined in `conftest.py` (like `client`) as arguments to your test functions.
4.  Use standard `assert` statements for checks.

Example (`tests/test_example.py`):

```python
import json

def test_example_endpoint(client):
    response = client.get('/api/some_endpoint') # Assuming endpoint exists
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['key'] == 'expected_value'
```

## Using Debug Utilities

The `debug_utils.py` module contains functions to diagnose database issues. You can import and use them if needed.

```python
from tests.debug_utils import debug_database

# Debug the default database
debug_database()

# Debug a specific database file
debug_database('/path/to/database.db')
``` 