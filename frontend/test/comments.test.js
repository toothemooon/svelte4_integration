/**
 * Comments Component Tests
 * 
 * Tests for the Comments component focusing on listing, adding, and deleting comments
 */
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import Comments from '../src/components/Comments.svelte';
import { jest, describe, beforeEach, test, expect } from '@jest/globals';

// Mock comment data
const mockComments = [
  {
    id: 1,
    post_id: 1,
    content: 'This is the first test comment',
    timestamp: '2023-06-15T12:00:00Z'
  },
  {
    id: 2,
    post_id: 1,
    content: 'This is the second test comment',
    timestamp: '2023-06-16T14:30:00Z'
  }
];

describe('Comments Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    fetch.mockClear();
    
    // Return already resolved promises for component immediate rendering
    let mockResponseFn = () => ({
      ok: true,
      json: () => Promise.resolve(mockComments)
    });
    
    // Mock fetch implementation (immediately resolved)
    fetch.mockImplementation(() => Promise.resolve(mockResponseFn()));
    
    // Reset window.confirm mock
    window.confirm = jest.fn(() => true);
    
    // Reset window.alert mock
    window.alert = jest.fn();
  });
  
  test('Shows loading state initially', async () => {
    // Use slower fetch for this test
    fetch.mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(() => {
        resolve({
          ok: true,
          json: () => Promise.resolve(mockComments)
        });
      }, 100))
    );
    
    const { getByText } = render(Comments, { props: { postId: 1 } });
    
    // Should show loading text
    expect(getByText('Loading comments...')).toBeInTheDocument();
  });
  
  test('Displays comments when loaded', async () => {
    const { getByText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for comments to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Wait for UI to update
    await waitFor(() => {
      expect(getByText('This is the first test comment')).toBeInTheDocument();
      expect(getByText('This is the second test comment')).toBeInTheDocument();
    });
  });
  
  test('Displays error message when fetch fails', async () => {
    // Mock a failed fetch
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ message: 'Server error' })
      })
    );
    
    const { getByText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for error to show
    await waitFor(() => {
      expect(getByText(/Error loading comments:/)).toBeInTheDocument();
    });
  });
  
  test('Shows empty state when no comments are available', async () => {
    // Mock empty comments array
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      })
    );
    
    const { getByText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for empty state to show
    await waitFor(() => {
      expect(getByText('No comments yet. Be the first to add one!')).toBeInTheDocument();
    });
  });
  
  test('Adds a new comment when form is submitted', async () => {
    // Mock successful post response
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockComments)
      })
    ).mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          id: 3,
          post_id: 1,
          content: 'New test comment',
          timestamp: '2023-06-17T10:00:00Z'
        })
      })
    );
    
    const { getByText, getByPlaceholderText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for comments to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Type in the comment input
    const commentInput = getByPlaceholderText('Leave a comment...');
    await fireEvent.input(commentInput, { target: { value: 'New test comment' } });
    
    // Submit the form
    const submitButton = getByText('Add Comment');
    await fireEvent.click(submitButton);
    
    // Check that POST request was made
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(fetch.mock.calls[1][0]).toContain('/api/posts/1/comments');
    expect(fetch.mock.calls[1][1].method).toBe('POST');
    
    // Should display the new comment
    await waitFor(() => {
      expect(getByText('New test comment')).toBeInTheDocument();
    });
    
    // Input should be cleared
    expect(commentInput.value).toBe('');
  });
  
  test('Deletes a comment when delete button is clicked', async () => {
    // Mock successful delete response
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockComments)
      })
    ).mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 1 })
      })
    );
    
    const { getByText, queryByText, getAllByLabelText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for comments to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Wait for delete buttons to be available
    await waitFor(() => {
      expect(getAllByLabelText('Delete comment').length).toBe(2);
    });
    
    // Find all delete buttons and click the first one
    const deleteButtons = getAllByLabelText('Delete comment');
    await fireEvent.click(deleteButtons[0]);
    
    // Check that confirm was called
    expect(window.confirm).toHaveBeenCalled();
    
    // Check that DELETE request was made
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(fetch.mock.calls[1][0]).toContain('/api/comments/1');
    expect(fetch.mock.calls[1][1].method).toBe('DELETE');
    
    // First comment should be removed
    await waitFor(() => {
      expect(queryByText('This is the first test comment')).not.toBeInTheDocument();
    });
    
    // Second comment should still be there
    expect(getByText('This is the second test comment')).toBeInTheDocument();
  });
  
  test('Does not delete comment when confirmation is canceled', async () => {
    // Set confirm to return false (cancel)
    window.confirm = jest.fn(() => false);
    
    const { getByText, getAllByLabelText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for comments to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Wait for delete buttons to be available
    await waitFor(() => {
      expect(getAllByLabelText('Delete comment').length).toBe(2);
    });
    
    // Find all delete buttons and click the first one
    const deleteButtons = getAllByLabelText('Delete comment');
    await fireEvent.click(deleteButtons[0]);
    
    // Check that confirm was called
    expect(window.confirm).toHaveBeenCalled();
    
    // Check that DELETE request was NOT made (fetch should still be called only once for initial load)
    expect(fetch).toHaveBeenCalledTimes(1);
    
    // Both comments should still be there
    expect(getByText('This is the first test comment')).toBeInTheDocument();
    expect(getByText('This is the second test comment')).toBeInTheDocument();
  });
  
  test('Handles error when adding a comment fails', async () => {
    // Mock failed post response
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockComments)
      })
    ).mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ message: 'Server error' })
      })
    );
    
    const { getByText, getByPlaceholderText } = render(Comments, { props: { postId: 1 } });
    
    // Wait for comments to load
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
    });
    
    // Type in the comment input
    const commentInput = getByPlaceholderText('Leave a comment...');
    await fireEvent.input(commentInput, { target: { value: 'New test comment' } });
    
    // Submit the form
    const submitButton = getByText('Add Comment');
    await fireEvent.click(submitButton);
    
    // Check that POST request was made
    expect(fetch).toHaveBeenCalledTimes(2);
    
    // Should show an alert with the error
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalled();
    });
  });
}); 