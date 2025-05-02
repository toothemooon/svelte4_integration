# Backend Scripts

This folder contains utility scripts for maintaining and managing the blog application.

## Available Scripts

### Admin Scripts (`admin_scripts/`)

Contains tools for managing admin users. See the [Admin Scripts README](admin_scripts/README.md) for details.

### User Listing (`list_users.py`)

Lists all users in the database with their roles and creation timestamps.

Usage:
```bash
python backend/scripts/list_users.py
```

## Adding New Scripts

When adding new scripts to this folder, make sure to:

1. Use relative imports for accessing the backend modules
2. Update any database paths to use `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` to get the backend dir
3. Document the script's purpose and usage in this README

## Security Note

Some scripts in this folder may contain sensitive operations. Make sure to:

1. Never commit credentials or secrets to the repository
2. Add folders containing sensitive scripts to .gitignore (e.g., admin_scripts/) 