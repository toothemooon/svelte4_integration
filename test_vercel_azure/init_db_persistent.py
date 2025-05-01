from app import app, get_db
import os
import sqlite3

with app.app_context():
    # Get path to database
    db_path = app.config.get('DATABASE', 'database.db')
    
    # Check if the database already exists
    if not os.path.exists(db_path):
        print(f"Database does not exist at {db_path}, initializing...")
        # Initialize the database schema
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        
        # Add some sample data
        db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user1', 'user1@example.com'))
        db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user2', 'user2@example.com'))
        db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user3', 'user3@example.com'))
        
        # Insert sample comments for different posts
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (1, 'Feel free to leave your comments here!',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (1, 'I found this very helpful for getting started.',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (2, 'The component explanation was exactly what I needed.',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (3, 'Looking forward to more posts on routing.',))
        
        db.commit()
        print("Database initialized successfully with sample data.")
    else:
        print(f"Database already exists at {db_path}, skipping initialization.")
        # Just print a quick count of comments for verification
        db = get_db()
        cursor = db.execute('SELECT COUNT(*) FROM comments')
        count = cursor.fetchone()[0]
        print(f"Found {count} existing comments in the database.") 