#!/bin/bash
# Startup script for Azure Web App (Python/Flask)

echo "--- Starting Azure Startup Script ---"
echo "Timestamp: $(date)"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Listing directory contents:"
ls -la

# Navigate to the site root where the code is deployed
cd /home/site/wwwroot

echo "--- Environment Setup ---"
# Create persistent directory for the database if it doesn't exist
PERSIST_DIR="/home/site/wwwroot/data"
echo "Ensuring persistent data directory exists at $PERSIST_DIR"
mkdir -p "$PERSIST_DIR"
ls -la /home/site/wwwroot # List contents to verify data dir

# Set environment variable for the database location
export DATABASE_DIR="$PERSIST_DIR"
echo "DATABASE_DIR environment variable set to: $DATABASE_DIR"

echo "--- Dependency Installation ---"
# Ensure pip is up-to-date
python -m pip install --upgrade pip
echo "Installing dependencies from requirements.txt..."
# Use --no-cache-dir to prevent potential issues with caching in Azure
if pip install --no-cache-dir -r requirements.txt; then
    echo "Dependencies installed successfully."
else
    echo "Error installing dependencies. Exiting."
    exit 1
fi

echo "Listing installed packages:"
pip list

echo "--- Database and Admin User Setup ---"
# Check if the database file exists, initialize if not
DATABASE_PATH="$DATABASE_DIR/database.db"
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Database file not found at $DATABASE_PATH. Initializing database..."
    # Run init_db.py to create schema ONLY if the file doesn't exist
    # This assumes init_db.py creates the database file
    if python init_db.py; then
        echo "Database initialized successfully."
    else
        echo "Error initializing database. Exiting."
        # Decide if we should exit or continue - let's continue but log the error
        echo "Continuing despite DB init error..."
    fi
else
    echo "Database file found at $DATABASE_PATH."
fi

# Ensure the superadmin user exists (using the dedicated script)
# Make sure the path to the script is correct relative to /home/site/wwwroot
echo "Ensuring superadmin user exists..."
if python scripts/admin_scripts/ensure_admin.py; then
    echo "Superadmin check/creation successful."
else
    echo "Error running ensure_admin.py. Continuing..."
    # Log error but continue, admin might exist or manual intervention needed
fi

echo "--- Starting Application ---"
echo "Starting Gunicorn server (simplified command)..."
# Bind to 0.0.0.0 and the port Azure expects (usually 8000 for Python)
# Simplified command for debugging
gunicorn app:app --bind=0.0.0.0:8000

echo "--- Startup Script Finished ---" 