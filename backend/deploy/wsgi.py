"""
WSGI entry point for production deployment
-----------------------------------------
This file is used by production servers (like Gunicorn) to run the application.
"""

import sys
import os

# Add current directory to path for module imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application
from app import app as application

# This allows Azure to find the app
app = application

if __name__ == "__main__":
    # This is used when this file is run directly
    application.run() 