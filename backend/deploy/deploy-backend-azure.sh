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
# Define the full path to the startup script in the deploy directory
STARTUP_SCRIPT_PATH="$SCRIPT_DIR/$STARTUP_SCRIPT_NAME"

# Default to not include database
INCLUDE_DATABASE=0

# Display help information
display_help() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help           Display this help message"
    echo "  -d, --include-db     Include the local database in the deployment"
    echo
}

# Parse command line arguments
while [ "$1" != "" ]; do
    case $1 in
        -h | --help )           display_help
                                exit 0
                                ;;
        -d | --include-db )     INCLUDE_DATABASE=1
                                ;;
        * )                     echo "Invalid option: $1"
                                display_help
                                exit 1
    esac
    shift
done

# --- Verify the necessary tools are available ---
# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed or not in your PATH."
    echo "Please install it by following instructions at: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if zip utility is installed
if ! command -v zip &> /dev/null; then
    echo "Error: zip utility is not installed or not in your PATH."
    echo "Please install it using your system's package manager."
    exit 1
fi

# --- Check Azure Login Status ---
echo "Checking Azure login status..."
# Get an account list and check if authenticated
AZURE_LOGIN_STATUS=$(az account list 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$AZURE_LOGIN_STATUS" ] || [ "$AZURE_LOGIN_STATUS" = "[]" ]; then
    echo "You are not logged in to Azure. Please login with:"
    echo "az login"
    exit 1
fi
echo "Azure login verified."

# Restarting the app before deployment can sometimes help
echo "Restarting Azure App Service before deployment..."
az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"
echo "Waiting 30 seconds for the app to fully restart before deploying..."
sleep 30

echo "Deploying package to Azure App Service: $APP_NAME in $RESOURCE_GROUP..."

# --- Create temporary directory for deployment artifacts ---
TEMP_DIR=$(mktemp -d /tmp/azure-deploy-XXXXXX)
echo "Created temporary directory: $TEMP_DIR"

# --- Copy necessary files to the temporary directory ---
echo "Copying files to temporary directory..."
# Core application files needed for deployment
cp -r "$BACKEND_DIR/app.py" "$BACKEND_DIR/init_db.py" "$BACKEND_DIR/schema.sql" "$BACKEND_DIR/requirements.txt" "$TEMP_DIR"

# Make sure scripts directories exist
mkdir -p "$TEMP_DIR/scripts/admin_scripts"
cp -r "$BACKEND_DIR/scripts/admin_scripts/"*.py "$TEMP_DIR/scripts/admin_scripts/"

# Copy the startup script to the temp directory
cp "$STARTUP_SCRIPT_PATH" "$TEMP_DIR"

# Create database directory if needed
if [ $INCLUDE_DATABASE -eq 1 ]; then
    echo "Including local database in deployment package..."
    
    # Check if database exists
    DATABASE_PATH="$BACKEND_DIR/database.db"
    if [ -f "$DATABASE_PATH" ]; then
        echo "Found local database at: $DATABASE_PATH"
        mkdir -p "$TEMP_DIR/data"
        cp "$DATABASE_PATH" "$TEMP_DIR/data/"
        echo "Database copied to deployment package data directory."
    else
        echo "Warning: Local database not found at $DATABASE_PATH. Will create new database on Azure."
    fi
fi

# --- Create the deployment package ---
echo "Creating deployment package..."
cd "$TEMP_DIR"
zip -r "$DEPLOY_ZIP_PATH" * -x "*.pyc" "__pycache__/*"

echo "Deployment package created at: $DEPLOY_ZIP_PATH"
echo "Package contents:"
unzip -l "$DEPLOY_ZIP_PATH"

# --- Deploy to Azure using az webapp deploy ---
echo "Uploading and deploying package to Azure..."
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path "$DEPLOY_ZIP_PATH" --type zip

if [ $? -ne 0 ]; then
    echo "Error: Deployment failed"
    exit 1
fi

echo "Setting startup command to run the startup script..."
az webapp config set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --startup-file "$STARTUP_SCRIPT_NAME"

# --- Clean Up ---
echo "Cleaning up temporary deployment artifacts..."
rm -rf "$TEMP_DIR"
echo "Temporary directory removed."

# --- Verify deployment ---
echo "Restarting webapp to apply changes..."
az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"

echo "Waiting 30 seconds for app to start..."
sleep 30

echo "Checking health of the deployed application..."
HEALTH_URL="https://$APP_NAME-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net/api/health"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "Deployment successful! The application is running."
    echo "Health check URL: $HEALTH_URL"
    echo "Returned status code: $HTTP_STATUS"
else
    echo "Warning: Health check failed with status code: $HTTP_STATUS"
    echo "The application may still be starting or there might be an issue."
    echo "Check the logs using: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
fi

echo "Deployment process completed." 