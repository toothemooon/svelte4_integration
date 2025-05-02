<script>
    // This component is loaded when the user navigates to the '/post/:id' route
    // It displays a single blog post based on the ID in the URL parameter
    import { onMount } from 'svelte';
    import { location } from 'svelte-spa-router';
    import { push } from 'svelte-spa-router'; // Import push for navigation
    import Comments from './Comments.svelte';
    import { API_URL } from '../config.js'; // Import API_URL
    import { isLoggedIn, token, userRole } from '../authStore.js'; // Import auth stores
    
    // State for the post data
    let post = null;
    let loading = true;
    let error = null;
    let postId = null;
    let deleting = false;
    let deleteError = null;
    
    // Parse the post ID from the URL path
    $: {
        // Extract the post ID from the location string
        // The format is "/post/123" so we split and take the last part
        const urlParts = $location.split('/');
        postId = urlParts.length > 1 ? urlParts[urlParts.length - 1] : null;
        
        // If the postId changes, fetch the post data
        if (postId) {
            fetchPost(postId);
        }
    }
    
    // Function to fetch post data
    async function fetchPost(id) {
        loading = true;
        error = null;
        try {
            if (!id) {
                throw new Error("Post ID is missing from URL");
            }

            const response = await fetch(`${API_URL}/api/posts/${id}`);
            
            if (response.status === 404) {
                 throw new Error("Post not found");
            }
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            post = await response.json();
            
        } catch (err) {
            error = err.message || "Failed to load post";
            console.error('Error fetching post:', err);
        } finally {
            loading = false;
        }
    }

    // Function to delete a post
    async function deletePost() {
        if (!confirm(`Are you sure you want to delete this post: "${post.title}"?`)) {
            return; // User cancelled the deletion
        }
        
        deleting = true;
        deleteError = null;
        
        try {
            const response = await fetch(`${API_URL}/api/posts/${postId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${$token}` // Include auth token
                }
            });
            
            // Try to parse response as JSON first
            let errorData;
            let responseText;
            
            try {
                // Try to get JSON response
                errorData = await response.json();
            } catch (jsonError) {
                // If not JSON, get text
                try {
                    responseText = await response.text();
                    console.error('Non-JSON response:', responseText);
                } catch (textError) {
                    console.error('Could not read response as text:', textError);
                }
            }
            
            if (!response.ok) {
                // Different error message based on what we could get from the response
                if (errorData && errorData.message) {
                    throw new Error(errorData.message);
                } else if (responseText) {
                    throw new Error(`Server error: ${response.status}. Response: ${responseText.substring(0, 100)}...`);
                } else {
                    throw new Error(`Error deleting post. Status: ${response.status}`);
                }
            }
            
            // Successfully deleted, redirect to home page
            alert('Post deleted successfully');
            push('/');
            
        } catch (err) {
            deleteError = err.message || "Failed to delete post";
            console.error('Error deleting post:', err);
        } finally {
            deleting = false;
        }
    }

    // Function to format timestamp
    function formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString();
    }
</script>

<!-- Post detail page that displays a single blog post -->
<div class="page">
    {#if loading}
        <div class="loading">Loading post...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else if post}
        <article class="post">
            <h1>{post.title}</h1>
            <div class="post-meta">
                {#if post.author} 
                    <span>By {post.author}</span>
                    <span>•</span>
                {/if}
                <span>{formatDate(post.timestamp)}</span>
            </div>
            
            <div class="post-content">
                <p>{post.content}</p> 
            </div>
            
            <div class="post-actions">
                <a href="/" class="back-button">← Back to posts</a>
                
                <!-- Admin-only delete button -->
                {#if $isLoggedIn && $userRole === 'admin'}
                    <button 
                        class="delete-button" 
                        on:click={deletePost} 
                        disabled={deleting}
                    >
                        {#if deleting}Deleting...{:else}Delete Post{/if}
                    </button>
                {/if}
            </div>
            
            {#if deleteError}
                <div class="error">{deleteError}</div>
            {/if}
            
            <!-- Comments section, rendered only if post.id exists -->
            {#if post.id}
                <Comments postId={post.id} />
            {/if}
            
        </article>
    {:else} 
        <div class="error">Post data could not be loaded.</div>
    {/if}
</div>

<style>
    /* Common page styling consistent with other route components */
    .page {
        padding: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Post title */
    h1 {
        color: #ff3e00;
        margin-bottom: 0.5rem;
    }
    
    /* Loading and error messages */
    .loading, .error {
        text-align: center;
        padding: 2rem;
        font-size: 1.2rem;
    }
    
    .error {
        color: #d33;
    }
    
    /* Post metadata styling */
    .post-meta {
        color: #666;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }
    
    .post-meta span {
        margin-right: 0.5rem;
    }
    
    /* Post content styling */
    .post-content {
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    /* Action buttons styling */
    .post-actions {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .back-button {
        display: inline-block;
        color: #ff3e00;
        text-decoration: none;
        font-weight: 500;
    }
    
    .back-button:hover {
        text-decoration: underline;
    }
    
    .delete-button {
        background-color: #e74c3c;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: background-color 0.2s;
    }
    
    .delete-button:hover {
        background-color: #c0392b;
    }
    
    .delete-button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
</style>
