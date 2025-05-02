import { writable } from 'svelte/store';
import { push } from 'svelte-spa-router';
import { API_URL } from './config.js';

const TOKEN_KEY = 'jwt_token'; // Key for localStorage

// State: isLoggedIn (boolean), token (string), errorMsg (string)
export const isLoggedIn = writable(false);
export const token = writable(null);
export const errorMsg = writable(null); // To display auth errors
export const userRole = writable(null); // Add store for user role

// Helper function to decode JWT token
function decodeToken(token) {
    try {
        // JWT tokens are base64 encoded in three parts: header.payload.signature
        const base64Payload = token.split('.')[1];
        // Decode base64 (replace URL-safe chars and pad if needed)
        const base64 = base64Payload.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        const decoded = JSON.parse(jsonPayload);
        console.log('Decoded token payload:', decoded); // Add debugging
        return decoded;
    } catch (error) {
        console.error('Error decoding token:', error);
        return null;
    }
}

// Helper function to clear errors
export function clearError() {
    errorMsg.set(null);
}

// Function to check token on app load
export function initializeAuth() {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    if (storedToken) {
        // Set token and logged in state
        token.set(storedToken);
        isLoggedIn.set(true);
        
        // Decode token and extract user role
        const decoded = decodeToken(storedToken);
        if (decoded && decoded.role) {
            console.log('Setting user role from stored token:', decoded.role); // Add debugging
            userRole.set(decoded.role);
        } else {
            console.warn('No role found in stored token'); // Add debugging
        }
        
        console.log('Auth initialized from stored token.');
    } else {
        console.log('No stored token found.');
    }
}

// Login function
export async function login(username, password) {
    clearError();
    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || `Login failed (Status: ${response.status})`);
        }

        if (data.token) {
            console.log('Received token:', data.token); // Add debugging
            token.set(data.token);
            isLoggedIn.set(true);
            localStorage.setItem(TOKEN_KEY, data.token); // Store token
            
            // Set user role directly from the response if available
            if (data.user && data.user.role) {
                console.log('Setting user role directly from response:', data.user.role);
                userRole.set(data.user.role);
            } else {
                // Fall back to decoding the token
                const decoded = decodeToken(data.token);
                if (decoded && decoded.role) {
                    console.log('Setting user role from decoded token:', decoded.role);
                    userRole.set(decoded.role);
                } else {
                    console.warn('No role found in token or response');
                }
            }
            
            console.log('Login successful, token stored.');
            push('/'); // Redirect to home page after successful login
        } else {
            throw new Error('Login failed: No token received.');
        }

    } catch (err) {
        console.error('Login error:', err);
        errorMsg.set(err.message);
        isLoggedIn.set(false); // Ensure logged out state on error
        token.set(null);
        localStorage.removeItem(TOKEN_KEY);
    }
}

// Logout function
export function logout() {
    clearError();
    token.set(null);
    isLoggedIn.set(false);
    userRole.set(null); // Clear user role
    localStorage.removeItem(TOKEN_KEY); // Remove token from storage
    console.log('Logged out, token removed.');
    push('/'); // Redirect to home
}

// Register function
export async function register(username, password) {
    clearError();
    try {
        const response = await fetch(`${API_URL}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || `Registration failed (Status: ${response.status})`);
        }

        console.log('Registration successful:', data.message);
        // Optional: Automatically log in after registration
        // await login(username, password); 
        // OR just show a success message and let user log in manually
        alert('Registration successful! Please log in.'); // Simple alert for now
        push('/auth'); // Stay on auth page (or redirect to login part if separate)


    } catch (err) {
        console.error('Registration error:', err);
        errorMsg.set(err.message);
    }
}

// Initialize auth state when the store is loaded
initializeAuth(); 