<script>
    // This component is loaded when the user navigates to the '/' route
    // It's referenced in the routes object in App.svelte
</script>

<!-- Home page content that is displayed when this route is active -->
<!-- The .page class provides consistent styling across all page components -->
<div class="page">
    <h1>Welcome to my blog site!</h1>
    <p>This is a simple blog site built with Svelte.</p>
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
</style> 