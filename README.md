# Old Svelte & Flask Project

A beginner-friendly project that connects a Svelte frontend with a Flask backend using SQLite for data storage. This project demonstrates how to build a simple full-stack web application with a blog-style interface that supports post-specific comments and role-based access control.

## Project Overview

This project consists of two main parts:
1. **Frontend**: A Svelte application that runs in the browser
2. **Backend**: A Flask API server that connects to an SQLite database

The frontend makes API calls to the backend to fetch data, which is then displayed to the user.

## Key Features

- **Blog Interface**: Simple, responsive UI for browsing and reading posts
- **Comments System**: Each post has its own comment section
- **Authentication**: User login and token-based authentication
- **Role-Based Access Control**: Admin and regular user roles with different permissions
- **Post Management**: Admins can create and delete posts
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
old_svelte/
├── backend/                 # Flask backend application
│   ├── app.py               # Main Flask application
│   ├── schema.sql           # SQL schema for database (users and comments)
│   ├── init_db.py           # Script to initialize/reset the local database
│   ├── scripts/             # Utility scripts for administration
│   │   ├── list_users.py    # Script to list all users in the database
│   │   └── admin_scripts/   # Admin user management scripts (gitignored)
│   ├── requirements.txt     # Python dependencies
│   ├── database.db          # Local SQLite database file (Gitignored)
│   └── build/               # Build, deployment and test directories
│       ├── deploy/          # Deployment scripts and configurations
│       │   ├── deploy-to-azure.sh # Script to deploy backend to Azure
│       │   └── debug_azure.py   # Debug script for Azure DB issues
│       ├── tests/           # Backend tests (pytest)
│       └── pytest.ini       # Pytest configuration
│
├── frontend/                # Svelte frontend application
│   ├── public/              # Static assets and HTML template
│   ├── src/                 # Source code
│   │   ├── components/      # UI components
│   │   │   ├── Navbar.svelte
│   │   │   ├── Home.svelte
│   │   │   ├── Post.svelte
│   │   │   ├── CreatePost.svelte
│   │   │   ├── Comments.svelte
│   │   │   ├── Footer.svelte
│   │   │   └── About.svelte
│   │   ├── App.svelte       # Main application component with routing
│   │   ├── main.js          # Entry point
│   │   ├── authStore.js     # Authentication and user role management
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
**Warning:** This script drops existing tables. For production, database initialization is handled differently.

5. Create an admin user (optional, test_user1 is already an admin):
```bash
python scripts/admin_scripts/create_admin.py
# Or use the convenience script:
./scripts/admin_scripts/make_admin.sh myusername mypassword
```

6. Run the Flask application for local development:
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

## Role-Based Access Control

This application implements role-based access control with two main roles:

### User Roles

1. **Admin**:
   - Can create new posts
   - Can delete any post
   - Can edit any post
   - Can access admin-only endpoints

2. **Regular User**:
   - Can view posts
   - Can add comments
   - Can edit only their own posts (if they created any)

### How to Use Different Roles

By default, the following test users are created:
- Admin: `test_user1` with password `password1`
- User: `test_user2` with password `password2`

You can also create a custom admin user with:
```bash
cd backend
python scripts/admin_scripts/create_admin.py <username> <password>
# Or use the convenience script:
./scripts/admin_scripts/make_admin.sh <username> <password>
```

### Technical Implementation

The RBAC system is implemented through:
- JWT tokens with role information
- Admin-required decorator in Flask backend
- Role-based UI visibility in the frontend
- Permission checks for all operations

## Backend Testing

The `backend/build/tests/` directory contains automated tests for the Flask application using `pytest`.

To run these tests and generate coverage reports, please refer to the instructions in the `backend/build/tests/README.md` file.

### Running RBAC Tests

To specifically test role-based access control functionality:

```bash
cd backend
python build/tests/run_coverage.py --rbac
```

## Frontend Features

The frontend is a blog application with the following features:

### Home Page
- Displays a list of blog posts with titles, excerpts, and dates
- Each post card is clickable and navigates to the individual post view
- Accessible design with keyboard navigation support

### Post Management
- Admin users can create new posts via the "Create Post" link in navigation
- Admin users can delete posts from the post detail page
- Only logged in admin users see these UI controls

### Post Page
- Displays a single blog post with title, author, date, and content
- Dynamic routing with URL parameters: `/post/:id`
- Post-specific comments section that allows users to add and delete comments
- Admin delete button for post removal (visible only to admins)
- Loading states and error handling

### Authentication and Authorization
- Login form with username/password
- User role detection and UI adaptation
- Protected routes and access control
- Visual indication of current user role in navigation

### Comments System
- Each blog post has its own unique set of comments
- Users can add new comments to specific posts
- Users can delete comments with a confirmation dialog
- Comments display content and timestamp

### Navigation
- Responsive navigation bar with role-based links
- Active link highlighting
- Client-side routing with svelte-spa-router

## API Endpoints

The backend provides these API endpoints:

- **GET /api/health** - Health check endpoint to verify the backend is running
  - Returns: `{"status": "ok", "message": "Flask backend is running"}`

- **GET /api/users** - Retrieves the list of users from the database
  - Returns: Array of user objects with id, username, and timestamp

- **GET /api/posts** - Retrieves all blog posts
  - Returns: Array of post objects with id, title, content, excerpt, and timestamp

- **GET /api/posts/:id** - Retrieves a specific post by ID
  - Returns: Single post object

- **POST /api/posts** - Creates a new post (admin only)
  - Requires: JWT token with admin role
  - Request: JSON object with title and content fields
  - Returns: Created post object

- **DELETE /api/posts/:id** - Deletes a post by ID (admin only)
  - Requires: JWT token with admin role
  - Returns: Success message

- **PUT /api/posts/:id** - Updates a post (owner or admin only)
  - Requires: JWT token
  - Request: JSON object with title and content fields
  - Returns: Updated post object

- **GET /api/posts/:post_id/comments** - Retrieves all comments for a specific post
  - Returns: Array of comment objects

- **POST /api/posts/:post_id/comments** - Adds a new comment to a specific post
  - Request: JSON object with content field
  - Returns: Created comment object

- **POST /api/login** - Authenticates a user and returns a JWT
  - Request: JSON object with username and password fields
  - Returns: JWT token and user information including role

- **POST /api/register** - Registers a new user
  - Request: JSON object with username and password fields
  - Returns: Success message

- **GET /api/admin/users** - Admin-only endpoint that returns detailed user information
  - Requires: JWT token with admin role
  - Returns: Array of user objects with detailed information

## Frontend-Backend Connection

The project uses a flexible configuration system that allows the frontend to connect to different backend environments:

- **Development**: When running locally, the frontend connects to `http://localhost:5001`
- **Production**: When deployed to Vercel or accessed from a non-localhost domain, it connects to the Azure backend at `https://sarada-hbegajbsfxekdyex.canadacentral-01.azurewebsites.net`

This configuration is managed in `frontend/src/config.js` and automatically detects which environment is being used.

### Cross-Origin Resource Sharing (CORS)

The backend is configured with proper CORS headers to allow the frontend to make cross-origin requests for all HTTP methods (GET, POST, DELETE) regardless of where it's hosted.

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

- **scripts/admin_scripts/create_admin.py**: Script to create an admin user.

- **requirements.txt**: Lists the Python packages needed to run the application.

- **database.db**: The SQLite database file that stores the data.

- **build/deploy/deploy-to-azure.sh**: The primary script for deploying the backend to Azure App Service. It packages the application, handles dependencies, and configures Azure for persistent database storage.

- **build/deploy/debug_azure.py**: An optional utility script to help diagnose database persistence issues directly on the Azure App Service environment if needed.

## API Endpoints

The backend provides these API endpoints:

- **GET /** - Simple test endpoint that verifies database connection
  - Returns: Text message confirming database connection

- **GET /api/health** - Health check endpoint to verify the backend is running
  - Returns: `{"status": "ok", "message": "Flask backend is running"}`

- **GET /api/users** - Retrieves the list of users from the database
  - Returns: Array of user objects with id, username, and timestamp

- **GET /api/posts** - Retrieves all blog posts
  - Returns: Array of post objects with id, title, content, excerpt, and timestamp

- **GET /api/posts/:id** - Retrieves a specific post by ID
  - Returns: Single post object

- **POST /api/posts** - Creates a new post (admin only)
  - Requires: JWT token with admin role
  - Request: JSON object with title and content fields
  - Returns: Created post object

- **DELETE /api/posts/:id** - Deletes a post by ID (admin only)
  - Requires: JWT token with admin role
  - Returns: Success message

- **PUT /api/posts/:id** - Updates a post (owner or admin only)
  - Requires: JWT token
  - Request: JSON object with title and content fields
  - Returns: Updated post object

- **GET /api/posts/:post_id/comments** - Retrieves all comments for a specific post
  - Returns: Array of comment objects

- **POST /api/posts/:post_id/comments** - Adds a new comment to a specific post
  - Request: JSON object with content field
  - Returns: Created comment object

- **POST /api/login** - Authenticates a user and returns a JWT
  - Request: JSON object with username and password fields
  - Returns: JWT token and user information including role

- **POST /api/register** - Registers a new user
  - Request: JSON object with username and password fields
  - Returns: Success message

- **GET /api/admin/users** - Admin-only endpoint that returns detailed user information
  - Requires: JWT token with admin role
  - Returns: Array of user objects with detailed information

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

- If you see CORS errors, verify that Flask-CORS is installed and configured properly 
- For database issues, you can reset the database by deleting the `database.db` file within the `/home/site/wwwroot/data` directory on your Azure App Service (using Kudu tools or SSH) and redeploying. **Warning:** This will delete all existing comments.
- For Azure deployment issues, check the logs:
  ```bash
  az webapp log tail --resource-group YOUR_RESOURCE_GROUP --name YOUR_APP_NAME
  ```
- When running the frontend locally, ensure you're accessing it from the exact URL shown in the terminal (typically http://localhost:8080)
