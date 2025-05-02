#!/usr/bin/env python3
"""
Create Test Admin Account

This script creates an admin user account for testing purposes.
It will initialize the database if it doesn't exist and create
an admin user with the specified username and password.
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# Default admin credentials - these can be changed as needed
DEFAULT_ADMIN_USERNAME = "testadmin"
DEFAULT_ADMIN_PASSWORD = "password123"  # Change this in production!

# Get the path to the database directory from environment variable or use the current directory
DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(DATABASE_DIR, 'database.db')

def init_db_if_needed():
    """Initialize the database if it doesn't exist already."""
    # Check if database file exists
    db_exists = os.path.isfile(DATABASE_PATH)
    
    if not db_exists:
        print(f"Database file not found at {DATABASE_PATH}. Creating database...")
        
        # Create the directory if it doesn't exist
        os.makedirs(DATABASE_DIR, exist_ok=True)
        
        # Create a new database connection
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create posts table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create comments table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print("Database initialized successfully.")
    else:
        print(f"Database already exists at {DATABASE_PATH}")
    
    return True

def create_admin_user(username, password):
    """Create an admin user with the specified username and password."""
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if the user already exists
        cursor.execute("SELECT id, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user:
            user_id, role = user
            print(f"User '{username}' already exists (ID: {user_id}, Role: {role})")
            
            # Update to admin role if not already admin
            if role != 'admin':
                cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
                conn.commit()
                print(f"Updated user '{username}' to admin role")
            else:
                print(f"User '{username}' is already an admin")
                
            # Update password if requested
            update_password = input(f"Do you want to update the password for '{username}'? (y/n): ").lower()
            if update_password == 'y':
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
                conn.commit()
                print(f"Password updated for user '{username}'")
        else:
            # Create a new admin user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed_password, 'admin')
            )
            conn.commit()
            
            user_id = cursor.lastrowid
            print(f"Created new admin user '{username}' with ID: {user_id}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

def main():
    """Main execution function."""
    # Get admin credentials, either from command line or use defaults
    username = DEFAULT_ADMIN_USERNAME
    password = DEFAULT_ADMIN_PASSWORD
    
    # Allow command-line override of defaults
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    
    print(f"Database directory: {DATABASE_DIR}")
    print(f"Database path: {DATABASE_PATH}")
    
    # Initialize database if needed
    if init_db_if_needed():
        # Create the admin user
        if create_admin_user(username, password):
            print(f"\nAdmin user setup complete!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print("You can use these credentials to log in to the application.")
        else:
            print("Failed to create admin user.")
            sys.exit(1)
    else:
        print("Failed to initialize database.")
        sys.exit(1)

if __name__ == "__main__":
    main() 