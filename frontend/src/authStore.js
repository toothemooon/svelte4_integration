import { writable } from 'svelte/store';
import { push } from 'svelte-spa-router';
import { API_URL } from './config.js';

const TOKEN_KEY = 'jwt_token'; // Key for localStorage

// State: isLoggedIn (boolean), token (string), errorMsg (string), currentUserId (number)
export const isLoggedIn = writable(false);
export const token = writable(null);
export const errorMsg = writable(null); // To display auth errors
export const currentUserId = writable(null); // Store the current user's ID

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
        // Decode token to get user ID
        try {
            const payload = JSON.parse(atob(storedToken.split('.')[1]));
            currentUserId.set(payload.user_id);
        } catch (e) {
            console.error('Error decoding token:', e);
        }
        console.log('Auth initialized from stored token.');
    } else {
        console.log('No stored token found.');
    }
}

// Login function
// Update login function
export async function login(username, password) {
    clearError();
    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (!data.token) {
            throw new Error('No token received in response');
        }

        token.set(data.token);
        isLoggedIn.set(true);
        localStorage.setItem(TOKEN_KEY, data.token);
        push('/');
        
    } catch (err) {
        console.error('Login error:', err);
        errorMsg.set(err.message || 'Login failed. Please try again.');
        isLoggedIn.set(false);
        token.set(null);
        localStorage.removeItem(TOKEN_KEY);
    }
}

// Logout function
export function logout() {
    clearError();
    token.set(null);
    isLoggedIn.set(false);
    currentUserId.set(null);
    localStorage.removeItem(TOKEN_KEY);
    console.log('Logged out, token removed.');
    push('/');
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
        alert('Registration successful! Please log in.');
        push('/auth');

    } catch (err) {
        console.error('Registration error:', err);
        errorMsg.set(err.message);
    }
}

// Initialize auth state when the store is loaded
initializeAuth(); 