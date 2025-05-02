"""
Debug utilities for diagnosing database and deployment issues
"""
import os
import sqlite3
import datetime
import sys

def debug_database(db_path="database.db"):
    """
    Print detailed database information for debugging
    
    Args:
        db_path: Path to the database file to debug (default: database.db)
    """
    print("\n===== DATABASE DEBUG INFO =====")
    
    # 1. Check environment
    print("\n--- Environment: ---")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    print(f"Python version: {sys.version}")
    
    # 2. Check database file
    print(f"\n--- Database file check: ---")
    if os.path.exists(db_path):
        print(f"Database exists at: {db_path}")
        print(f"Database size: {os.path.getsize(db_path)} bytes")
        print(f"Created: {datetime.datetime.fromtimestamp(os.path.getctime(db_path))}")
        print(f"Last modified: {datetime.datetime.fromtimestamp(os.path.getmtime(db_path))}")
        print(f"Owner/permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
    else:
        print(f"Database NOT found at: {db_path}")
        
        # Check if it's in another common directory
        for check_dir in ['/home/site/wwwroot', '/tmp', '.']:
            check_path = os.path.join(check_dir, 'database.db')
            if os.path.exists(check_path):
                print(f"But found at: {check_path}")
                db_path = check_path
                break
    
    # 3. Check site-packages directory to see if initialization is happening there
    site_packages = None
    for p in sys.path:
        if "site-packages" in p:
            site_packages = p
            break
    
    if site_packages:
        print(f"\n--- Site-packages check: ---")
        print(f"Site-packages directory: {site_packages}")
        if os.path.exists(os.path.join(site_packages, 'database.db')):
            print(f"WARNING: Database found in site-packages - this could cause persistence issues")
    
    # 4. Check DATABASE_DIR environment variable
    print("\n--- Environment variables: ---")
    db_dir = os.environ.get('DATABASE_DIR', 'Not set')
    print(f"DATABASE_DIR = {db_dir}")
    
    if db_dir != 'Not set' and os.path.exists(os.path.join(db_dir, 'database.db')):
        print(f"Database found at DATABASE_DIR location")
        db_path = os.path.join(db_dir, 'database.db')
    
    # 5. Dump table info and recent comments
    try:
        print("\n--- Database content: ---")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Comments count
        cursor.execute("SELECT COUNT(*) FROM comments")
        count = cursor.fetchone()[0]
        print(f"Total comments: {count}")
        
        # Recent comments
        cursor.execute("SELECT id, post_id, content, timestamp FROM comments ORDER BY id DESC LIMIT 5")
        comments = cursor.fetchall()
        print("\nMost recent comments:")
        for c in comments:
            print(f"  ID {c['id']}: Post {c['post_id']} - '{c['content']}' (at {c['timestamp']})")
        
        conn.close()
    except Exception as e:
        print(f"Error accessing database: {e}")
    
    # 6. Check startup script
    print("\n--- Startup script check: ---")
    startup_path = "startup.sh"
    if os.path.exists(startup_path):
        print(f"Startup script exists at: {startup_path}")
        with open(startup_path, 'r') as f:
            content = f.read()
            print("Startup script content:")
            print("---")
            print(content)
            print("---")
    else:
        print("Startup script not found in current directory")
    
    print("\n===== END DEBUG INFO =====")

if __name__ == "__main__":
    # Allow specifying a custom database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database.db"
    debug_database(db_path) 