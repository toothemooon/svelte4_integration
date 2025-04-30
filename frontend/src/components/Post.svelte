<script>
    // This component is loaded when the user navigates to the '/post/:id' route
    // It displays a single blog post based on the ID in the URL parameter
    import { onMount } from 'svelte';
    import { params } from 'svelte-spa-router';
    
    // State for the post data
    let post = null;
    let loading = true;
    let error = null;
    
    // Fetch post data when component mounts
    onMount(async () => {
        try {
            // In a real app, you would fetch from your backend API using the ID
            // For example: await fetch(`http://localhost:5001/api/posts/${$params.id}`);
            
            // Simulating API response for now
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Check if we have a valid ID
            if ($params.id) {
                // Simulate fetching post from database
                post = {
                    id: $params.id,
                    title: "Example Blog Post #" + $params.id,
                    content: "This is a placeholder for the blog post content. In a real application, this content would be fetched from a database based on the post ID from the URL.",
                    author: "User",
                    date: new Date().toLocaleDateString()
                };
            } else {
                error = "Post not found";
            }
        } catch (err) {
            error = "Failed to load post";
            console.error(err);
        } finally {
            loading = false;
        }
    });
</script>

<!-- Post detail page that displays a single blog post -->
<div class="page">
    {#if loading}
        <div class="loading">Loading post...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else}
        <article class="post">
            <h1>{post.title}</h1>
            <div class="post-meta">
                <span>By {post.author}</span>
                <span>•</span>
                <span>{post.date}</span>
            </div>
            
            <div class="post-content">
                <p>{post.content}</p>
            </div>
            
            <div class="post-actions">
                <a href="/" class="back-button">← Back to posts</a>
            </div>
        </article>
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
    
    /* Back button styling */
    .post-actions {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
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
</style>
