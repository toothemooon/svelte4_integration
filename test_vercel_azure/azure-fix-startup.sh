#!/bin/bash
# Improved startup script for Azure with fixed database persistence

# Enable tracing for debugging
set -x

# Check current environment
echo "Current directory: $(pwd)"
ls -la

# Install dependencies
echo "Installing dependencies..."
pip install Flask==2.0.1 Werkzeug==2.0.1 Flask-Cors==3.0.10 gunicorn

# Create a more permanent storage directory - Azure's persistent storage
# /home/site/wwwroot is persistent across restarts
PERSISTENT_DIR="/home/site/wwwroot/data"
mkdir -p "$PERSISTENT_DIR"

# Show all environment variables (for debugging)
echo "Environment variables:"
printenv | sort

# Make the database directory available as an environment variable
# This must be the ABSOLUTE path, so Flask can find it
export DATABASE_DIR="$PERSISTENT_DIR"
echo "Set DATABASE_DIR=$DATABASE_DIR"

# Run the debug script to check environment
echo "Running debug script..."
python test_vercel_azure/debug_azure.py > "$PERSISTENT_DIR/debug_log.txt" 2>&1
cat "$PERSISTENT_DIR/debug_log.txt"

# Now patch the Flask app to use the correct database path
# This ensures app.py looks in the right place for the database
echo 'Patching app.py to use persistent database location...'
cat > app_patch.py << 'EOF'
import os
print("Patching app.py to use persistent directory...")
with open('app.py', 'r') as f:
    content = f.read()

# Update the DATABASE_DIR line to use absolute path
content = content.replace(
    "DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))",
    "DATABASE_DIR = os.environ.get('DATABASE_DIR', '/home/site/wwwroot/data')"
)

with open('app.py', 'w') as f:
    f.write(content)
print("Patched app.py successfully")
EOF
python app_patch.py

# Copy our improved init_db script
cp test_vercel_azure/init_db_persistent.py init_db.py

# Only initialize the database if it doesn't exist
if [ ! -f "$DATABASE_DIR/database.db" ]; then
    echo "Database not found, initializing at $DATABASE_DIR/database.db ..."
    python init_db.py
else
    echo "Database already exists at $DATABASE_DIR/database.db"
fi

# Log what database we're using
echo "Final database path: $DATABASE_DIR/database.db"
ls -la "$DATABASE_DIR"

# Start the application using gunicorn
echo "Starting Gunicorn server with patched app..."
gunicorn --bind=0.0.0.0:8000 app:app 