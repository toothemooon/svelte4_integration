/**
 * Post Component Tests
 * 
 * Tests for the Post component focusing on displaying a single blog post
 * and testing role-based functionality like admin-only post deletion
 */
import { render, waitFor, fireEvent } from '@testing-library/svelte';
import Post from '../src/components/Post.svelte';
import { isLoggedIn, token, userRole } from '../src/authStore';
import { get } from 'svelte/store';
import { jest, describe, beforeEach, test, expect } from '@jest/globals';

// Import the mocked push function (location is automatically mocked in __mocks__)
import { push } from 'svelte-spa-router';

// Mock post data
const mockPost = {
  id: 1,
  title: 'Test Post Title',
  content: 'This is the content of the test post.',
  author: 'Test Author',
  timestamp: '2023-06-15T12:00:00Z'
};

describe('Post Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    fetch.mockClear();
    
    // Reset auth stores
    isLoggedIn.set(false);
    token.set(null);
    userRole.set(null);
    
    // Setup a successful fetch response by default
    fetch.mockImplementation((url) => {
      if (url.includes('/api/posts/1')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPost)
        });
      }
      
      if (url.includes('/api/posts/1/comments')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      
      return Promise.resolve({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ message: 'Not found' })
      });
    });
  });
  
  test('Shows loading state initially', async () => {
    // Mock fetch to delay returning post
    fetch.mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(() => {
        resolve({
          ok: true,
          json: () => Promise.resolve(mockPost)
        });
      }, 50))
    );
    
    const { getByText } = render(Post);
    
    // Should show loading text
    expect(getByText('Loading post...')).toBeInTheDocument();
  });
  
  test('Displays post when loaded', async () => {
    const { getByText } = render(Post);
    
    // Wait for post to load
    await waitFor(() => {
      expect(getByText('Test Post Title')).toBeInTheDocument();
    });
    
    // Should display post details
    expect(getByText('This is the content of the test post.')).toBeInTheDocument();
    
    // Should show back button
    expect(getByText('← Back to posts')).toBeInTheDocument();
  });
  
  test('Delete button is not visible when not logged in', async () => {
    const { queryByText, getByText } = render(Post);
    
    // Wait for post to load
    await waitFor(() => {
      expect(getByText('Test Post Title')).toBeInTheDocument();
    });
    
    // Delete button should not be visible
    expect(queryByText('Delete Post')).not.toBeInTheDocument();
  });
  
  test('Delete button is not visible for regular users', async () => {
    // Set up as logged in regular user
    isLoggedIn.set(true);
    token.set('mock-token');
    userRole.set('user');
    
    const { queryByText, getByText } = render(Post);
    
    // Wait for post to load
    await waitFor(() => {
      expect(getByText('Test Post Title')).toBeInTheDocument();
    });
    
    // Delete button should not be visible
    expect(queryByText('Delete Post')).not.toBeInTheDocument();
  });
  
  test('Delete button is visible for admin users', async () => {
    // Set up as logged in admin
    isLoggedIn.set(true);
    token.set('mock-admin-token');
    userRole.set('admin');
    
    const { getByText } = render(Post);
    
    // Wait for post to load
    await waitFor(() => {
      expect(getByText('Test Post Title')).toBeInTheDocument();
    });
    
    // Delete button should be visible
    expect(getByText('Delete Post')).toBeInTheDocument();
  });
  
  test('Clicking delete button calls API with confirmation', async () => {
    // Set up as logged in admin
    isLoggedIn.set(true);
    token.set('mock-admin-token');
    userRole.set('admin');
    
    // Mock confirmation dialog
    global.confirm = jest.fn(() => true);
    
    // Mock delete endpoint
    fetch.mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ message: 'Post deleted successfully' })
    }));
    
    const { getByText } = render(Post);
    
    // Wait for post to load
    await waitFor(() => {
      expect(getByText('Test Post Title')).toBeInTheDocument();
    });
    
    // Click the delete button
    fireEvent.click(getByText('Delete Post'));
    
    // Confirm dialog should be shown
    expect(global.confirm).toHaveBeenCalled();
    
    // Fetch should be called with DELETE method
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/posts\/1/),
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-admin-token'
          })
        })
      );
    });
  });
  
  test('User can cancel post deletion', async () => {
    // Set up as logged in admin
    isLoggedIn.set(true);
    token.set('mock-admin-token');
    userRole.set('admin');
    
    // Mock confirmation dialog to return false (cancel)
    global.confirm = jest.fn(() => false);
    
    const { getByText } = render(Post);
    
    // Wait for post to load
    await waitFor(() => {
      expect(getByText('Test Post Title')).toBeInTheDocument();
    });
    
    // Click the delete button
    fireEvent.click(getByText('Delete Post'));
    
    // Confirm dialog should be shown
    expect(global.confirm).toHaveBeenCalled();
    
    // No additional fetch calls should be made (only the initial post load)
    expect(fetch).toHaveBeenCalledTimes(2); // One for post, one for comments
  });
}); 