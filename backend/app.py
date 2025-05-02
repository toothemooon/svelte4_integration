"""
Flask Backend Application
------------------------
This file is the main entry point for the Flask backend application.
It sets up a web server with API endpoints that connect to an SQLite database.
"""

from flask import Flask, g, jsonify, request  # Flask web framework, global context, JSON response helper, request parser
import sqlite3
from queue import Queue                       # SQLite database library
from flask_cors import CORS          # Cross-Origin Resource Sharing (allows frontend to call backend APIs)
import datetime                      # For timestamp handling
import os                           # For environment variables
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
try:
    # Try standard import first
    import jwt
except ImportError:
    # If standard import fails, attempt to import from installed package
    try:
        import PyJWT as jwt
    except ImportError:
        # If all imports fail, report error
        raise ImportError("JWT module could not be imported. Please install with: pip install PyJWT")
from datetime import datetime, timedelta # For JWT expiration
from functools import wraps # For creating decorators
import sys # For sys.path

# Create a new Flask application
app = Flask(__name__)

# Define allowed origins for CORS
# Get frontend URL from environment variable or default
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://www.sarada.lol') # Add your Vercel/frontend URL
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "https://www.sarada.lol",    # Explicitly include with www
    "https://sarada.lol",        # Explicitly include without www
    "http://www.sarada.lol",    # HTTP version with www
    "http://sarada.lol",        # HTTP version without www
    "http://localhost:5173",     # For local Svelte development
    "http://127.0.0.1:5173"      # Also for local Svelte development
]

# Configure CORS more specifically
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
    r"/": {"origins": ALLOWED_ORIGINS}  # Add root endpoint
})

# Database configuration
# Use a path that works in both local development and Azure deployment
# Update the database path handling
DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(DATABASE_DIR, 'database.db')

# Ensure directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)
print(f"Database path: {DATABASE}")  # Log the path for debugging

# --- Configuration --- 
# IMPORTANT: Use environment variables for production secrets!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_very_secret_key_change_me')

'''
Get a database connection. 

This function creates a new connection if one doesn't exist yet, or returns an
existing connection stored in Flask's 'g' object (which lasts for the duration
of a request).

Returns:
    sqlite3.Connection: A database connection
'''
# Update get_db() function
# Add to top of app.py
from sqlite3 import connect
from queue import Queue

# Connection pool setup
class SQLiteConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self._connections = Queue(max_connections)
        for _ in range(max_connections):
            conn = connect(DATABASE, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._connections.put(conn)

    def get_connection(self):
        return self._connections.get()

    def return_connection(self, conn):
        self._connections.put(conn)

connection_pool = SQLiteConnectionPool()

# Update get_db() function
def get_db():
    if 'db' not in g:
        g.db = connection_pool.get_connection()
    return g.db

# Update teardown_appcontext
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        connection_pool.return_connection(db)

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
    # Admin user hook - ensures admin user exists after database init
    try:
        # Check if admin_scripts module exists and call ensure_admin
        from scripts.admin_scripts.ensure_admin import ensure_admin_exists
        ensure_admin_exists()
    except ImportError:
        print("Admin scripts not found - skipping admin user creation")
    except Exception as e:
        print(f"Error creating admin user: {e}")

# --- Authentication Decorators ---
'''
Decorator to protect routes that require authentication.

This decorator checks for a valid JWT token in the request headers
and passes the authenticated user to the decorated function.

Returns:
    function: The decorated function with user authentication
'''
# Update the token_required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                auth_header = request.headers['Authorization']
                if not auth_header.startswith('Bearer '):
                    return jsonify({'message': 'Invalid authorization header format'}), 401
                token = auth_header.split(" ")[1]
            except Exception as e:
                return jsonify({'message': f'Authorization header error: {str(e)}'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            db = get_db()
            cursor = db.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],))
            current_user = cursor.fetchone()
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401
        except Exception as e:
            app.logger.error(f'Token validation error: {e}')
            return jsonify({'message': 'Token validation failed'}), 401

        return f(current_user, *args, **kwargs)
    return decorated
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
Health check endpoint to verify the backend is running.

This is used by the frontend to check if it can connect to the backend.

Returns:
    flask.Response: JSON with status information
'''
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Flask backend is running"})

'''
Get all users (for testing purposes).

Returns:
    flask.Response: JSON response with a list of all users
'''
@app.route('/api/users', methods=['GET'])
def get_users():
    db = get_db()
    cursor = db.execute('SELECT id, username, timestamp FROM users')
    
    # Convert rows to dictionaries without password hash
    users = []
    for row in cursor.fetchall():
        user_dict = dict(id=row['id'], username=row['username'], timestamp=row['timestamp'])
        users.append(user_dict)
    
    return jsonify(users)

'''
Debug endpoint to check database tables and configuration.
'''
@app.route('/api/debug/database', methods=['GET'])
def debug_database():
    """Debug endpoint to check database tables and contents."""
    conn = get_db()
    # Check tables
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    
    # Check posts table
    posts_count = 0
    if 'posts' in tables:
        cursor = conn.execute("SELECT COUNT(*) FROM posts")
        posts_count = cursor.fetchone()[0]
    
    return jsonify({
        'tables': tables,
        'posts_count': posts_count,
        'database_path': DATABASE
    })

'''
Get all posts from the database.

Returns:
    flask.Response: JSON response with a list of all posts
'''
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts from the database, including user data."""
    try:
        db = get_db()
        
        # Simple query to get posts with author usernames
        query = """
        SELECT 
            posts.id, 
            posts.title, 
            posts.content, 
            posts.timestamp, 
            users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
        """
        
        posts = db.execute(query).fetchall()
        
        # Convert posts to list of dictionaries
        post_list = []
        for post in posts:
            post_dict = {
                'id': post['id'],
                'title': post['title'],
                'content': post['content'],
                'timestamp': post['timestamp'],
                'username': post['username']
            }
            post_list.append(post_dict)
        
        return jsonify(post_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

'''
Get a single post by its ID.

Args:
    post_id (int): ID of the post to retrieve

Returns:
    flask.Response: JSON response with the post data or 404 error
'''
@app.route('/api/posts/<int:post_id>', methods=['GET', 'DELETE'])
def get_or_delete_post(post_id):
    if request.method == 'GET':
        return get_post_by_id(post_id)
    elif request.method == 'DELETE':
        # Check for authentication
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Bearer token malformed'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token using the secret key
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Find the user based on the token data
            db = get_db()
            cursor = db.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],))
            current_user = cursor.fetchone()
            if not current_user:
                 return jsonify({'message': 'User not found'}), 401
                
        except Exception as e:
            return jsonify({'message': f'Authentication error: {str(e)}'}), 401

        # User is authenticated, proceed with deletion
        return delete_post(current_user, post_id)

def get_post_by_id(post_id):
    db = get_db()
    cursor = db.execute('SELECT id, title, content, timestamp FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if post is None:
        return jsonify({"error": f"Post with ID {post_id} not found"}), 404
    
    # Convert the row to a dictionary
    post_dict = dict(id=post['id'], title=post['title'], content=post['content'], timestamp=post['timestamp'])
    
    return jsonify(post_dict)

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
    timestamp = datetime.now().isoformat()
    
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

# --- User Authentication Routes ---

'''
Register a new user.
'''
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400

    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    db = get_db()
    try:
        cursor = db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        db.commit()
    except sqlite3.IntegrityError: # Handles UNIQUE constraint violation for username
        return jsonify({'message': 'Username already exists'}), 409 # 409 Conflict
    except Exception as e:
        db.rollback()
        print(f"Registration error: {e}")
        return jsonify({'message': 'Registration failed'}), 500

    return jsonify({'message': 'User registered successfully'}), 201

'''
Login a user and return a JWT.
'''
@app.route('/api/login', methods=['POST'])
def login():
    # Get the request data as JSON
    request_data = request.get_json()
    
    # Validate request data
    if not request_data or not 'username' in request_data or not 'password' in request_data:
        return jsonify({'message': 'Missing username or password'}), 400
    
    username = request_data['username']
    password = request_data['password']
    
    # Connect to database
    db = get_db()
    
    # Find the user
    cursor = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    # Generate JWT token
    token_payload = {
        'user_id': user['id'],
        'username': user['username'],
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
    
    # Return token with user information
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username']
        }
    })

'''
Add a new blog post (Protected Route).

This endpoint receives post data (title, content) and adds it to the posts table.
Requires authentication.
'''
@app.route('/api/posts', methods=['POST'])
@token_required
def add_post(current_user):
    """Create a new post."""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Title and content are required"}), 400
    
    title = data['title'].strip()
    content = data['content'].strip()
    
    if not title or not content:
        return jsonify({"error": "Title and content cannot be empty"}), 400

    try:
        db = get_db()
        cursor = db.execute(
            'INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)',
            (title, content, current_user['id'])
        )
        db.commit()
        
        # Get the newly created post
        new_post = db.execute(
            'SELECT id, title, content, timestamp FROM posts WHERE id = ?',
            (cursor.lastrowid,)
        ).fetchone()
        
        return jsonify({
            "id": new_post['id'],
            "title": new_post['title'],
            "content": new_post['content'],
            "timestamp": new_post['timestamp'],
            "message": "Post created successfully"
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Failed to create post"}), 500

'''
Edit an existing blog post (Protected Route).

Args:
    post_id (int): ID of the post to edit

This route allows users to edit their own posts.

Returns:
    flask.Response: JSON with updated post data
'''
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@token_required
def edit_post(current_user, post_id):
    """Edit an existing post."""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    title = data['title'].strip()
    content = data['content'].strip()
    
    if not title or not content:
        return jsonify({'error': 'Title and content cannot be empty'}), 400

    try:
        db = get_db()
        
        # Check if post exists and user is owner
        post = db.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,)).fetchone()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        if post['user_id'] != current_user['id']:
            return jsonify({'error': 'Not authorized to edit this post'}), 403
        
        # Update post
        db.execute(
            'UPDATE posts SET title = ?, content = ? WHERE id = ?',
            (title, content, post_id)
        )
        db.commit()
        
        # Get updated post
        updated_post = db.execute(
            'SELECT id, title, content, timestamp FROM posts WHERE id = ?',
            (post_id,)
        ).fetchone()
        
        return jsonify({
            'id': updated_post['id'],
            'title': updated_post['title'],
            'content': updated_post['content'],
            'timestamp': updated_post['timestamp'],
            'message': 'Post updated successfully'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to update post'}), 500

def delete_post(current_user, post_id):
    """Delete a post."""
    try:
        db = get_db()
        
        # Check if post exists and user is owner
        post = db.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,)).fetchone()
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        if post['user_id'] != current_user['id']:
            return jsonify({'error': 'Not authorized to delete this post'}), 403
        
        # Delete post
        db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        db.commit()
        
        return jsonify({'message': 'Post deleted successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Failed to delete post'}), 500

# Start the Flask application when run directly
if __name__ == '__main__':
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Get debug mode from environment variable (defaults to False)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Note: Port 5001 is used because port 5000 is often in use on macOS
    app.run(host='0.0.0.0', debug=debug_mode, port=port) 