#!/usr/bin/env python3
"""
Test script to verify database persistence
This script adds a comment to the database and then checks if it exists
"""

import os
import sys
import sqlite3
import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Flask app
from backend.app import app, get_db

def test_db_persistence():
    """Test if comments persist in the database"""
    with app.app_context():
        db = get_db()
        
        # Get current comment count
        cursor = db.execute('SELECT COUNT(*) FROM comments')
        initial_count = cursor.fetchone()[0]
        print(f"Initial comment count: {initial_count}")
        
        # Add a test comment with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_comment = f"Test comment added at {timestamp}"
        
        db.execute(
            'INSERT INTO comments (post_id, content) VALUES (?, ?)',
            (1, test_comment)
        )
        db.commit()
        
        # Verify the comment was added
        cursor = db.execute('SELECT COUNT(*) FROM comments')
        new_count = cursor.fetchone()[0]
        print(f"New comment count: {new_count}")
        
        # Find our test comment
        cursor = db.execute('SELECT * FROM comments WHERE content = ?', (test_comment,))
        comment = cursor.fetchone()
        
        if comment:
            print(f"Successfully added and retrieved comment with ID: {comment['id']}")
            return True
        else:
            print("Failed to retrieve the added comment!")
            return False

def list_all_comments():
    """List all comments in the database"""
    with app.app_context():
        db = get_db()
        cursor = db.execute('SELECT * FROM comments ORDER BY id DESC LIMIT 10')
        comments = cursor.fetchall()
        
        print("\n--- Last 10 Comments ---")
        for comment in comments:
            print(f"ID: {comment['id']}, Post: {comment['post_id']}, Content: {comment['content']}")

if __name__ == "__main__":
    print("Running database persistence test...")
    success = test_db_persistence()
    list_all_comments()
    
    if success:
        print("\nTest PASSED: Database persistence is working properly.")
    else:
        print("\nTest FAILED: Database persistence issue detected.") 