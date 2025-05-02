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
echo "DATABASE_DIR environment variable set to: $DATABASE_DIR"
echo "FLASK_ENV set to: $FLASK_ENV"
echo "FLASK_APP set to: $FLASK_APP"

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
    # This assumes init_db.py creates the database file in DATABASE_DIR
    if python init_db.py; then
        echo "Database initialized successfully."
    else
        echo "Error initializing database. Continuing but logging error..."
    fi
else
    echo "Database file found at $DATABASE_PATH."
fi

# Ensure the superadmin user exists (using the dedicated script)
# Path is relative to APP_ROOT (/home/site/wwwroot)
echo "Ensuring superadmin user exists..."
if python scripts/admin_scripts/ensure_admin.py; then
    echo "Superadmin check/creation successful."
else
    echo "Error running ensure_admin.py. Continuing..."
    # Log error but continue, admin might exist or manual intervention needed
fi

echo "--- Starting Application ---"
echo "Starting Gunicorn server..."
# Bind to 0.0.0.0 and the port Azure expects (usually 8000 for Python Web Apps)
# Use environment variables for configuration where possible
GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=2 --log-level=info --access-logfile - --error-logfile -"
echo "Gunicorn command: gunicorn $GUNICORN_CMD_ARGS app:app"

gunicorn $GUNICORN_CMD_ARGS app:app

echo "--- Startup Script Finished --- Gunicorn exited? ---"
# If Gunicorn exits, the container might restart. This line might not be reached. 