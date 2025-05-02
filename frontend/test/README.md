# Frontend Testing

This directory contains automated tests for the Svelte frontend application using Jest and Svelte Testing Library.

## Overview

The testing setup includes:

-   **Jest:** The core JavaScript testing framework.
-   **Svelte Testing Library:** Utilities for testing Svelte components in a user-centric way.
-   **Configuration:** Jest configuration is located within `package.json`.
-   **Setup File (`setup.js`):** Used for global Jest setup (e.g., extending `expect` with `@testing-library/jest-dom`).
-   **Mocks (`__mocks__/`):** Contains manual mocks for dependencies like `config.js` and `svelte-spa-router`.

## Running Tests

All test commands should be run from the **`frontend/`** directory.

### Running All Tests

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies if you haven't already
# npm install

# Run all *.test.js tests
npm test
```

### Running Tests in Watch Mode

Jest's watch mode can be run directly if needed (requires Jest CLI installed globally or via npx):

```bash
# Run Jest in watch mode
npx jest --watch
```
*(Note: A specific `test:watch` script is not currently defined in `package.json`)*

### Running Specific Tests

You can run specific test files or tests matching a pattern by passing arguments to Jest via `npm test --`:

```bash
# Run only navbar tests
npm test -- navbar.test.js

# Run tests with "login" in their description
npm test -- -t "login"

# Run only role-based access control tests
npm test -- -t "role"
```

## Test Files and Structure

-   `*.test.js`: Test files for different components or features:
    -   `home.test.js` - Tests for the Home component
    -   `navbar.test.js` - Tests for the Navbar component, including role-based UI elements
    -   `comments.test.js` - Tests for the Comments component
    -   `auth.test.js` - Tests for authentication and role handling
    -   `post.test.js` - Tests for post display and admin actions (delete functionality)
-   `setup.js`: Jest setup file (imports `@testing-library/jest-dom`).
-   `__mocks__/`: Contains mocks for external modules used during testing.

## Role-Based Access Control Testing

The test suite includes specific tests for role-based access control:

### Testing User Roles

- `auth.test.js` tests JWT token decoding and role extraction
- `auth.test.js` tests the userRole store updates correctly based on login/logout

### Testing Admin-Only UI Elements

- `navbar.test.js` tests that the "Create Post" link is only shown to admin users
- `post.test.js` tests that the "Delete Post" button is only visible to admin users

### Testing Permission-Based Actions

- `post.test.js` tests the post deletion functionality for admin users
- Tests verify correct UI handling based on user roles

### Creating Test Admin Users

For manual testing with admin users, you can create them using the backend admin scripts:

```bash
# From project root
cd backend
python scripts/admin_scripts/create_admin.py testadmin securepassword

# Or use the convenience script
./scripts/admin_scripts/make_admin.sh testadmin securepassword
```

## Adding New Tests

1.  Create a new file named `ComponentName.test.js`.
2.  Import necessary functions from `@testing-library/svelte` and other utilities.
3.  Import the Svelte component to test.
4.  Write test cases using `describe` and `it` (or `test`).
5.  Render the component using `render()`.
6.  Interact with the component using `screen` queries and `fireEvent`.
7.  Use `expect` assertions (using matchers from `@testing-library/jest-dom` provided via `setup.js`) to verify results.

```javascript
// Example: src/components/MyComponent.test.js
import { render, screen, fireEvent } from '@testing-library/svelte';
import MyComponent from '../src/components/MyComponent.svelte'; // Adjust path as needed

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(MyComponent, { props: { name: 'Test' } });
    const heading = screen.getByRole('heading');
    expect(heading).toHaveTextContent('Hello Test!'); // Uses jest-dom matcher
  });

  // Add more tests for interaction, etc.
});
``` 