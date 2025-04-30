<script>
    // This component is loaded when the user navigates to the '/create' route
    // It's referenced in the routes object in App.svelte
    
    // State variables for form inputs
    let title = '';
    let content = '';
    
    // Form submission handler function
    function handleSubmit() {
        // Here you would handle the form submission
        // In a real app, this would send data to a backend API
        console.log('Submitting post:', { title, content });
        alert('Post created (simulated)');
        
        // Reset form fields after submission
        title = '';
        content = '';
    }
</script>

<!-- Create Post page content that is displayed when this route is active -->
<!-- Contains a form with input fields and a submit button -->
<div class="page">
    <h1>Create New Post</h1>
    
    <!-- Form with event modifier preventDefault to handle the submission in JavaScript -->
    <!-- instead of the browser's default form submission behavior -->
    <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
            <label for="title">Title</label>
            <!-- bind:value is a Svelte directive that creates two-way binding -->
            <!-- between the input value and the title variable -->
            <input id="title" type="text" bind:value={title} required>
        </div>
        
        <div class="form-group">
            <label for="content">Content</label>
            <textarea id="content" bind:value={content} rows="6" required></textarea>
        </div>
        
        <button type="submit">Create Post</button>
    </form>
</div>

<style>
    /* Common page styling consistent with other route components */
    .page {
        padding: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Svelte's orange brand color for the main heading */
    h1 {
        color: #ff3e00;
    }
    
    /* Spacing between form groups for better readability */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    /* Style for form labels */
    label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    
    /* Style for input fields and textareas */
    input, textarea {
        width: 100%;
        padding: 0.5rem;
        font-size: 1rem;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    
    /* Style for the submit button */
    button {
        background-color: #ff3e00;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border-radius: 4px;
        cursor: pointer;
    }
    
    /* Darken the button color on hover for better UX */
    button:hover {
        background-color: #e63600;
    }
</style> 