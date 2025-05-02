<!-- frontend/src/components/CreatePost.svelte -->
<script>
    import { onMount } from 'svelte';
    import { isLoggedIn, token as authToken } from '../authStore.js'; // Remove userRole import
    import { push } from 'svelte-spa-router'; // For redirecting
    import { API_URL } from '../config.js'; // Import the API URL
    import { get } from 'svelte/store'; // Import get to read store value once

    let title = '';
    let content = '';
    let submitting = false;
    let error = null;
    let success = null;

    // Route Guard: Redirect if not logged in
    onMount(() => {
        const unsubscribe = isLoggedIn.subscribe(loggedIn => {
            if (!loggedIn) {
                console.log('User not logged in, redirecting from /create-post');
                push('/'); // Redirect to home page
                return;
            }
        });
        return unsubscribe;
    });

    async function handleSubmit() {
        submitting = true;
        error = null;
        success = null;

        // Basic validation
        if (!title.trim() || !content.trim()) {
            error = "Title and content cannot be empty.";
            submitting = false;
            return;
        }

        try {
            const currentToken = get(authToken); // Get the current token value
            if (!currentToken) {
                throw new Error("Authentication token not found. Please log in again.");
            }

            // --- Call the backend API --- 
            console.log('Submitting post with token:', currentToken);
            const response = await fetch(`${API_URL}/api/posts`, { // Use API_URL
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${currentToken}` // Include the token
                },
                body: JSON.stringify({ title, content })
            });

            if (!response.ok) {
                // Try to get error message from backend response body
                let errorMsgText = `HTTP error! Status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsgText = errorData.message || errorData.error || errorMsgText;
                } catch (e) {
                    // Ignore if response body is not JSON
                }
                 // Check for specific auth error status
                 if (response.status === 401) {
                     errorMsgText += ". Your session may have expired. Please log out and log back in.";
                     // Consider forcing logout here: import { logout } from '../authStore.js'; logout();
                 }
                throw new Error(errorMsgText);
            }
            
            const result = await response.json();
            console.log('Post created:', result);
            // --- End of API call ---

            // Use success message from backend if available, otherwise default
            success = result.message || "Post created successfully!";
            title = ''; // Clear form
            content = '';
            
            // Optional: Redirect to the new post page after a short delay
            // setTimeout(() => {
            //     if (result && result.id) {
            //         push(`/post/${result.id}`);
            //     }
            // }, 1500); 

        } catch (err) {
            console.error('Error creating post:', err);
            error = `Failed to create post: ${err.message}`;
        } finally {
            submitting = false;
        }
    }
</script>

<div class="page">
    <h1>Create New Post</h1>

    {#if success}
        <div class="message success">{success}</div>
    {/if}
    {#if error}
        <div class="message error">{error}</div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="create-post-form">
        <div class="form-group">
            <label for="title">Title</label>
            <input type="text" id="title" bind:value={title} required disabled={submitting}>
        </div>
        <div class="form-group">
            <label for="content">Content</label>
            <textarea id="content" bind:value={content} rows="10" required disabled={submitting}></textarea>
        </div>
        <button type="submit" class="submit-button" disabled={submitting}>
            {#if submitting} Creating... {:else} Create Post {/if}
        </button>
    </form>
</div>

<style>
    .page {
        padding: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
    h1 {
        color: #ff3e00;
        margin-bottom: 1.5rem;
    }
    .create-post-form {
        background-color: #f9f9f9;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .form-group {
        margin-bottom: 1.5rem;
    }
    label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #333;
    }
    input[type="text"], textarea {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box; /* Include padding in width */
    }
    textarea {
        resize: vertical; /* Allow vertical resizing */
    }
    .submit-button {
        background-color: #ff3e00;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
        display: inline-block; /* Allow disabling */
    }
    .submit-button:hover {
        background-color: #e63600;
    }
    .submit-button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
    .message {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
        text-align: center;
    }
    .success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style> 