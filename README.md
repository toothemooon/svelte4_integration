# Old Svelte & Flask Project

A beginner-friendly project that connects a Svelte frontend with a Flask backend using SQLite for data storage. This project demonstrates how to build a simple full-stack web application with a blog-style interface that supports post-specific comments.

## Project Overview

This project consists of two main parts:
1. **Frontend**: A Svelte application that runs in the browser
2. **Backend**: A Flask API server that connects to an SQLite database

The frontend makes API calls to the backend to fetch data, which is then displayed to the user.

## Project Structure

```
old_svelte/
├── backend/                 # Flask backend application
│   ├── app.py               # Main Flask application
│   ├── schema.sql           # SQL schema for database (users and comments)
│   ├── init_db.py           # Script to initialize/reset the local database
│   ├── requirements.txt     # Python dependencies
│   ├── database.db          # Local SQLite database file (Gitignored)
│   ├── deploy/              # Deployment scripts and configurations
│   │   ├── deploy-to-azure.sh # Script to deploy backend to Azure (persistent DB)
│   │   └── debug_azure.py   # Optional script to debug Azure DB issues
│   └── tests/               # Backend tests (pytest)
│       ├── README.md        # Instructions for running tests
│       ├── test_api.py
│       ├── conftest.py
│       ├── run_coverage.py  # Script to run tests with coverage
│       └── ...              # Other test utilities
│
├── frontend/                # Svelte frontend application
│   ├── public/              # Static assets and HTML template
│   ├── src/                 # Source code
│   │   ├── components/      # UI components
│   │   │   ├── Navbar.svelte
│   │   │   ├── Home.svelte
│   │   │   ├── Post.svelte
│   │   │   ├── Comments.svelte
│   │   │   ├── Footer.svelte
│   │   │   └── About.svelte
│   │   ├── App.svelte       # Main application component with routing
│   │   ├── main.js          # Entry point
│   │   └── config.js        # Backend API URL configuration
│   ├── package.json         # NPM dependencies and scripts
│   └── rollup.config.js     # Rollup bundler configuration
│
├── .github/                 # (Removed - Workflows deleted)
├── .venv/                   # Python virtual environment (Gitignored)
├── .gitattributes
└── README.md                # This documentation file
```

## Setup and Installation

### Backend (Flask)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv ../.venv  # Create venv in project root
source ../.venv/bin/activate # On Linux/macOS
# or ..\\.venv\\Scripts\\activate on Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the *local* database with sample data (only needed once or for reset):
```bash
python init_db.py
```
**Warning:** This script drops existing tables. For production, database initialization is handled differently (see Azure deployment).

5. Run the Flask application for local development:
```bash
# Optional: Set FLASK_DEBUG=true for development features
export FLASK_DEBUG=true # Linux/macOS
# set FLASK_DEBUG=true # Windows CMD
# $env:FLASK_DEBUG = "true" # Windows PowerShell

python app.py
```

The backend will be available at http://localhost:5001.

### Frontend (Svelte)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:8080

## Deploying Backend to Azure App Service

The backend includes a deployment script (`backend/deploy/deploy-to-azure.sh`) to easily deploy to Microsoft Azure App Service. This script includes fixes to ensure database persistence.

### Prerequisites
- Azure account with an active subscription
- Azure CLI installed (`az` command available)
- An existing Azure App Service (Python runtime, Linux recommended)

### Deployment Steps

1. Make sure you're logged in to Azure CLI:
```bash
az login
```

2. Run the deployment script from the project root:
```bash
bash ./backend/deploy/deploy-to-azure.sh
```

The script handles packaging, dependencies, persistent storage setup, and deployment.

3. Your backend API will be available at:
```
https://YOUR-APP-NAME.azurewebsites.net
```
*(Replace `YOUR-APP-NAME` with your actual Azure App Service name)*

## Backend Testing

The `backend/tests/` directory contains tests for the Flask application using `pytest`.

To run the tests:
1. Ensure you have activated your virtual environment and installed dependencies (`pip install -r backend/requirements.txt`), including `pytest` and `pytest-cov`.
2. Navigate to the `backend` directory (`cd backend`).
3. Run `python -m pytest`.

To run tests with coverage:
1. Navigate to the `backend` directory (`cd backend`).
2. Run `python -m pytest --cov=. tests/`.
3. To generate an HTML report (in `backend/htmlcov/`), run `python -m coverage html` after running the tests with `--cov`.

For detailed information on the test structure, fixtures, and utilities, please see the `README.md` file inside the `backend/tests/` directory.

## Frontend Features

The frontend is a blog application with the following features:

### Home Page
- Displays a list of blog posts with titles, excerpts, and dates
- Each post card is clickable and navigates to the individual post view
- Accessible design with keyboard navigation support

### Post Page
- Displays a single blog post with title, author, date, and content
- Dynamic routing with URL parameters: `/post/:id`
- Post-specific comments section that allows users to add and delete comments
- Loading states and error handling

### Comments System
- Each blog post has its own unique set of comments
- Users can add new comments to specific posts
- Users can delete comments with a confirmation dialog
- Comments display content and timestamp

### Navigation
- Responsive navigation bar with links to Home and About pages
- Active link highlighting
- Client-side routing with svelte-spa-router

### Footer
- Simple, minimalist footer with credits

## Frontend-Backend Connection

The project uses a flexible configuration system that allows the frontend to connect to different backend environments:

- **Development**: When running locally, the frontend connects to `http://localhost:5001`
- **Production**: When deployed to Vercel or accessed from a non-localhost domain, it connects to the Azure backend at `https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net`

This configuration is managed in `frontend/src/config.js` and automatically detects which environment is being used.

### Cross-Origin Resource Sharing (CORS)

The backend is configured with proper CORS headers to allow the frontend to make cross-origin requests for all HTTP methods (GET, POST, DELETE) regardless of where it's hosted.

### Fallback Behavior

The application includes fallback mechanisms to handle cases where the backend might be unavailable:

- If comment retrieval fails, the UI will show an appropriate error message
- When adding or deleting comments, if the backend is unavailable, the frontend will simulate the operations locally
- The home page shows hardcoded sample posts if the backend post API is not available

These fallbacks provide a more resilient user experience when working with a distributed architecture.

## Understanding the Files

### Frontend (Svelte)

- **src/main.js**: The entry point of the application. It creates and mounts the main Svelte component.

- **src/App.svelte**: The main component that sets up routing and includes the Navbar and Footer components.

- **src/components/Navbar.svelte**: Navigation component with client-side routing.

- **src/components/Home.svelte**: Blog listing page that displays a list of posts.

- **src/components/Post.svelte**: Individual post view that displays a single blog post based on the ID and includes the Comments component.

- **src/components/Comments.svelte**: Component for displaying, adding, and deleting comments for a specific post.

- **src/components/Footer.svelte**: Simple footer with credits.

- **src/components/About.svelte**: Simple about page with information.

- **public/index.html**: The HTML template that loads the bundled JavaScript and CSS.

- **package.json**: Contains the project metadata, dependencies, and npm scripts.

- **rollup.config.js**: Configuration for the Rollup bundler that builds the project.

- **src/config.js**: Manages backend API URL configuration based on the current environment.

### Backend (Flask)

- **app.py**: The main Flask application that defines API routes, database connection, and handles requests.

- **schema.sql**: Defines the database tables and structure (users and comments).

- **init_db.py**: Script that initializes the database with the schema and adds sample users and comments.

- **requirements.txt**: Lists the Python packages needed to run the application.

- **database.db**: The SQLite database file that stores the data.

- **deploy/deploy-to-azure.sh**: The primary script for deploying the backend to Azure App Service. It packages the application, handles dependencies, and configures Azure for persistent database storage.

- **deploy/debug_azure.py**: An optional utility script to help diagnose database persistence issues directly on the Azure App Service environment if needed.

## API Endpoints

The backend provides these API endpoints:

- **GET /** - Simple test endpoint that verifies database connection
  - Returns: Text message confirming database connection

- **GET /api/health** - Health check endpoint to verify the backend is running
  - Returns: `{"status": "ok", "message": "Flask backend is running"}`

- **GET /api/users** - Retrieves the list of users from the database
  - Returns: Array of user objects with id, username, and email

- **GET /api/posts/:post_id/comments** - Retrieves all comments for a specific post
  - Returns: Array of comment objects with id, post_id, content, and timestamp

- **POST /api/posts/:post_id/comments** - Adds a new comment to a specific post
  - Request: JSON object with content field
  - Returns: Created comment object

- **DELETE /api/comments/:comment_id** - Deletes a specific comment
  - Returns: Success message with the deleted comment ID

## Testing Backend-Frontend Connection (Manual)

To manually test if your frontend can communicate with the backend from your browser's developer console (F12):

Test the health check:
```javascript
fetch('http://localhost:5001/api/health') // Replace with your Azure URL if testing deployed version
  .then(response => response.json())
  .then(data => console.log('Connection successful!', data))
  .catch(error => console.error('Connection failed:', error));
```

Test the comments API (for post ID 1):
```javascript
fetch('http://localhost:5001/api/posts/1/comments') // Replace URL if needed
  .then(response => response.json())
  .then(data => console.log('Comments for post #1:', data))
  .catch(error => console.error('Failed to fetch comments:', error));
```

## Future Enhancements

To fully implement the blog functionality, consider adding these API endpoints:

- **GET /api/posts** - Retrieve all blog posts
- **GET /api/posts/:id** - Retrieve a specific blog post by ID
- **POST /api/posts** - Create a new blog post
- **User authentication system** - Allow users to register, login, and have personalized experiences

## How the Connection Works

1. The frontend (Svelte) makes HTTP requests to the backend (Flask) using the `fetch` API
2. The backend receives these requests, interacts with the SQLite database, and returns JSON data
3. The frontend displays this data in the browser

The connection between frontend and backend is enabled by CORS (Cross-Origin Resource Sharing), which allows the frontend running on port 8080 to access the backend running on port 5001.

## Troubleshooting

- If port 5000 is in use (common on macOS), the app uses port 5001 instead
- Check browser console (F12) for any network errors and API responses
- Make sure both servers (frontend and backend) are running simultaneously
- If you see CORS errors, verify that Flask-CORS is installed and configured properly 
- For database issues, you can reset the database by deleting the `database.db` file within the `/home/site/wwwroot/data` directory on your Azure App Service (using Kudu tools or SSH) and redeploying. **Warning:** This will delete all existing comments.
- For Azure deployment issues, check the logs:
  ```bash
  az webapp log tail --resource-group YOUR_RESOURCE_GROUP --name YOUR_APP_NAME
  ```
- If the frontend displays a blank page, check your browser console for JavaScript errors
- When running the frontend locally, ensure you're accessing it from the exact URL shown in the terminal (typically http://localhost:8080)
- Remember that you must run terminal commands from the correct directory:
  - For frontend commands: `cd frontend && npm run dev`
  - For backend commands: `cd backend && python app.py`