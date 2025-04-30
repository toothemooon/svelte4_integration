from app import app, init_db, get_db

with app.app_context():
    # Initialize the database schema
    init_db()
    
    # Add some sample data
    db = get_db()
    db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user1', 'user1@example.com'))
    db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user2', 'user2@example.com'))
    db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user3', 'user3@example.com'))
    db.commit()
    
    print("Database initialized successfully with sample data.") 