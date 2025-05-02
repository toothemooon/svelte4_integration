<script>
    import { onMount } from 'svelte';
    import { API_URL } from '../config.js';
    
    // Post ID is a required prop
    export let postId;
    
    // State variables
    let comments = [];
    let newComment = '';
    let loading = true;
    let error = null;
    
    // Function to fetch comments for a specific post
    async function fetchComments() {
        loading = true;
        error = null; // Reset error on fetch
        try {
            const response = await fetch(`${API_URL}/api/posts/${postId}/comments`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            comments = await response.json();
        } catch (err) {
            console.error('Error fetching comments:', err);
            error = err.message;
            // Removed fallback logic - just show the error
        } finally {
            loading = false;
        }
    }
    
    // Function to add a new comment
    async function addComment() {
        if (!newComment.trim()) return;
        
        try {
            const response = await fetch(`${API_URL}/api/posts/${postId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ content: newComment })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Comment added:', result);
            
            // Add the new comment to the top of the list
            comments = [result, ...comments];
            
            // Clear the input field
            newComment = '';
            
        } catch (err) {
            console.error('Error adding comment:', err);
            // Removed fallback logic
            // Simply alert the user or update an error state
            alert('Failed to add comment. Please check connection and try again. ' + err.message);
        }
    }
    
    // Function to delete a comment
    async function deleteComment(id) {
        if (!confirm('Are you sure you want to delete this comment?')) return;
        
        try {
            const response = await fetch(`${API_URL}/api/comments/${id}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            // Remove the comment from the list
            comments = comments.filter(comment => comment.id !== id);
            console.log(`Comment ${id} deleted successfully`);
            
        } catch (err) {
            console.error('Error deleting comment:', err);
            // Removed fallback logic
            // Simply alert the user or update an error state
            alert('Failed to delete comment. Please check connection and try again. ' + err.message);
        }
    }
    
    // Handle form submission
    function handleSubmit(event) {
        event.preventDefault();
        addComment();
    }
    
    // Format timestamp for display
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }
    
    // Load comments when component mounts
    onMount(fetchComments);
</script>

<div class="comments-container">
    <h3>Comments</h3>
    
    <!-- Comment input form -->
    <form class="comment-form" on:submit={handleSubmit}>
        <input 
            type="text" 
            bind:value={newComment} 
            placeholder="Leave a comment..."
            aria-label="New comment content"
        >
        <button type="submit" disabled={!newComment.trim()}>
            Add Comment
        </button>
    </form>
    
    <!-- Comments display -->
    <div class="comments-list">
        {#if loading && comments.length === 0}
            <div class="loading">Loading comments...</div>
        {:else if error && comments.length === 0}
            <div class="error">
                <p>Error loading comments: {error}</p>
                <button on:click={fetchComments}>Try Again</button>
            </div>
        {:else if comments.length === 0}
            <div class="empty-state">No comments yet. Be the first to add one!</div>
        {:else}
            <ul>
                {#each comments as comment (comment.id)}
                    <li class="comment-item">
                        <div class="comment-content">{comment.content}</div>
                        <div class="comment-meta">
                            <span class="comment-timestamp">
                                {#if comment.timestamp}
                                    {formatDate(comment.timestamp)}
                                {:else}
                                    Just now
                                {/if}
                            </span>
                            <button 
                                class="delete-button" 
                                on:click={() => deleteComment(comment.id)}
                                aria-label="Delete comment"
                            >
                                ×
                            </button>
                        </div>
                    </li>
                {/each}
            </ul>
        {/if}
    </div>
</div>

<style>
    .comments-container {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    h3 {
        color: #ff3e00;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    
    .comment-form {
        display: flex;
        margin-bottom: 1.5rem;
        gap: 0.5rem;
    }
    
    input {
        flex: 1;
        padding: 0.75rem;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    
    button {
        background-color: #ff3e00;
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    button:hover {
        background-color: #e63600;
    }
    
    button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
    
    .comments-list {
        margin-top: 1.5rem;
    }
    
    .loading, .error, .empty-state {
        text-align: center;
        padding: 2rem;
        background-color: #f9f9f9;
        border-radius: 8px;
    }
    
    .error {
        color: #d33;
    }
    
    ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .comment-item {
        padding: 1rem;
        border-bottom: 1px solid #eee;
        position: relative;
    }
    
    .comment-item:last-child {
        border-bottom: none;
    }
    
    .comment-content {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .comment-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .comment-timestamp {
        font-size: 0.8rem;
        color: #777;
    }
    
    .delete-button {
        background-color: transparent;
        color: #999;
        border: none;
        font-size: 1.5rem;
        font-weight: bold;
        cursor: pointer;
        line-height: 1;
        padding: 0 0.5rem;
        border-radius: 4px;
        transition: all 0.2s;
    }
    
    .delete-button:hover {
        background-color: #ff3e00;
        color: white;
    }
</style> 