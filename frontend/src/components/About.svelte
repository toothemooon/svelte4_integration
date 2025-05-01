<script>
    // This component is loaded when the user navigates to the '/about' route
    // It's referenced in the routes object in App.svelte
</script>

<!-- About page content that is displayed when this route is active -->
<!-- Contains information about the site/author -->
<div class="page">
    <h1>About Me</h1>
    
    <p>This is my hobby blog site, testing cloud deployment.</p>
    
    <h2>My Goal</h2>
    <p>Continue to learn and build my blog web app.</p>
    
    <h2>Contact</h2>
    <p>You can reach me at hsc110110123@outlook.com</p>
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
    
    /* Style for section headings */
    h2 {
        margin-top: 1.5rem;
        color: #333;
    }
    
    /* Improved paragraph readability with increased line height */
    p {
        line-height: 1.6;
    }
</style> 