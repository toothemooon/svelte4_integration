"""
Script to list all users in the database with their roles
"""
import os
import sqlite3

# Get the path to the database
DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE = os.path.join(DATABASE_DIR, 'database.db')

def list_users():
    """List all users in the database with their roles"""
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    try:
        # Query all users
        cursor = conn.execute('SELECT id, username, role, timestamp FROM users')
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
            return
        
        print("\nList of users in the database:")
        print("-" * 60)
        print(f"{'ID':<5} {'Username':<20} {'Role':<10} {'Created At'}")
        print("-" * 60)
        
        for user in users:
            print(f"{user['id']:<5} {user['username']:<20} {user['role']:<10} {user['timestamp']}")
        
        print("-" * 60)
    
    except sqlite3.Error as e:
        print(f"Error querying users: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_users() 