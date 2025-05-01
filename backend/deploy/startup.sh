#!/bin/bash
# Very simple startup script for Azure

# Enable bash tracing for debugging
set -x

# Display current directory and files
echo "Current directory: $(pwd)"
ls -la

# Install dependencies
echo "Installing dependencies..."
pip install Flask==2.0.1 Werkzeug==2.0.1 Flask-Cors==3.0.10 gunicorn

# Start the application using gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 app:app 