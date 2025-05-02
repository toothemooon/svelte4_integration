<script>
    // This component is loaded when the user navigates to the '/' route
    // It's referenced in the routes object in App.svelte
    import { onMount } from 'svelte';
    import { push } from 'svelte-spa-router';
    import { API_URL } from '../config.js';
    
    // State for blog posts
    let posts = [];
    let loading = true;
    let error = null;
    
    // Function to navigate to a post
    function viewPost(id) {
        push(`/post/${id}`);
    }
    
    // Handle keyboard events for accessibility
    function handleKeydown(id, event) {
        // Navigate on Enter or Space key
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            viewPost(id);
        }
    }
    
    // Fetch blog posts when component mounts
    onMount(async () => {
        loading = true;
        error = null;
        try {
            const response = await fetch(`${API_URL}/api/posts`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            posts = await response.json();
            
            // Optional: Format timestamp for display here if needed
            // posts = posts.map(post => ({ ...post, formattedDate: new Date(post.timestamp).toLocaleDateString() }));

        } catch (err) {
            error = "Failed to load posts";
            console.error('Error fetching posts:', err);
            // Keep existing hardcoded data as fallback? Or show error only.
            // posts = [ /* ... original hardcoded posts ... */ ]; 
        } finally {
            loading = false;
        }
    });

    // Function to format timestamp (if not done in onMount)
    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
</script>

<!-- Home page content that is displayed when this route is active -->
<!-- The .page class provides consistent styling across all page components -->
<div class="page">
    <h1>Welcome to my blog site!</h1>
    <p class="intro">This is a simple blog site. Click on any post to read more.</p>
    
    <!-- Blog posts list -->
    <div class="posts-container">
        <h2>Blog Posts</h2>
        {#if loading}
            <div class="loading">Loading posts...</div>
        {:else if error}
            <div class="error">{error}</div>
        {:else if posts.length === 0}
            <div class="empty-state">No posts available yet.</div>
        {:else}
            <ul class="posts-list">
                {#each posts as post (post.id)}
                    <li class="post-item">
                        <div 
                            class="post-card" 
                            on:click={() => viewPost(post.id)}
                            on:keydown={(e) => handleKeydown(post.id, e)}
                            tabindex="0"
                            role="button"
                            aria-label="Read post: {post.title}"
                        >
                            <h2>{post.title}</h2>
                            <p class="post-excerpt">{post.excerpt || 'No excerpt available.'}</p>
                            <div class="post-footer">
                                <span class="post-date">{formatDate(post.timestamp)}</span>
                                <span class="read-more">Read more →</span>
                            </div>
                        </div>
                    </li>
                {/each}
            </ul>
        {/if}
    </div>
</div>

<style>
    /* Common page styling that's consistent across route components */
    /* Each page has the same width and padding for visual consistency */
    .page {
        padding: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Svelte's orange brand color for the main heading */
    h1 {
        color: #ff3e00;
    }
    
    h2 {
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Style for intro paragraph */
    .intro {
        margin-bottom: 2rem;
        font-size: 1.1rem;
        line-height: 1.5;
    }
    
    /* Loading and error messages */
    .loading, .error, .empty-state {
        text-align: center;
        padding: 2rem;
        background-color: #f9f9f9;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error {
        color: #d33;
    }
    
    /* List of posts styling */
    .posts-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    /* Individual post item */
    .post-item {
        margin-bottom: 1.5rem;
    }
    
    /* Post card styling */
    .post-card {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }
    
    .post-card:hover, .post-card:focus {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        outline: none;
    }
    
    /* Post title */
    .post-card h2 {
        margin-top: 0;
        color: #333;
        font-size: 1.4rem;
    }
    
    /* Post excerpt */
    .post-excerpt {
        margin-bottom: 1.5rem;
        line-height: 1.5;
        color: #555;
    }
    
    /* Post footer with date and read more */
    .post-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
    }
    
    /* Post date */
    .post-date {
        color: #777;
    }
    
    /* Read more link */
    .read-more {
        color: #ff3e00;
        font-weight: 500;
    }
</style> 