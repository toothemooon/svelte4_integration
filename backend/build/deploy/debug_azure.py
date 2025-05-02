"""
Debug script to diagnose Azure database persistence issues

This script is now a thin wrapper around the debug utilities in the tests module.
"""
import os
import sys

# Add the parent's parent directory to the path so we can import from tests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the debug function from the tests module
from tests.debug_utils import debug_database

if __name__ == "__main__":
    # Allow specifying a custom database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database.db"
    debug_database(db_path) 