"""
Flask Backend Application
------------------------
This file is the main entry point for the Flask backend application.
It sets up a web server with API endpoints that connect to an SQLite database.
"""

from flask import Flask, g, jsonify  # Flask web framework, global context, JSON response helper
import sqlite3                       # SQLite database library
from flask_cors import CORS          # Cross-Origin Resource Sharing (allows frontend to call backend APIs)

# Create a new Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes, allowing the frontend to make API calls to this backend

# Database configuration
DATABASE = 'database.db'  # Name of the SQLite database file stored in the project directory

'''
Get a database connection. 

This function creates a new connection if one doesn't exist yet, or returns an
existing connection stored in Flask's 'g' object (which lasts for the duration
of a request).

Returns:
    sqlite3.Connection: A database connection
'''
def get_db():
    db = getattr(g, '_database', None)  # Check if connection already exists
    if db is None:  # If no existing connection
        # Create a new connection
        db = g._database = sqlite3.connect(DATABASE)
        # Configure to return rows that can be accessed by column name
        db.row_factory = sqlite3.Row
    return db

'''
Automatically close the database connection when the request ends.

This function is registered with Flask to run when a request context
ends, ensuring we don't leave database connections open.

Args:
    exception: Any exception that occurred during the request
'''
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()  # Close the connection if it exists

'''
Initialize the database with tables and schema.

This function reads the schema.sql file and executes the SQL commands
to create the database structure. Called by init_db.py when setting up
the application.
'''
def init_db():
    with app.app_context():  # Create a Flask application context
        db = get_db()  # Get a database connection
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())  # Execute the SQL commands
        db.commit()  # Commit the changes

# API Routes

'''
Root endpoint - Simple database connection test.

Returns:
    str: A message indicating the database connection is working
'''
@app.route('/')
def index():
    db = get_db()  # Get database connection
    cursor = db.execute('SELECT 1')  # Run a simple query
    result = cursor.fetchone()  # Get the first result
    return f"Database connection successful: {result[0]}"

'''
Get all users from the database.

This endpoint returns a JSON array containing all users in the database.

Returns:
    flask.Response: JSON response with user data
'''
@app.route('/api/users', methods=['GET'])
def get_users():
    db = get_db()  # Get database connection
    cursor = db.execute('SELECT * FROM users')  # Query all users
    
    # Convert database rows to dictionaries for JSON serialization
    users = [dict(id=row[0], username=row[1], email=row[2]) for row in cursor.fetchall()]
    
    return jsonify(users)  # Return as JSON response

'''
Health check endpoint to verify the backend is running.

This is used by the frontend to check if it can connect to the backend.

Returns:
    flask.Response: JSON with status information
'''
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Flask backend is running"})

# Start the Flask application when run directly
if __name__ == '__main__':
    # Run the app in debug mode (shows detailed errors) on port 5001
    # Note: Port 5001 is used because port 5000 is often in use on macOS
    app.run(debug=True, port=5001) 