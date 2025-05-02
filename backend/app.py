"""
Flask Backend Application
------------------------
This file is the main entry point for the Flask backend application.
It sets up a web server with API endpoints that connect to an SQLite database.
"""

from flask import Flask, g, jsonify, request  # Flask web framework, global context, JSON response helper, request parser
import sqlite3                       # SQLite database library
from flask_cors import CORS          # Cross-Origin Resource Sharing (allows frontend to call backend APIs)
import datetime                      # For timestamp handling
import os                           # For environment variables

# Create a new Flask application
app = Flask(__name__)
# Configure CORS with explicit settings to ensure all operations work properly
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"], 
                               "allow_headers": ["Content-Type", "Authorization"]}})

# Database configuration
# Use a path that works in both local development and Azure deployment
DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(DATABASE_DIR, 'database.db')

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
# @app.route('/api/users', methods=['GET']) # Route removed as users table is not used by frontend
# def get_users():
#     db = get_db()  # Get database connection
#     cursor = db.execute('SELECT * FROM users')  # Query all users
#     
#     # Convert database rows to dictionaries for JSON serialization
#     users = [dict(id=row[0], username=row[1], email=row[2]) for row in cursor.fetchall()]
#     
#     return jsonify(users)  # Return as JSON response

'''
Health check endpoint to verify the backend is running.

This is used by the frontend to check if it can connect to the backend.

Returns:
    flask.Response: JSON with status information
'''
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Flask backend is running"})

'''
Get all comments for a specific post.

Args:
    post_id (int): ID of the post to get comments for
    
Returns:
    flask.Response: JSON response with comments data
'''
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY timestamp DESC', (post_id,))
    
    # Convert database rows to dictionaries for JSON serialization
    comments = [dict(id=row[0], post_id=row[1], content=row[2], timestamp=row[3]) for row in cursor.fetchall()]
    
    return jsonify(comments)

'''
Add a new comment to a specific post.

Args:
    post_id (int): ID of the post to add a comment to
    
Returns:
    flask.Response: JSON response with the newly created comment
'''
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_post_comment(post_id):
    # Get the request data as JSON
    request_data = request.get_json()
    
    # Check if the required field exists
    if not request_data or 'content' not in request_data:
        return jsonify({"error": "Comment content is required"}), 400
    
    content = request_data['content']
    
    # Insert the new comment into the database
    db = get_db()
    cursor = db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (post_id, content))
    db.commit()
    
    # Get the ID of the newly inserted comment
    new_id = cursor.lastrowid
    
    # Get the current timestamp in ISO format
    timestamp = datetime.datetime.now().isoformat()
    
    # Return the new comment as JSON
    return jsonify({
        "id": new_id,
        "post_id": post_id,
        "content": content,
        "timestamp": timestamp,
        "message": "Comment added successfully"
    }), 201

'''
Delete a comment.

Args:
    comment_id (int): ID of the comment to delete
    
Returns:
    flask.Response: JSON response with result of deletion
'''
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    db = get_db()
    
    # Check if the comment exists
    cursor = db.execute('SELECT id FROM comments WHERE id = ?', (comment_id,))
    comment = cursor.fetchone()
    
    if not comment:
        return jsonify({"error": f"Comment with ID {comment_id} not found"}), 404
    
    # Delete the comment
    db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    db.commit()
    
    return jsonify({"message": f"Comment {comment_id} deleted successfully"}), 200

# Start the Flask application when run directly
if __name__ == '__main__':
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Get debug mode from environment variable (defaults to False)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Note: Port 5001 is used because port 5000 is often in use on macOS
    app.run(host='0.0.0.0', debug=debug_mode, port=port) 