from flask import Flask, g
import sqlite3
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True) 