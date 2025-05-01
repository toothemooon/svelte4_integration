#!/bin/bash

# Enable bash tracing for debugging
set -x

# Display current directory and files
echo "Current directory: $(pwd)"
ls -la

# Install dependencies if needed
echo "Installing dependencies..."
pip install Flask==2.0.1 Werkzeug==2.0.1 Flask-Cors==3.0.10 gunicorn

# Copy our persistent init_db script
echo "Setting up persistent init_db..."
cp test_vercel_azure/init_db_persistent.py init_db.py

# Use our modified init_db that preserves data
echo "Running database initialization (will skip if DB exists)..."
python init_db.py

# Start the application using gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 app:app 