#!/bin/bash
# Deployment script for Flask backend to Azure App Service.
# Packages necessary files and uses 'az webapp deploy'.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
APP_NAME="sarada"                 # Azure Web App name
RESOURCE_GROUP="blog_quickstart"  # Azure Resource Group name
DEPLOY_ZIP_NAME="azure_deployment_package.zip"
STARTUP_SCRIPT_NAME="azure_startup.sh" # Must match the name of the startup script created

# Get the directory where this script is located
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# Assuming this script is in the backend directory
BACKEND_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(realpath "$BACKEND_DIR/..")"
DEPLOY_ZIP_PATH="$PROJECT_ROOT/$DEPLOY_ZIP_NAME" # Place zip in project root

echo "--- Starting Azure Deployment ---"
echo "Project Root: $PROJECT_ROOT"
echo "Backend Directory: $BACKEND_DIR"
echo "Deployment Package: $DEPLOY_ZIP_PATH"

# --- Prepare Deployment Package ---
echo "Creating deployment package..."

# Ensure the startup script is executable (it should be already, but double-check)
chmod +x "$BACKEND_DIR/$STARTUP_SCRIPT_NAME"

# Change to the backend directory to create the zip with relative paths
cd "$BACKEND_DIR"

# Create the zip file containing required application files
# -r: recursive for directories (like scripts/)
# -q: quiet mode
zip -r -q "$DEPLOY_ZIP_PATH" \
    app.py \
    init_db.py \
    schema.sql \
    requirements.txt \
    scripts/ \
    "$STARTUP_SCRIPT_NAME" \
    -x "*.pyc" "__pycache__/*" ".DS_Store"

echo "Deployment package created successfully at $DEPLOY_ZIP_PATH"

# Return to the original directory (optional, good practice)
cd "$PROJECT_ROOT"

# --- Azure Deployment ---
echo "Deploying package to Azure App Service: $APP_NAME in $RESOURCE_GROUP..."

# Use 'az webapp deploy' for zip deployment
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$DEPLOY_ZIP_PATH" --type zip --clean true

echo "Deployment command executed."

# --- Configure Startup Command ---
echo "Configuring Azure App Service startup command..."

# Set the startup file to the script included in our zip
# Azure runs this from /home/site/wwwroot, so the path is relative to that
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "$STARTUP_SCRIPT_NAME"

echo "Startup command configured."

# --- Restart Web App ---
echo "Restarting Azure App Service: $APP_NAME..."

az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"

echo "Restart command issued."

# --- Post-Deployment Check ---
echo "Waiting 30 seconds for the app to restart and initialize..."
sleep 30

AZURE_URL="https://$APP_NAME.azurewebsites.net"
echo "Checking application health at $AZURE_URL/api/health ..."

# Use curl to check the health endpoint. Exit code 0 means success (2xx or 3xx).
# --fail makes curl return non-zero on server errors (4xx, 5xx)
if curl --fail --silent --show-error --location "$AZURE_URL/api/health"; then
    echo
    echo "--- Deployment Successful! --- Application is responding."
else
    echo
    echo "--- Deployment Failed --- Application health check failed."
    echo "Please check the Azure logs for $APP_NAME:"
    echo "az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
    # Optionally, automatically stream logs here
    # az webapp log tail --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"
    exit 1 # Exit with error code if health check fails
fi

# --- Cleanup (Optional) ---
# echo "Cleaning up deployment package..."
# rm "$DEPLOY_ZIP_PATH"

echo "--- Azure Deployment Script Finished ---" 