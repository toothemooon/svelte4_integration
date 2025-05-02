"""
pytest configuration file
"""
import os
import sys
import pytest
import tempfile

# Add the backend directory to the path so we can import app
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)
from app import app

# Import test_db_utils from the local directory
from build.tests.test_db_utils import create_test_db, teardown_test_db

@pytest.fixture
def client():
    """Create a test client for the app"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    
    # Create a test client
    with app.test_client() as client:
        # Create a test database with sample data
        with app.app_context():
            create_test_db(db_path)
        
        yield client
    
    # Clean up
    os.close(db_fd)
    teardown_test_db(db_path)

@pytest.fixture
def app_context():
    """Create an app context for tests that need it"""
    with app.app_context():
        yield 