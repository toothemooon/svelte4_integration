"""
Database utilities for testing
"""
import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# Add the backend directory to the path so we can import app
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)
from app import app, init_db, get_db

def create_test_db(db_path=None):
    """
    Create a test database with sample data
    
    This function can be used by tests to create a fresh database for testing.
    If db_path is provided, it will create the database at that location.
    Otherwise, it will use an in-memory database.
    
    Returns:
        A database connection to the test database
    """
    with app.app_context():
        # Override the DATABASE path if provided
        if db_path:
            app.config['DATABASE'] = db_path

        # Initialize the database schema
        init_db()
        
        # Get database connection
        db = get_db()
        
        # Insert sample users with hashed passwords
        password1 = generate_password_hash('password1', method='pbkdf2:sha256')
        password2 = generate_password_hash('password2', method='pbkdf2:sha256')
        
        db.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                  ('test_user1', password1, 'admin'))
        db.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                  ('test_user2', password2, 'user'))
        
        # Insert sample posts
        db.execute('INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)', 
                  ('Test Post 1', 'This is the content of test post 1', 1))
        db.execute('INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)', 
                  ('Test Post 2', 'This is the content of test post 2', 2))
        
        # Insert sample comments for different posts
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', 
                  (1, 'Test comment for post 1'))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', 
                  (2, 'Test comment for post 2'))
        
        db.commit()
        
        return db

def teardown_test_db(db_path):
    """
    Clean up the test database after tests
    
    Args:
        db_path: Path to the test database file to delete
    """
    # Close any open connections
    with app.app_context():
        get_db().close()
    
    # If we're using a file-based database, delete it
    if db_path and db_path != ':memory:' and os.path.exists(db_path):
        os.remove(db_path) 