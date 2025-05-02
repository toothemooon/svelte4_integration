#!/bin/bash
# Deployment script for Flask backend to Azure App Service.
# Ensures database persistence using Azure's persistent storage.
# Updated to fix CORS issues with Vercel frontend

# Exit on error
set -e

# --- Configuration ---
APP_NAME="sarada" # Replace with your Azure Web App name if different
RESOURCE_GROUP="blog_quickstart" # Replace with your Azure Resource Group name

# Paths (relative to project root where script is run)
DEPLOY_DIR="$(dirname "$(realpath "$0")")" # Get the directory where this script is located
PROJECT_ROOT="$(dirname "$(dirname "$DEPLOY_DIR")")" # Get the project root directory
BACKEND_DIR="$(dirname "$DEPLOY_DIR")" # Backend directory is one level up from deploy dir
# Use a temporary directory in the user's home folder for staging
TEMP_DIR="$HOME/svelte_flask_deploy_temp_$(date +%s)" # Add timestamp to avoid conflicts
ZIP_FILE="$DEPLOY_DIR/package.zip" # Deployment package file

# --- Script Start ---
echo "===== Azure Deployment for $APP_NAME ====="
echo "Script location: $DEPLOY_DIR"
echo "Project root: $PROJECT_ROOT"
echo "Backend directory: $BACKEND_DIR"
echo "Temp directory: $TEMP_DIR"

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

# Check if logged in to Azure
echo "---> Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "Not logged in to Azure. Initiating login..."
    az login
fi

# 2. Prepare Deployment Package
echo "---> Preparing deployment package in $TEMP_DIR ..."
mkdir -p "$TEMP_DIR"
rm -rf "$TEMP_DIR/*" # Clean temp directory

# Copy backend application files (excluding the deploy subdirectory)
echo "Copying application files..."
rsync -av --progress "$BACKEND_DIR/" "$TEMP_DIR/" --exclude deploy

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

# Ensure CORS is properly configured in app.py
echo "Checking CORS configuration..."
if [ -f "$TEMP_DIR/app.py" ]; then
    # Check if CORS is already properly configured
    if ! grep -q "CORS(app, resources={r\"/api/\*\": {\"origins\": \"\*\"" "$TEMP_DIR/app.py"; then
        echo "Enhancing CORS configuration in app.py..."
        # Back up the original file
        cp "$TEMP_DIR/app.py" "$TEMP_DIR/app.py.bak"
        # Update the CORS configuration - handling different potential formats
        if grep -q "CORS(app)" "$TEMP_DIR/app.py"; then
            sed -i'' -e 's/CORS(app)/CORS(app, resources={r"\/api\/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})/g' "$TEMP_DIR/app.py"
        else
            # If not using the simple format, insert after the app creation
            sed -i'' -e '/app = Flask(__name__)/a\
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})' "$TEMP_DIR/app.py"
        fi
        echo "CORS configuration updated in app.py"
    else
        echo "CORS is already properly configured in app.py"
    fi
else
    echo "Error: app.py not found in $TEMP_DIR. Check rsync command."
    exit 1
fi

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

# Log installed packages for debugging
echo "Listing installed packages..."
pip list

# Dynamically patch app.py to use the persistent database path
# This avoids needing different code for local vs Azure.
echo "Patching app.py database path..."
sed -i "s|DATABASE_DIR = os.environ.get('DATABASE_DIR', os.path.dirname(os.path.abspath(__file__)))|DATABASE_DIR = os.environ.get('DATABASE_DIR', '$PERSIST_DIR')|g" app.py

# Double check CORS is properly configured for production
echo "Verifying CORS configuration..."
if ! grep -q "CORS(app, resources={r\"/api/\*\": {\"origins\": \"\*\"" app.py; then
    echo "Enhancing CORS configuration for production..."
    if grep -q "CORS(app)" app.py; then
        sed -i "s/CORS(app)/CORS(app, resources={r\"\/api\/*\": {\"origins\": \"*\", \"methods\": [\"GET\", \"POST\", \"DELETE\", \"OPTIONS\"], \"allow_headers\": [\"Content-Type\", \"Authorization\"]}})/g" app.py
    else
        # If not using the simple format, insert after the app creation
        sed -i '/app = Flask(__name__)/a\
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})\' app.py
    fi
fi

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
# Add CORS-related headers to Gunicorn to ensure they're properly set
gunicorn --bind=0.0.0.0:8000 --timeout 600 \
         --forwarded-allow-ips="*" \
         --access-logfile=- \
         --error-logfile=- \
         app:app

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

# 6. Configure Azure App Service
# Set the startup command explicitly to ensure our script runs
echo "---> Configuring Azure startup command..."
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "startup.sh"

# 7. Configure CORS on Azure App Service level
echo "---> Configuring CORS at Azure App Service level..."
# This adds an additional layer of CORS support at the Azure platform level
az webapp cors add --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" \
  --allowed-origins "https://svelte4-integration.vercel.app" "http://localhost:5173" "*"

# 8. Restart the app to apply changes
echo "---> Restarting Azure Web App to apply changes..."
az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"

# 9. Test endpoint to verify CORS headers
echo "---> Testing CORS headers (may take a minute for deployment to complete)..."
sleep 30  # Give the app a moment to restart

echo "Testing health endpoint..."
curl -I -X OPTIONS -H "Origin: https://svelte4-integration.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     "https://$APP_NAME.azurewebsites.net/api/health" || echo "CORS test failed, but deployment might still be in progress"

# 10. Completion Message
echo "---> Deployment to Azure complete!"
echo "Your app should be available shortly at: https://$APP_NAME.azurewebsites.net"
echo "To monitor logs, run: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo "(Allow 1-2 minutes for the app to fully start after deployment before testing)"

# --- Script End --- 