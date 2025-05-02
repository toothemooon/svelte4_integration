"""
Database initialization script

This script initializes the database with sample data for development.
WARNING: This will reset all existing data in the database!
"""
import os
import sys

# Add the tests directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))

# Import the database initialization function
from app import app, init_db, get_db

def initialize_database():
    """Initialize the database with tables and sample data"""
    print("⚠️ WARNING: This script will DROP all tables and recreate the database!")
    print("Any existing comments or user data will be LOST!")
    print("For a persistent database approach, use test_vercel_azure/init_db_persistent.py instead.\n")

    with app.app_context():
        # Initialize the database schema
        init_db()
        
        # Add some sample data
        db = get_db()
        
        # Insert sample posts
        sample_posts = [
            ('Welcome to the Blog', 'This is the first post on our blog. Feel free to leave comments!', 1),
            ('Getting Started with Svelte', 'Svelte is a modern JavaScript framework for building user interfaces.', 1),
            ('Flask Backend Setup', 'Learn how to set up a Flask backend for your Svelte application.', 1)
        ]
        
        for title, content, user_id in sample_posts:
            db.execute('INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)', 
                      (title, content, user_id))
        
        # Insert sample comments for different posts
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (1, 'Feel free to leave your comments here!',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (1, 'I found this very helpful for getting started.',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (2, 'The component explanation was exactly what I needed.',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (3, 'Looking forward to more posts on routing.',))
        
        db.commit()
        
        # Ensure admin user exists
        try:
            from scripts.admin_scripts.ensure_admin import ensure_admin_exists
            ensure_admin_exists()
            print("Admin user has been created or verified.")
        except ImportError:
            print("Admin scripts not found - skipping admin user creation")
        except Exception as e:
            print(f"Error creating admin user: {e}")
        
        print("Database initialized with sample data.")

if __name__ == "__main__":
    initialize_database() 