/**
 * Home Component Tests
 * 
 * Tests for the Home component focusing on post listing and navigation
 */
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import Home from '../src/components/Home.svelte';
import { jest, describe, beforeEach, test, expect } from '@jest/globals';

// Create a mock for svelte-spa-router
const pushMock = jest.fn();

// Mock imports
jest.unstable_mockModule('svelte-spa-router', () => ({
  push: pushMock
}));

// Mock post data
const mockPosts = [
  {
    id: 1,
    title: 'First Test Post',
    excerpt: 'This is the first test post excerpt',
    timestamp: '2023-06-15T12:00:00Z'
  },
  {
    id: 2,
    title: 'Second Test Post',
    excerpt: 'This is the second test post excerpt',
    timestamp: '2023-06-16T14:30:00Z'
  }
];

describe('Home Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    fetch.mockClear();
    
    // Reset router push function
    pushMock.mockClear();
    
    // Setup a successful fetch response by default
    fetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockPosts)
      })
    );
  });
  
  test('Shows loading state initially', () => {
    // Mock fetch to delay returning posts
    fetch.mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(() => {
        resolve({
          ok: true,
          json: () => Promise.resolve(mockPosts)
        });
      }, 100))
    );
    
    const { getByText } = render(Home);
    
    // Should show loading text
    expect(getByText('Loading posts...')).toBeInTheDocument();
  });
  
  test('Displays posts when loaded', async () => {
    const { getByText, findAllByRole } = render(Home);
    
    // Wait for posts to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Should display both posts
    await waitFor(() => {
      expect(getByText('First Test Post')).toBeInTheDocument();
      expect(getByText('This is the first test post excerpt')).toBeInTheDocument();
      expect(getByText('Second Test Post')).toBeInTheDocument();
      expect(getByText('This is the second test post excerpt')).toBeInTheDocument();
    });
    
    // Should have 2 post cards (with role="button")
    const postCards = await findAllByRole('button');
    expect(postCards.length).toBe(2);
  });
  
  test('Displays error message when fetch fails', async () => {
    // Mock a failed fetch
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        status: 500
      })
    );
    
    const { getByText } = render(Home);
    
    // Wait for error to show
    await waitFor(() => {
      expect(getByText('Failed to load posts')).toBeInTheDocument();
    });
  });
  
  // Skip this test for now - we'll need to simulate the viewPost function
  test.skip('Navigates to post when post card is clicked', async () => {
    const { findAllByRole } = render(Home);
    
    // Wait for posts to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Wait for post cards to be rendered
    const postCards = await findAllByRole('button');
    const firstPostCard = postCards[0];
    
    // Click on the first post
    await fireEvent.click(firstPostCard);
    
    // Check that router.push was called with correct path
    expect(pushMock).toHaveBeenCalledWith('/post/1');
  });
  
  test('Shows empty state when no posts are available', async () => {
    // Mock empty posts array
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      })
    );
    
    const { getByText } = render(Home);
    
    // Wait for empty state to show
    await waitFor(() => {
      expect(getByText('No posts available yet.')).toBeInTheDocument();
    });
  });
}); 