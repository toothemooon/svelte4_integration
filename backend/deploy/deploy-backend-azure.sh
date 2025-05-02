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

# Get the directory where this script is located (backend/deploy)
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# Get the backend directory (one level up from script dir)
BACKEND_DIR="$(realpath "$SCRIPT_DIR/..")"
# Get the project root (one level up from backend dir)
PROJECT_ROOT="$(realpath "$BACKEND_DIR/..")"
# Define the full path for the zip file in the project root
DEPLOY_ZIP_PATH="$PROJECT_ROOT/$DEPLOY_ZIP_NAME"
# Define the full path to the startup script in its new location
STARTUP_SCRIPT_PATH_FULL="$SCRIPT_DIR/$STARTUP_SCRIPT_NAME"
# Define the path of the startup script relative to the backend dir (for zipping)
STARTUP_SCRIPT_RELATIVE_PATH="deploy/$STARTUP_SCRIPT_NAME"
# Construct Azure URL (ensure this matches your Azure app URL format)
AZURE_INSTANCE_ID="hbegajbsfxekdyex" # Extracted from previous logs/config
AZURE_REGION="canadacentral-01" # Extracted from previous logs/config
AZURE_URL="https://$APP_NAME-$AZURE_INSTANCE_ID.$AZURE_REGION.azurewebsites.net"

echo "--- Starting Azure Deployment ---"
echo "Project Root: $PROJECT_ROOT"
echo "Backend Directory: $BACKEND_DIR"
echo "Script Directory: $SCRIPT_DIR"
echo "Deployment Package: $DEPLOY_ZIP_PATH"
echo "Startup Script Full Path: $STARTUP_SCRIPT_PATH_FULL"
echo "Startup Script Relative Path: $STARTUP_SCRIPT_RELATIVE_PATH"
echo "Target Azure URL: $AZURE_URL"

# --- Prepare Deployment Package ---
echo "Creating deployment package..."

# Ensure the startup script is executable
chmod +x "$STARTUP_SCRIPT_PATH_FULL"

# Change to the backend directory to create the zip with correct relative paths
cd "$BACKEND_DIR"

# Remove previous zip if it exists
if [ -f "$DEPLOY_ZIP_PATH" ]; then
    echo "Removing previous deployment package..."
    rm "$DEPLOY_ZIP_PATH"
fi

# Create the zip file containing required application files
# Add files relative to BACKEND_DIR
zip -r -q "$DEPLOY_ZIP_PATH" \
    app.py \
    init_db.py \
    schema.sql \
    requirements.txt \
    scripts/ \
    "$STARTUP_SCRIPT_RELATIVE_PATH" \
    -x "*.pyc" "__pycache__/*" ".DS_Store"

echo "Deployment package created successfully at $DEPLOY_ZIP_PATH"

# Return to the script directory (where deploy-backend-azure.sh is)
cd "$SCRIPT_DIR"

# --- Azure Deployment ---
echo "Verifying Azure login..."
az account show > /dev/null || (echo "ERROR: Not logged in to Azure. Please run 'az login' first." && exit 1)
echo "Azure login verified."

# Restarting the app before deployment can sometimes help
echo "Restarting Azure App Service before deployment..."
az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"
echo "Waiting 15 seconds for the app to begin restarting..."
sleep 15

echo "Deploying package to Azure App Service: $APP_NAME in $RESOURCE_GROUP..."

# Use 'az webapp deploy' for zip deployment
# Added --debug for more verbose output if issues occur
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$DEPLOY_ZIP_PATH" --type zip --clean true

echo "Deployment command executed. Azure is processing the package."

# --- Configure Startup Command ---
echo "Configuring Azure App Service startup command..."

# Set the startup file to the path *inside the deployed package*
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "$STARTUP_SCRIPT_RELATIVE_PATH"

echo "Startup command configured."
echo "Waiting 10 seconds before restarting the app..."
sleep 10

# --- Restart Web App ---
echo "Restarting Azure App Service: $APP_NAME to apply changes..."

az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"

echo "Restart command issued."

# --- Post-Deployment Check ---
HEALTH_CHECK_URL="$AZURE_URL/api/health"
MAX_RETRIES=5
RETRY_DELAY=20 # seconds

echo "Waiting up to $(($MAX_RETRIES * $RETRY_DELAY)) seconds for the app to become healthy..."

for ((i=1; i<=$MAX_RETRIES; i++)); do
    echo "Attempt $i/$MAX_RETRIES: Checking application health at $HEALTH_CHECK_URL ..."
    # Use curl: --fail -> fail on 4xx/5xx, -s -> silent, -S -> show error, -L -> follow redirects
    if curl --fail -sSL "$HEALTH_CHECK_URL"; then
        echo
        echo "--- Deployment Successful! --- Application is responding at $HEALTH_CHECK_URL."
        HEALTHY=true
        break
    else
        echo "Health check failed. Waiting $RETRY_DELAY seconds before retrying..."
        sleep $RETRY_DELAY
    fi
done

if [ "$HEALTHY" != true ]; then
    echo
    echo "--- Deployment May Have Failed --- Application health check failed after $MAX_RETRIES attempts."
    echo "Please check the Azure logs for $APP_NAME:"
    echo "az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
    echo "Streaming logs for the next 60 seconds (press Ctrl+C to stop earlier):"
    # Timeout might not be available everywhere, but attempt it
    timeout 60 az webapp log tail --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" || az webapp log tail --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"
    exit 1
fi

# --- Cleanup (Optional) ---
# echo "Cleaning up deployment package..."
# rm "$DEPLOY_ZIP_PATH"

echo "--- Azure Deployment Script Finished Successfully ---" 