#!/bin/bash
# Simplified deployment script for Azure

# Configuration
APP_NAME="sarada"
RESOURCE_GROUP="blog_quickstart"
SOURCE_DIR="./backend"
ZIP_FILE="./backend/deploy/package.zip"

echo "===== Simple Deployment to Azure Web App ====="
echo "App name: $APP_NAME"

# Verify Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    exit 1
fi

# Check login status
echo "Checking Azure login status..."
az account show &> /dev/null || az login

# Copy essential files to backend folder
echo "Preparing files for deployment..."
cp "$SOURCE_DIR/deploy/startup.sh" "$SOURCE_DIR/"
cp "$SOURCE_DIR/deploy/web.config" "$SOURCE_DIR/"
chmod +x "$SOURCE_DIR/startup.sh"

# Create deployment package
echo "Creating deployment package..."
rm -f "$ZIP_FILE" 2>/dev/null
mkdir -p backend/deploy

# Create the zip file
pushd "$SOURCE_DIR" > /dev/null
zip -r "../deploy/package.zip" . -x "deploy/*" "__pycache__/*" "*.pyc"
popd > /dev/null

# Remove temporary files
echo "Cleaning up..."
rm -f "$SOURCE_DIR/startup.sh"
rm -f "$SOURCE_DIR/web.config"

# Deploy to Azure
echo "Deploying to Azure Web App: $APP_NAME"
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$ZIP_FILE" --type zip

# Set the startup command explicitly
echo "Setting startup command..."
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "startup.sh"

echo "Deployment complete. Your app should be available at: https://$APP_NAME.azurewebsites.net"
echo "To see logs, run: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME" 