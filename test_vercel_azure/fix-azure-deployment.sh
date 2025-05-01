#!/bin/bash
# Fixed deployment script for Azure with proper dependencies

# Configuration
APP_NAME="sarada"
RESOURCE_GROUP="blog_quickstart"
ZIP_FILE="$(pwd)/test_vercel_azure/package.zip"

echo "===== Fixed Azure Deployment with Persistent Database ====="
echo "App name: $APP_NAME"

# Verify Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    exit 1
fi

# Check login status
echo "Checking Azure login status..."
az account show &> /dev/null || az login

# Prepare deployment folder
echo "Preparing deployment package..."
TEMP_DIR="$(pwd)/test_vercel_azure/temp_deploy"
mkdir -p "$TEMP_DIR"

# Copy backend files
cp -r backend/* "$TEMP_DIR/"

# Copy test files
cp test_vercel_azure/debug_azure.py "$TEMP_DIR/"

# Create requirements.txt with exact versions
cat > "$TEMP_DIR/requirements.txt" << 'EOF'
Flask==2.0.1
flask-cors==3.0.10
Werkzeug==2.0.1
gunicorn==20.1.0
EOF

# Create a simpler, more robust startup script
cat > "$TEMP_DIR/startup.sh" << 'EOF'
#!/bin/bash
# Set -e to exit on error
set -e

echo "Starting Azure deployment startup script"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Create persistent data directory
PERSIST_DIR="/home/site/wwwroot/data"
mkdir -p "$PERSIST_DIR"

# Install dependencies first
echo "Installing dependencies from requirements.txt"
pip install -r requirements.txt

# Make sure flask-cors is specifically installed
echo "Ensuring flask-cors is installed"
pip install flask-cors==3.0.10

# Export database directory 
export DATABASE_DIR="$PERSIST_DIR"
echo "Database directory set to: $DATABASE_DIR"

# Modify app.py to use the persistent path
echo "Patching app.py to use persistent database location"
sed -i "s|DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))|DATABASE_DIR = os.environ.get('DATABASE_DIR', '/home/site/wwwroot/data')|g" app.py

# Check for existing database
if [ ! -f "$PERSIST_DIR/database.db" ]; then
    echo "No database found, initializing at $PERSIST_DIR/database.db"
    # Copy original init_db but modify it to preserve data
    cat > init_db.py << 'EOFDB'
from app import app, get_db
import os
import sqlite3

with app.app_context():
    # Use persistent directory
    db_path = os.path.join(os.environ.get('DATABASE_DIR', '/home/site/wwwroot/data'), 'database.db')
    
    # Only initialize if doesn't exist
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
EOFDB
    # Run modified init script
    python init_db.py
else
    echo "Database already exists at $PERSIST_DIR/database.db"
fi

# Show all files in persistent directory
echo "Current files in $PERSIST_DIR:"
ls -la "$PERSIST_DIR"

# Start the app with gunicorn
echo "Starting gunicorn server on port 8000"
gunicorn --bind=0.0.0.0:8000 app:app
EOF

# Make the startup script executable
chmod +x "$TEMP_DIR/startup.sh"

# Create web.config for Azure
cat > "$TEMP_DIR/web.config" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="%HOME%\site\wwwroot\startup.sh" 
                  arguments="" 
                  stdoutLogEnabled="true" 
                  stdoutLogFile="%HOME%\LogFiles\python.log" />
  </system.webServer>
  <system.web>
    <customErrors mode="Off" />
  </system.web>
</configuration>
EOF

# Create the zip file
echo "Creating deployment package at $ZIP_FILE"
rm -f "$ZIP_FILE" 2>/dev/null
cd "$TEMP_DIR"
zip -r "$ZIP_FILE" .
cd - > /dev/null

# Verify zip file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: Zip file was not created successfully at $ZIP_FILE"
    exit 1
fi

# Clean up temp files
rm -rf "$TEMP_DIR"

# Deploy to Azure
echo "Deploying to Azure Web App: $APP_NAME"
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$ZIP_FILE" --type zip

# Set the startup command explicitly
echo "Setting startup command..."
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "startup.sh"

echo "Deployment complete. Your app should be available at: https://$APP_NAME.azurewebsites.net"
echo "To see logs, run: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo "WAIT AT LEAST 1 MINUTE before testing comments to allow site to fully start up" 