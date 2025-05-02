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

# Create a new Flask application
app = Flask(__name__)
# Configure CORS with explicit settings to ensure all operations work properly
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
                               "allow_headers": ["Content-Type", "Authorization"]}})

# Database configuration
# Use a path that works in both local development and Azure deployment
DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(DATABASE_DIR, 'database.db')

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
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check for token in 'Authorization: Bearer <token>' header
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
            # Find the user based on the token data (e.g., user_id)
            db = get_db()
            cursor = db.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],))
            current_user = cursor.fetchone()
            if not current_user:
                 return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"Token validation error: {e}") # Log the error
            return jsonify({'message': 'Token validation failed'}), 401

        # Pass the current user information to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated

'''
Decorator to protect routes that require admin privileges.

This decorator first authenticates the user and then checks if they have
the 'admin' role before allowing access to the protected route.

Returns:
    function: The decorated function with admin authorization
'''
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # First, authenticate the user (reuse token_required logic)
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
            # Find the user based on the token data (e.g., user_id)
            db = get_db()
            cursor = db.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],))
            current_user = cursor.fetchone()
            if not current_user:
                 return jsonify({'message': 'User not found'}), 401
                 
            # Check if user has admin role
            if current_user['role'] != 'admin':
                return jsonify({'message': 'Admin privileges required'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"Token validation error: {e}") # Log the error
            return jsonify({'message': 'Token validation failed'}), 401

        # Pass the current user information to the decorated function
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
Get all posts from the database.

Returns:
    flask.Response: JSON response with a list of all posts
'''
@app.route('/api/posts', methods=['GET'])
def get_posts():
    db = get_db()
    cursor = db.execute('SELECT id, title, content, timestamp FROM posts ORDER BY timestamp DESC')
    
    # Convert rows to dictionaries, potentially creating excerpts
    posts = []
    for row in cursor.fetchall():
        post_dict = dict(id=row['id'], title=row['title'], content=row['content'], timestamp=row['timestamp'])
        # Create a simple excerpt (e.g., first 100 characters)
        post_dict['excerpt'] = (row['content'][:100] + '...') if len(row['content']) > 100 else row['content']
        posts.append(post_dict)
    
    return jsonify(posts)

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
        # Check for admin privileges
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
                 
            # Check if user has admin role
            if current_user['role'] != 'admin':
                return jsonify({'message': 'Admin privileges required'}), 403
                
        except Exception as e:
            return jsonify({'message': f'Authentication error: {str(e)}'}), 401

        # User is admin, proceed with deletion
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
    
    # Print debug information
    print(f"User found: {user['username']}, Role: {user['role']}")
    
    # Generate JWT token
    token_payload = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],  # Include role in token
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    
    print(f"Token payload: {token_payload}")
    
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
    
    # Return token with role information directly in the response
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })

'''
Add a new blog post (Protected Route).

This endpoint receives post data (title, content) and adds it to the posts table.
Requires admin role.
'''
@app.route('/api/posts', methods=['POST'])
@admin_required # Changed from @token_required to @admin_required
def add_post(current_user):
    # current_user is passed from the decorator
    request_data = request.get_json()
    
    if not request_data or 'title' not in request_data or 'content' not in request_data:
        return jsonify({"error": "Title and content are required"}), 400
    
    title = request_data['title']
    content = request_data['content']
    user_id = current_user['id'] # Get user ID from the authenticated user
    
    if not title.strip() or not content.strip():
        return jsonify({"error": "Title and content cannot be empty"}), 400

    db = get_db()
    try:
        cursor = db.execute('INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)', (title, content, user_id))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error adding post: {e}")
        return jsonify({"error": "Failed to add post"}), 500
        
    new_id = cursor.lastrowid
    
    cursor = db.execute('SELECT timestamp FROM posts WHERE id = ?', (new_id,))
    new_post_row = cursor.fetchone()
    timestamp = new_post_row['timestamp'] if new_post_row else datetime.utcnow().isoformat()

    return jsonify({
        "id": new_id,
        "title": title,
        "content": content,
        "user_id": user_id,
        "timestamp": timestamp,
        "message": "Post created successfully"
    }), 201

'''
Edit an existing blog post (Protected Route).

Args:
    post_id (int): ID of the post to edit

This route allows users to edit their own posts. Users with admin role
can edit any post.

Returns:
    flask.Response: JSON with updated post data
'''
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@token_required
def edit_post(current_user, post_id):
    # Get database connection
    db = get_db()
    
    # First, check if the post exists
    cursor = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    
    # Check if user is the owner or an admin
    is_owner = post['user_id'] == current_user['id']
    is_admin = current_user['role'] == 'admin'
    
    if not (is_owner or is_admin):
        return jsonify({'message': 'Not authorized to edit this post'}), 403
    
    # Get request data
    request_data = request.get_json()
    
    # Validate request data
    if not request_data or 'title' not in request_data or 'content' not in request_data:
        return jsonify({'message': 'Missing title or content'}), 400
    
    # Update the post
    db.execute(
        'UPDATE posts SET title = ?, content = ? WHERE id = ?',
        (request_data['title'], request_data['content'], post_id)
    )
    db.commit()
    
    # Get the updated post
    cursor = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    updated_post = cursor.fetchone()
    
    # Create a response
    post_data = {
        'id': updated_post['id'],
        'title': updated_post['title'],
        'content': updated_post['content'],
        'user_id': updated_post['user_id'],
        'timestamp': updated_post['timestamp'],
        'message': 'Post updated successfully'
    }
    
    return jsonify(post_data), 200

'''
Delete an existing blog post (Admin only).

Args:
    current_user: The admin user performing the deletion
    post_id (int): ID of the post to delete

Returns:
    flask.Response: JSON response confirming the deletion
'''
def delete_post(current_user, post_id):
    # Get database connection
    db = get_db()
    
    # First, check if the post exists
    cursor = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    
    try:
        # Delete the post
        db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        
        # Also delete any comments associated with the post
        db.execute('DELETE FROM comments WHERE post_id = ?', (post_id,))
        
        db.commit()
        return jsonify({'message': f'Post {post_id} deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        print(f"Error deleting post: {e}")
        return jsonify({'message': 'Failed to delete post'}), 500

# ------ Admin Routes ------

'''
Admin-only endpoint to get detailed user information.

Requires admin role to access. Returns detailed information about all users.

Returns:
    flask.Response: JSON response with detailed user information
'''
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users(current_user):
    db = get_db()
    cursor = db.execute('SELECT id, username, role, timestamp FROM users')
    
    # Convert rows to dictionaries with detailed information
    users = []
    for row in cursor.fetchall():
        user_dict = dict(id=row['id'], username=row['username'], 
                        role=row['role'], timestamp=row['timestamp'])
        
        # Get post count for each user
        post_cursor = db.execute('SELECT COUNT(*) as post_count FROM posts WHERE user_id = ?', (row['id'],))
        post_count = post_cursor.fetchone()['post_count']
        user_dict['post_count'] = post_count
        
        users.append(user_dict)
    
    return jsonify(users)

# Start the Flask application when run directly
if __name__ == '__main__':
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Get debug mode from environment variable (defaults to False)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Note: Port 5001 is used because port 5000 is often in use on macOS
    app.run(host='0.0.0.0', debug=debug_mode, port=port) 