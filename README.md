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
├── frontend/                # Svelte frontend application
│   ├── public/              # Static assets and HTML template
│   ├── src/                 # Source code
│   │   ├── components/      # UI components
│   │   │   ├── Navbar.svelte  # Navigation component
│   │   │   ├── Home.svelte    # Blog listing page
│   │   │   ├── Post.svelte    # Individual blog post view with comments
│   │   │   ├── Comments.svelte # Post-specific comments component
│   │   │   ├── Footer.svelte  # Simple footer with credits
│   │   │   └── About.svelte   # About page
│   │   ├── App.svelte       # Main application component with routing
│   │   └── main.js          # Entry point
│   ├── package.json         # NPM dependencies and scripts
│   └── rollup.config.js     # Rollup bundler configuration
│
├── backend/                 # Flask backend application
│   ├── app.py               # Main Flask application
│   ├── schema.sql           # SQL schema for database (users and comments)
│   ├── init_db.py           # Script to initialize the database
│   ├── requirements.txt     # Python dependencies
│   └── database.db          # SQLite database file
│
└── README.md                # This documentation file
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

### Backend (Flask)

- **app.py**: The main Flask application that defines API routes, database connection, and handles requests.

- **schema.sql**: Defines the database tables and structure (users and comments).

- **init_db.py**: Script that initializes the database with the schema and adds sample users and comments.

- **requirements.txt**: Lists the Python packages needed to run the application.

- **database.db**: The SQLite database file that stores the data.

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

## Testing Backend-Frontend Connection

To test if your frontend can communicate with the backend, use the browser's developer console (F12) and run:

```javascript
fetch('http://localhost:5001/api/health')
  .then(response => response.json())
  .then(data => {
    console.log('Connection successful!', data);
  })
  .catch(error => {
    console.error('Connection failed:', error);
  });
```

To test the comments API specifically:

```javascript
fetch('http://localhost:5001/api/posts/1/comments')
  .then(response => response.json())
  .then(data => {
    console.log('Comments for post #1:', data);
  })
  .catch(error => {
    console.error('Failed to fetch comments:', error);
  });
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
- For database issues, you can reset the database by running `init_db.py` 