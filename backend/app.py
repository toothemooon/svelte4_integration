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
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS, 
                               "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
                               "allow_headers": ["Content-Type", "Authorization"], 
                               "supports_credentials": True}})

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
    # Database connection check
    conn = get_db()
    
    # Check tables
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    
    # Collect table statistics
    table_stats = {}
    for table_name in tables:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            
            # Get columns for this table
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = [col['name'] for col in cursor.fetchall()]
            
            table_stats[table_name] = {
                'count': count,
                'columns': columns
            }
            
            # If it's the posts table, get a sample row
            if table_name == 'posts' and count > 0:
                cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = dict(cursor.fetchone())
                table_stats[table_name]['sample'] = {k: str(v) for k, v in sample.items()}
        except Exception as e:
            table_stats[table_name] = {'error': str(e)}
    
    # Check Flask app configuration and routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    
    # Collect debug information
    debug_info = {
        'database_path': DATABASE,
        'tables': tables,
        'table_stats': table_stats,
        'app_routes': routes,
        'environment': {
            'flask_env': os.environ.get('FLASK_ENV'),
            'database_dir': os.environ.get('DATABASE_DIR'),
            'flask_app': os.environ.get('FLASK_APP'),
            'flask_debug': os.environ.get('FLASK_DEBUG'),
            'working_directory': os.getcwd(),
            'python_path': sys.path
        }
    }
    
    return jsonify(debug_info)

'''
Get all posts from the database.

Returns:
    flask.Response: JSON response with a list of all posts
'''
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts from the database, including user data."""
    # Add debugging logs
    app.logger.debug("Entering /api/posts endpoint")
    
    try:
        # Get database connection
        conn = get_db()
        
        # Log database connection
        app.logger.debug(f"Database connection established: {conn}")
        
        # Join posts with users table to get the username
        try:
            # More clear query with explicit column selection
            query = """
            SELECT 
                posts.id, 
                posts.title, 
                posts.content, 
                posts.created, 
                users.username
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created DESC
            """
            app.logger.debug(f"Executing SQL query: {query}")
            
            # Execute the query
            posts = conn.execute(query).fetchall()
            
            # Log query results
            app.logger.debug(f"Query returned {len(posts)} posts")
            
        except Exception as sql_error:
            # Log SQL-specific errors
            app.logger.error(f"SQL error in /api/posts: {str(sql_error)}")
            
            # Fallback to simpler query without join if the first one fails
            app.logger.debug("Attempting fallback query without JOIN")
            
            # Simple query just getting posts
            posts = conn.execute(
                'SELECT id, title, content, created FROM posts ORDER BY created DESC'
            ).fetchall()
            
            app.logger.debug(f"Fallback query returned {len(posts)} posts")
        
        conn.close()
        
        # Convert the posts to a list of dictionaries
        post_list = []
        for post in posts:
            # Convert datetime to string for JSON serialization
            # and format it for display
            created_date = post['created']
            if isinstance(created_date, str):
                # If it's already a string, use it as is
                formatted_date = created_date
            else:
                # Format datetime object
                formatted_date = created_date.strftime('%B %d, %Y')
            
            # Create dictionary with post data
            post_dict = {
                'id': post['id'],
                'title': post['title'],
                'content': post['content'],
                'timestamp': post['created'],
                'formattedDate': formatted_date
            }
            
            # Add username if available (from JOIN query)
            if 'username' in post.keys():
                post_dict['username'] = post['username']
            else:
                post_dict['username'] = 'Unknown'  # Fallback
            
            post_list.append(post_dict)
        
        app.logger.debug(f"Returning {len(post_list)} formatted posts")
        return jsonify(post_list)
        
    except Exception as e:
        # Log any other errors
        app.logger.error(f"Error in /api/posts endpoint: {str(e)}")
        
        # Return an error response
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

This route allows users to edit their own posts.

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
    
    # Check if user is the owner
    if post['user_id'] != current_user['id']:
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

def delete_post(current_user, post_id):
    # Get database connection
    db = get_db()
    
    # First, check if the post exists
    cursor = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    
    # Check if user is the owner
    if post['user_id'] != current_user['id']:
        return jsonify({'message': 'Not authorized to delete this post'}), 403
    
    # Delete the post
    db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

# Start the Flask application when run directly
if __name__ == '__main__':
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Get debug mode from environment variable (defaults to False)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Note: Port 5001 is used because port 5000 is often in use on macOS
    app.run(host='0.0.0.0', debug=debug_mode, port=port) 