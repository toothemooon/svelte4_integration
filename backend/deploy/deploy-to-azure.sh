#!/bin/bash
# Deployment script for Flask backend to Azure App Service.
# Ensures database persistence using Azure's persistent storage.

# --- Configuration ---
APP_NAME="sarada" # Replace with your Azure Web App name if different
RESOURCE_GROUP="blog_quickstart" # Replace with your Azure Resource Group name

# Paths (relative to project root where script is run)
DEPLOY_DIR="$(pwd)/backend/deploy"
TEMP_DIR="$DEPLOY_DIR/temp_deploy" # Temporary folder for packaging
ZIP_FILE="$DEPLOY_DIR/package.zip" # Deployment package file

# --- Script Start ---
echo "===== Azure Deployment for $APP_NAME ====="

# 1. Prerequisites Check
echo "---> Checking prerequisites..."
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI ('az') command not found. Please install it."
    exit 1
fi
if ! command -v rsync &> /dev/null; then
    echo "Error: 'rsync' command not found. Please install it."
    exit 1
fi
if ! command -v zip &> /dev/null; then
    echo "Error: 'zip' command not found. Please install it."
    exit 1
fi
az account show &> /dev/null || az login

# 2. Prepare Deployment Package
echo "---> Preparing deployment package in $TEMP_DIR ..."
mkdir -p "$TEMP_DIR"
rm -rf "$TEMP_DIR/*" # Clean temp directory

# Copy backend application files (excluding the deploy subdirectory)
echo "Copying application files..."
rsync -av --progress backend/ "$TEMP_DIR/" --exclude deploy

# Copy the Azure debugging script (optional, but helpful)
if [ -f "$DEPLOY_DIR/debug_azure.py" ]; then
    cp "$DEPLOY_DIR/debug_azure.py" "$TEMP_DIR/"
fi

# Create requirements.txt with pinned versions for stable deployment
echo "Creating requirements.txt..."
cat > "$TEMP_DIR/requirements.txt" << 'EOF'
Flask==2.0.1
flask-cors==3.0.10
Werkzeug==2.0.1
gunicorn==20.1.0
EOF

# Create the startup script that Azure will run
echo "Creating startup.sh..."
cat > "$TEMP_DIR/startup.sh" << 'EOF_STARTUP'
#!/bin/bash
# Startup script executed by Azure App Service

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Azure Startup Script Begin ---"
echo "Timestamp: $(date)"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Define the persistent storage directory for the database
PERSIST_DIR="/home/site/wwwroot/data"
mkdir -p "$PERSIST_DIR"
echo "Persistent data directory: $PERSIST_DIR"

# Set environment variable for the Flask app to find the database
export DATABASE_DIR="$PERSIST_DIR"

# Install Python dependencies
echo "Installing dependencies from requirements.txt..."
pip install --no-cache-dir -r requirements.txt

# Dynamically patch app.py to use the persistent database path
# This avoids needing different code for local vs Azure.
echo "Patching app.py database path..."
sed -i "s|DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))|DATABASE_DIR = os.environ.get('DATABASE_DIR', '$PERSIST_DIR')|g" app.py

# Dynamically create init_db.py that only runs if DB doesn't exist
DB_FILE="$PERSIST_DIR/database.db"
if [ ! -f "$DB_FILE" ]; then
    echo "Database not found ($DB_FILE), initializing..."
    cat > init_db.py << 'EOF_INITDB'
from app import app, get_db
import os, sqlite3
print("--- Running Database Initialization --- ")
with app.app_context():
    db_path = os.path.join(os.environ.get('DATABASE_DIR'), 'database.db')
    if not os.path.exists(db_path):
        print(f"Creating schema at {db_path}...")
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        # Add sample data (optional)
        db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user1', 'user1@example.com'))
        db.execute('INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)', ('user2', 'user2@example.com'))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (1, 'Default comment 1!',))
        db.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)', (1, 'Default comment 2!',))
        db.commit()
        print("Database schema created and sample data added.")
    else:
        print(f"Database already exists at {db_path}, skipping schema creation.")
print("--- Database Initialization Complete --- ")
EOF_INITDB
    # Execute the dynamically created init script
    python init_db.py
else
    echo "Database already exists ($DB_FILE), skipping initialization."
fi

# Display contents of persistent directory for logs
echo "Contents of $PERSIST_DIR:"
ls -la "$PERSIST_DIR"

# Start the Gunicorn server
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app

echo "--- Azure Startup Script End ---"
EOF_STARTUP' # End of startup script heredoc

# Make the startup script executable within the package
chmod +x "$TEMP_DIR/startup.sh"

# Create web.config needed for Python apps on Azure Windows App Service (even if using Linux)
# It mainly tells IIS how to hand off requests via HttpPlatformHandler.
echo "Creating web.config..."
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

# 3. Create Zip Package
echo "---> Creating deployment package: $ZIP_FILE ..."
rm -f "$ZIP_FILE" # Remove old package if exists
cd "$TEMP_DIR" # Go into temp dir to zip contents correctly
zip -r "$ZIP_FILE" . -x "*.pyc" "__pycache__/*" ".DS_Store"
cd - > /dev/null # Go back to original directory

# Verify zip file was created
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: Zip package creation failed!"
    exit 1
fi
echo "Zip package created successfully."

# 4. Clean up temporary directory
echo "---> Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# 5. Deploy to Azure
echo "---> Deploying $ZIP_FILE to Azure Web App: $APP_NAME ..."
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$ZIP_FILE" --type zip --clean true --verbose

# Check deployment status
if [ $? -ne 0 ]; then
    echo "Error: Azure deployment failed. Check logs above."
    exit 1
fi

# 6. Configure Azure App Service
# Set the startup command explicitly to ensure our script runs
echo "---> Configuring Azure startup command..."
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "startup.sh"

# 7. Completion Message
echo "---> Deployment to Azure complete!"
echo "Your app should be available shortly at: https://$APP_NAME.azurewebsites.net"
echo "To monitor logs, run: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo "(Allow 1-2 minutes for the app to fully start after deployment before testing)"

# --- Script End --- 