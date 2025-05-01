from app import app, init_db, get_db

with app.app_context():
    # Initialize the database schema
    init_db()
    
    # Add some sample data
    db = get_db()
    # Insert sample users
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