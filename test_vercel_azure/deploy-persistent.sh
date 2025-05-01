#!/bin/bash
# Simplified deployment script for Azure with persistent database

# Configuration
APP_NAME="sarada"
RESOURCE_GROUP="blog_quickstart"
# Make sure parent directories exist for zip file
mkdir -p test_vercel_azure
ZIP_FILE="$(pwd)/test_vercel_azure/package.zip"

echo "===== Deploying to Azure Web App with Persistent Database ====="
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
# Create temp directory with -p to ensure it exists
mkdir -p "$TEMP_DIR"

# Copy backend files
cp -r backend/* "$TEMP_DIR/"

# Copy our persistent database tools
cp test_vercel_azure/init_db_persistent.py "$TEMP_DIR/init_db.py"
cp test_vercel_azure/startup_persistent.sh "$TEMP_DIR/startup.sh"
chmod +x "$TEMP_DIR/startup.sh"

# Create an appropriate requirements.txt with version pinning
cat > "$TEMP_DIR/requirements.txt" << 'EOF'
flask==2.0.1
flask_cors==3.0.10
gunicorn==20.1.0
Werkzeug==2.0.1
EOF

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
echo "Creating zip file at $ZIP_FILE"
rm -f "$ZIP_FILE" 2>/dev/null
cd "$TEMP_DIR"
zip -r "$ZIP_FILE" .
cd - > /dev/null

# Verify zip file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: Zip file was not created successfully at $ZIP_FILE"
    exit 1
fi

# Remove temporary files
rm -rf "$TEMP_DIR"

# Deploy to Azure
echo "Deploying to Azure Web App: $APP_NAME"
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$ZIP_FILE" --type zip

# Set the startup command explicitly
echo "Setting startup command..."
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "startup.sh"

echo "Deployment complete. Your app should be available at: https://$APP_NAME.azurewebsites.net"
echo "To see logs, run: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME" 