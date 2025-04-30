# Old Svelte & Flask Project

A beginner-friendly project that connects a Svelte frontend with a Flask backend using SQLite for data storage. This project demonstrates how to build a simple full-stack web application.

## Project Overview

This project consists of two main parts:
1. **Frontend**: A Svelte application that runs in the browser
2. **Backend**: A Flask API server that connects to an SQLite database

The frontend makes API calls to the backend to fetch data, which is then displayed to the user.

## Project Structure

```
old_svelte/
├── frontend/              # Svelte frontend application
│   ├── public/            # Static assets and HTML template
│   ├── src/               # Source code
│   │   ├── App.svelte     # Main application component
│   │   └── main.js        # Entry point
│   ├── package.json       # NPM dependencies and scripts
│   └── rollup.config.js   # Rollup bundler configuration
│
├── backend/               # Flask backend application
│   ├── app.py             # Main Flask application
│   ├── schema.sql         # SQL schema for database
│   ├── init_db.py         # Script to initialize the database
│   ├── requirements.txt   # Python dependencies
│   └── database.db        # SQLite database file
│
└── README.md              # This documentation file
```

## Setup and Installation

### Backend (Flask)

1. Navigate to the backend directory:
```
cd backend
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Initialize the database with sample data:
```
python init_db.py
```

4. Run the Flask application:
```
python app.py
```

The backend will be available at http://localhost:5001 (Note: We use port 5001 because port 5000 is often used by macOS AirPlay Receiver)

### Frontend (Svelte)

1. Navigate to the frontend directory:
```
cd frontend
```

2. Install dependencies:
```
npm install
```

3. Run the development server:
```
npm run dev
```

The frontend will be available at http://localhost:8080

## Understanding the Files

### Frontend (Svelte)

- **src/main.js**: The entry point of the application. It creates and mounts the main Svelte component.
  ```javascript
  import App from './App.svelte';
  
  const app = new App({
    target: document.body
  });
  
  export default app;
  ```

- **src/App.svelte**: The main component that contains the user interface and logic for fetching data from the backend.
  ```javascript
  // Contains HTML template, JavaScript logic to fetch data from APIs, 
  // and CSS styles for the component
  ```

- **public/index.html**: The HTML template that loads the bundled JavaScript and CSS.

- **package.json**: Contains the project metadata, dependencies, and npm scripts.

- **rollup.config.js**: Configuration for the Rollup bundler that builds the project.

### Backend (Flask)

- **app.py**: The main Flask application that defines API routes, database connection, and handles requests.
  ```python
  # Key parts:
  # - Database connection setup
  # - API route definitions
  # - Flask app configuration with CORS
  ```

- **schema.sql**: Defines the database tables and structure.
  ```sql
  -- Creates users table with id, username, and email fields
  ```

- **init_db.py**: Script that initializes the database with the schema and adds sample users.
  ```python
  # Runs the schema SQL and inserts sample data
  ```

- **requirements.txt**: Lists the Python packages needed to run the application:
  ```
  flask==2.3.3
  flask-cors==4.0.0
  ```

- **database.db**: The SQLite database file that stores the data.

## API Endpoints

The backend provides these API endpoints:

- **GET /** - Simple test endpoint that verifies database connection
  - Returns: Text message confirming database connection

- **GET /api/health** - Health check endpoint to verify the backend is running
  - Returns: `{"status": "ok", "message": "Flask backend is running"}`

- **GET /api/users** - Retrieves the list of users from the database
  - Returns: Array of user objects with id, username, and email

## How the Connection Works

1. The frontend (Svelte) makes HTTP requests to the backend (Flask) using the `fetch` API
2. The backend receives these requests, interacts with the SQLite database, and returns JSON data
3. The frontend displays this data in the browser

The connection between frontend and backend is enabled by CORS (Cross-Origin Resource Sharing), which allows the frontend running on port 8080 to access the backend running on port 5001.

## Troubleshooting

- If port 5000 is in use (common on macOS), the app uses port 5001 instead
- Check browser console (F12) for any network errors
- Make sure both servers (frontend and backend) are running
- If you see CORS errors, verify that Flask-CORS is installed and configured properly 