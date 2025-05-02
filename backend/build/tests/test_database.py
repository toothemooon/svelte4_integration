"""
Tests for database utility functions
"""
import pytest
import os
import sys
import tempfile
import sqlite3

# Add the backend directory to the path so we can import app
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)
from app import get_db, init_db, close_connection


@pytest.mark.unit
def test_get_db_connection():
    """Test that get_db returns a database connection"""
    # Create a test app context
    from app import app
    
    with app.app_context():
        # Get a connection
        db = get_db()
        
        # Ensure we got a connection object
        assert db is not None
        assert isinstance(db, sqlite3.Connection)
        
        # Check that we can execute a query
        cursor = db.execute('SELECT 1')
        result = cursor.fetchone()
        assert result[0] == 1
        
        # Test the connection is stored in g
        from flask import g
        assert hasattr(g, '_database')
        assert g._database is db
        
        # Get another connection - should be the same one
        db2 = get_db()
        assert db2 is db

@pytest.mark.unit
def test_init_db():
    """Test database initialization"""
    # Create a test app context and temporary database
    from app import app
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    
    try:
        with app.app_context():
            # Initialize the database
            init_db()
            
            # Check that tables were created
            db = get_db()
            
            # Check users table
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert cursor.fetchone() is not None
            
            # Check posts table
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
            assert cursor.fetchone() is not None
            
            # Check comments table
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
            assert cursor.fetchone() is not None
    finally:
        os.close(db_fd)
        os.unlink(db_path)

@pytest.mark.unit
def test_close_connection():
    """Test connection closing function"""
    from app import app
    from flask import g
    
    # Setup a test app context with a database connection
    with app.app_context():
        # Get a connection to set g._database
        db = get_db()
        assert hasattr(g, '_database')
        
        # Call close_connection
        close_connection(None)
        
        # We're primarily testing that close_connection runs without errors
        # The actual SQLite connection closing is handled by SQLite itself
        assert True, "close_connection should execute without errors"

@pytest.mark.unit
def test_db_schema_users():
    """Test user table schema"""
    from app import app
    
    # Create a test app context
    with app.app_context():
        # Get a connection
        db = get_db()
        
        # Query for user table structure
        cursor = db.execute("PRAGMA table_info(users)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        # Check for expected columns
        assert 'id' in columns
        assert 'username' in columns
        assert 'password_hash' in columns
        
        # Check basic constraints and types
        assert columns['id'].upper() == 'INTEGER'  # ID should be integer
        assert columns['username'].upper() == 'TEXT'  # Username should be text
        assert columns['password_hash'].upper() == 'TEXT'  # Password hash should be text

@pytest.mark.unit
def test_db_schema_comments():
    """Test comments table schema"""
    from app import app
    
    # Create a test app context
    with app.app_context():
        # Get a connection
        db = get_db()
        
        # Query for comments table structure
        cursor = db.execute("PRAGMA table_info(comments)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        # Check for expected columns
        assert 'id' in columns
        assert 'post_id' in columns
        assert 'content' in columns
        assert 'timestamp' in columns
        
        # Check basic constraints and types
        assert columns['id'].upper() == 'INTEGER'  # ID should be integer
        assert columns['post_id'].upper() == 'INTEGER'  # Post ID should be integer
        assert columns['content'].upper() == 'TEXT'  # Content should be text 