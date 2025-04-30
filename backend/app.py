from flask import Flask, g, jsonify
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store database in the project directory
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

@app.route('/')
def index():
    db = get_db()
    # Example query
    cursor = db.execute('SELECT 1')
    result = cursor.fetchone()
    return f"Database connection successful: {result[0]}"

@app.route('/api/users', methods=['GET'])
def get_users():
    db = get_db()
    cursor = db.execute('SELECT * FROM users')
    users = [dict(id=row[0], username=row[1], email=row[2]) for row in cursor.fetchall()]
    return jsonify(users)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Flask backend is running"})

if __name__ == '__main__':
    app.run(debug=True, port=5001) 