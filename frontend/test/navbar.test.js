/**
 * Navbar Component Tests
 * 
 * Tests for the Navbar component focusing on navigation and authentication state
 */
import { render, fireEvent } from '@testing-library/svelte';
import Navbar from '../src/components/Navbar.svelte';
import { isLoggedIn, userRole } from '../src/authStore';
import { jest, describe, beforeEach, test, expect } from '@jest/globals';

// Create a mock for svelte-spa-router - we need to do this before the import
const pushMock = jest.fn();

// Mock imports
jest.unstable_mockModule('svelte-spa-router', () => ({
  push: pushMock,
  link: () => {}
}));

// Import the mocked module
const { push } = await import('svelte-spa-router');

describe('Navbar Component', () => {
  beforeEach(() => {
    // Reset authentication state
    isLoggedIn.set(false);
    userRole.set(null);
    
    // Clear all mocks
    pushMock.mockClear();
  });
  
  test('Shows "Login" button when not logged in', () => {
    // Set logged out state
    isLoggedIn.set(false);
    userRole.set(null);
    
    // Render the component
    const { getByText, queryByText } = render(Navbar);
    
    // Should show login button
    expect(getByText('Login')).toBeInTheDocument();
    
    // Should not show logout or create post buttons
    expect(queryByText('Logout')).not.toBeInTheDocument();
    expect(queryByText('Create Post')).not.toBeInTheDocument();
  });
  
  test('Shows "Logout" button when logged in as regular user', () => {
    // Set logged in state as regular user
    isLoggedIn.set(true);
    userRole.set('user');
    
    // Render the component
    const { getByText, queryByText } = render(Navbar);
    
    // Should show logout button
    expect(getByText('Logout')).toBeInTheDocument();
    
    // Should NOT show create post button (regular user)
    expect(queryByText('Create Post')).not.toBeInTheDocument();
    
    // Should not show login button
    expect(queryByText('Login')).not.toBeInTheDocument();
  });
  
  test('Shows "Logout" and "Create Post" buttons when logged in as admin', () => {
    // Set logged in state as admin
    isLoggedIn.set(true);
    userRole.set('admin');
    
    // Render the component
    const { getByText, queryByText } = render(Navbar);
    
    // Should show logout and create post buttons
    expect(getByText('Logout')).toBeInTheDocument();
    expect(getByText('Create Post')).toBeInTheDocument();
    
    // Should not show login button
    expect(queryByText('Login')).not.toBeInTheDocument();
  });
  
  test('Highlights different links based on currentPath prop', async () => {
    // Render with home path first
    const { container } = render(Navbar, { props: { currentPath: '/' } });
    
    // Check that home link has active class (updated selector)
    let homeLink = container.querySelector('a.nav-link.active');
    expect(homeLink).toBeInTheDocument();
    expect(homeLink.textContent).toBe('Home');
    
    // Render again with about path
    const { container: aboutContainer } = render(Navbar, { props: { currentPath: '/about' } });
    
    // Check that about link has active class (updated selector)
    let aboutLink = aboutContainer.querySelector('a.nav-link.active');
    expect(aboutLink).toBeInTheDocument();
    expect(aboutLink.textContent).toBe('About');
  });
  
  test('Navigation links are in the right section of the navbar', () => {
    const { container } = render(Navbar);
    
    // Check that the navigation links are in the .nav-section
    const navSection = container.querySelector('.nav-section');
    expect(navSection).toBeInTheDocument();
    
    // Check that Home, About are in nav-section
    expect(navSection.querySelector('a[href="/"]')).toBeInTheDocument();
    expect(navSection.querySelector('a[href="/about"]')).toBeInTheDocument();
  });
  
  test('Auth buttons have proper styling classes', () => {
    // Test login button styling
    isLoggedIn.set(false);
    
    let { container } = render(Navbar);
    let loginButton = container.querySelector('.login-btn');
    expect(loginButton).toBeInTheDocument();
    expect(loginButton.textContent).toBe('Login');
    
    // Test logout button styling
    isLoggedIn.set(true);
    
    let { container: loggedInContainer } = render(Navbar);
    let logoutButton = loggedInContainer.querySelector('.logout-btn');
    expect(logoutButton).toBeInTheDocument();
    expect(logoutButton.textContent).toBe('Logout');
  });
}); 