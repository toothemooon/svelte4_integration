# Vercel-Azure Database Persistence Test

This folder contains files to fix the issue where comments added to the blog disappear after refreshing the Vercel-hosted frontend that connects to the Azure backend.

## Problem Diagnosis

After analyzing the codebase, we identified the issue:

1. The comment data is not persisting in the Azure backend because `init_db.py` recreates the database from scratch on each restart.
2. When the Azure Web App restarts, it runs `init_db.py` which drops and recreates all tables, removing any user-added comments.
3. The database file isn't stored in a persistent location on Azure.

## Solution Files

This folder contains modified files to maintain comment persistence:

- `init_db_persistent.py` - A modified version of init_db that only initializes the database if it doesn't exist
- `startup_persistent.sh` - A modified startup script that uses the persistent init_db approach
- `test_db_persistence.py` - A script to verify database persistence by adding a comment and checking if it exists
- `azure-persistent-workflow.yml` - A GitHub Actions workflow file for deployment with persistent database
- `deploy-persistent.sh` - A script to deploy the Azure backend using the Azure CLI with persistent database

## How to Test

1. Run the database persistence test locally:
```bash
python test_vercel_azure/test_db_persistence.py
```

2. Deploy the backend to Azure with the persistent approach:
```bash
bash test_vercel_azure/deploy-persistent.sh
```

3. After deployment, add a comment through the Vercel-hosted frontend, then refresh the page to verify the comment persists.

## How It Works

1. The modified `init_db_persistent.py` checks if the database exists before initializing it:
   - If the database doesn't exist, it creates the schema and adds sample data
   - If the database exists, it leaves it alone, preserving existing comments

2. The `startup_persistent.sh` script:
   - Uses the persistent init_db approach
   - Sets the DATABASE_DIR environment variable to a persistent location in Azure
   - Only initializes the database if it doesn't exist

3. These changes ensure that user comments are preserved between Azure backend restarts. 