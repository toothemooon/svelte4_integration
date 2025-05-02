#!/bin/bash
# Startup script for Azure Web App (Python/Flask)

echo "--- Starting Azure Startup Script ---"
echo "Timestamp: $(date)"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Listing directory contents:"
ls -la

# Navigate to the site root where the code is deployed
# Azure deploys content to /home/site/wwwroot
APP_ROOT="/home/site/wwwroot"
echo "Changing to application root: $APP_ROOT"
cd "$APP_ROOT" || exit 1

echo "--- Environment Setup ---"
# Create persistent directory for the database if it doesn't exist
# Place data outside wwwroot if possible, but /home/site is writeable
PERSIST_DIR="/home/site/data" # Using /home/site instead of /home/site/wwwroot/data
echo "Ensuring persistent data directory exists at $PERSIST_DIR"
mkdir -p "$PERSIST_DIR"
ls -la /home/site # List contents to verify data dir

# Set environment variable for the database location
export DATABASE_DIR="$PERSIST_DIR"
export FLASK_ENV="production" # Set environment to production
export FLASK_APP="app:app"    # Explicitly set the Flask app
export FLASK_DEBUG="1"        # Enable debug for more verbose logs
export PYTHONUNBUFFERED="1"   # Ensure Python output is not buffered
echo "DATABASE_DIR environment variable set to: $DATABASE_DIR"
echo "FLASK_ENV set to: $FLASK_ENV"
echo "FLASK_APP set to: $FLASK_APP"
echo "FLASK_DEBUG set to: $FLASK_DEBUG"

echo "--- Dependency Installation ---"
# Ensure pip is up-to-date
python -m pip install --upgrade pip
echo "Installing dependencies from requirements.txt..."
# Use --no-cache-dir to prevent potential issues with caching in Azure
if pip install --no-cache-dir -r requirements.txt; then
    echo "Dependencies installed successfully."
else
    echo "Error installing requirements.txt. Trying individual installs..."
    # Force install critical packages individually
    pip install --no-cache-dir Flask==2.0.1
    pip install --no-cache-dir Werkzeug==2.0.1
    pip install --no-cache-dir Flask-Cors==3.0.10
    pip install --no-cache-dir PyJWT==2.8.0
    pip install --no-cache-dir gunicorn
fi

echo "Verifying Flask-CORS installation:"
pip show Flask-Cors

echo "Listing installed packages:"
pip list

echo "--- Database and Admin User Setup ---"
# Check if the database file exists, initialize if not
DATABASE_PATH="$DATABASE_DIR/database.db"
echo "Looking for database at: $DATABASE_PATH"
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Database file not found at $DATABASE_PATH. Initializing database..."
    # Run init_db.py to create schema ONLY if the file doesn't exist
    # This assumes init_db.py creates the database file in DATABASE_DIR
    if python init_db.py; then
        echo "Database initialized successfully."
        echo "Database contents:"
        ls -la "$DATABASE_DIR"
    else
        echo "Error initializing database. Error code: $?"
        echo "Continuing but expect problems..."
    fi
else
    echo "Database file found at $DATABASE_PATH."
    echo "Database size: $(du -h "$DATABASE_PATH")"
    # Print some database info using sqlite3 command if available
    if command -v sqlite3 &> /dev/null; then
        echo "Tables in database:"
        sqlite3 "$DATABASE_PATH" ".tables"
    fi
fi

# Ensure the admin user exists
# We'll create a specific admin account with fixed credentials for testing
echo "Ensuring admin user exists..."
cat > /tmp/ensure_admin.py << 'EOF'
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secure_password123"  # Should match the local admin password

DATABASE_DIR = os.environ.get('DATABASE_DIR', '/home/site/data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'database.db')

def ensure_admin_exists():
    print(f"Checking for admin user in {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if the admin user exists
        cursor.execute("SELECT id, username, role FROM users WHERE username = ?", (ADMIN_USERNAME,))
        admin = cursor.fetchone()
        
        if admin:
            admin_id, username, role = admin["id"], admin["username"], admin["role"]
            print(f"Admin user found: {username} (ID: {admin_id}, Role: {role})")
            
            # Ensure the user has admin role
            if role != 'admin':
                cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (admin_id,))
                conn.commit()
                print(f"Updated user '{username}' to admin role")
                
            return True
        else:
            # Create admin user
            print("Admin user not found. Creating...")
            hashed_password = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (ADMIN_USERNAME, hashed_password, 'admin')
            )
            conn.commit()
            
            admin_id = cursor.lastrowid
            print(f"Created admin user '{ADMIN_USERNAME}' with ID: {admin_id}")
            
            # Verify database tables and count records
            print("Database tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} records")
                
            return True
            
    except Exception as e:
        print(f"Error ensuring admin exists: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if ensure_admin_exists():
        print("Admin user setup complete.")
    else:
        print("Failed to ensure admin user exists.")
EOF

# Run the admin creation script
python /tmp/ensure_admin.py
echo "Admin setup complete."

# Ensure the superadmin user exists (using the dedicated script)
# Path is relative to APP_ROOT (/home/site/wwwroot)
echo "Ensuring superadmin user exists..."
if python scripts/admin_scripts/ensure_admin.py; then
    echo "Superadmin check/creation successful."
else
    echo "Error running ensure_admin.py. Error code: $?"
    echo "Continuing anyway..."
fi

# Create a routes verification script
echo "Creating Flask routes verification script..."
cat > /tmp/check_routes.py << 'EOF'
import os
import sys
import app

def print_routes():
    """Print all registered routes in the Flask app"""
    print("\n=== REGISTERED FLASK ROUTES ===")
    
    if not hasattr(app, 'app'):
        print("ERROR: app object not found in app module. Check your imports.")
        return
    
    flask_app = app.app
    
    # Get all registered routes
    routes = []
    for rule in flask_app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        routes.append((rule.endpoint, methods, str(rule)))
    
    # Sort routes by endpoint
    routes.sort(key=lambda x: x[0])
    
    # Print routes in a table format
    print(f"{'Endpoint':<30} {'Methods':<20} {'URL Path'}")
    print("-" * 80)
    for endpoint, methods, url in routes:
        print(f"{endpoint:<30} {methods:<20} {url}")
    
    # Check for specific routes we know should exist
    print("\n=== ROUTE VERIFICATION ===")
    found_routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
    
    critical_routes = [
        '/api/posts',
        '/api/health', 
        '/api/login',
        '/'
    ]
    
    for route in critical_routes:
        if any(route in r for r in found_routes):
            print(f"✅ Route '{route}' is properly registered")
        else:
            print(f"❌ Route '{route}' is MISSING!")
    
    # Print the app's configuration
    print("\n=== APP CONFIGURATION ===")
    print(f"Debug mode: {flask_app.debug}")
    print(f"Testing mode: {flask_app.testing}")
    print(f"Secret key set: {'Yes' if flask_app.secret_key else 'No'}")
    
    # Check if Flask-CORS is properly initialized
    if hasattr(flask_app, 'after_request_funcs'):
        has_cors = any('flask_cors' in str(func) for funcs in flask_app.after_request_funcs.values() for func in funcs)
        print(f"CORS middleware: {'Yes' if has_cors else 'No'}")
    else:
        print("CORS middleware: Cannot detect")

if __name__ == "__main__":
    print_routes()
EOF

# Run the routes verification script
echo "Verifying Flask routes..."
python /tmp/check_routes.py

echo "--- Starting Application ---"
echo "Starting Gunicorn server with debug logging..."
# Bind to 0.0.0.0 and the port Azure expects (usually 8000 for Python Web Apps)
# Increase log level and timeout for better debugging
# Use only 1 worker to simplify debugging
# Increase timeout for better debugging
GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=1 --threads=4 --log-level=debug --timeout=120 --access-logfile - --error-logfile - --reload"
echo "Gunicorn command: gunicorn $GUNICORN_CMD_ARGS app:app"

gunicorn $GUNICORN_CMD_ARGS app:app

echo "--- Startup Script Finished --- Gunicorn exited? ---"
# If Gunicorn exits, the container might restart. This line might not be reached. 