#!/usr/bin/env python3
"""
Check Azure Database Tables and Content

This script attempts to directly connect to the database in the Azure environment 
and examine its structure and content.
"""

import requests
import json

# Azure backend URL
AZURE_URL = "https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net"

def query_endpoint(endpoint):
    """Query an endpoint and return the result."""
    url = f"{AZURE_URL}{endpoint}"
    print(f"Querying: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        try:
            return response.json()
        except:
            return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function to check the database."""
    print("Checking database on Azure instance...")
    
    # Test root endpoint (should return database connection status)
    root_response = query_endpoint("/")
    print(f"Root endpoint response: {root_response}")
    
    # Check if we can get the list of users (which works based on previous tests)
    users_data = query_endpoint("/api/users")
    if isinstance(users_data, list):
        print(f"Users endpoint returned {len(users_data)} users:")
        for user in users_data:
            print(f"  - User ID: {user.get('id')}, Username: {user.get('username')}")
    else:
        print(f"Users endpoint returned: {users_data}")
    
    # Try to access posts data
    posts_data = query_endpoint("/api/posts")
    print(f"Posts endpoint returned: {posts_data}")
    
    # Create a special debug endpoint that will check the database tables
    print("\nCreating custom debug script to check database tables...")
    # We can't actually create a custom endpoint on Azure from here,
    # but we can explain what needs to be done
    
    print("\nTo properly diagnose the database issue:")
    print("1. Add a temporary debug endpoint to app.py:")
    print("   @app.route('/api/debug/database')")
    print("   def debug_database():")
    print("       conn = get_db()")
    print("       # Check tables")
    print("       cursor = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")")
    print("       tables = [row['name'] for row in cursor.fetchall()]")
    print("       ")
    print("       # Check posts table")
    print("       posts_count = 0")
    print("       if 'posts' in tables:")
    print("           cursor = conn.execute(\"SELECT COUNT(*) FROM posts\")")
    print("           posts_count = cursor.fetchone()[0]")
    print("       ")
    print("       return jsonify({")
    print("           'tables': tables,")
    print("           'posts_count': posts_count,")
    print("           'database_path': DATABASE")
    print("       })")
    
    print("\n2. Deploy the updated app.py to Azure")
    print("3. Access the /api/debug/database endpoint to check if:")
    print("   - The 'posts' table exists")
    print("   - There are any post records in the table")
    print("   - The database is being accessed from the correct location")

if __name__ == "__main__":
    main() 