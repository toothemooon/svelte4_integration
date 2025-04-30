<script>
    import { onMount } from 'svelte';
    
    // Props with default values
    export let backendStatus = 'Loading...';
    export let users = [];
    export let error = null;
    
    // Current year for copyright
    const currentYear = new Date().getFullYear();
</script>

<footer>
    <div class="footer-container">
        <!-- Backend Connection Info -->
        <div class="card">
            <h3>Backend Connection</h3>
            {#if error}
                <p class="error">{error}</p>
            {:else}
                <p>Status: {backendStatus}</p>
            {/if}
        </div>
        
        <!-- Users from Database -->
        <div class="card">
            <h3>Users from Database</h3>
            {#if users.length === 0}
                <p>No users found or still loading...</p>
            {:else}
                <ul>
                    {#each users as user}
                        <li>{user.username} ({user.email})</li>
                    {/each}
                </ul>
            {/if}
        </div>
        
        <!-- Credits -->
        <div class="credits">
            <p>Made by サラダ &copy; {currentYear}</p>
            <p class="version">v1.0.0</p>
        </div>
    </div>
</footer>

<style>
    /* Footer container */
    footer {
        text-align: center;
        padding: 1em;
        background-color: #f5f5f5;
        border-top: 1px solid #eaeaea;
        margin-top: 2rem;
    }
    
    .footer-container {
        max-width: 800px;
        margin: 0 auto;
    }

    /* Card style for info sections */
    .card {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 1em;
        margin: 1em 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Heading style in the footer */
    h3 {
        color: #ff3e00;
        font-weight: 400;
        margin-bottom: 0.5em;
    }
    
    /* Error text styling */
    .error {
        color: #d33;
    }
    
    /* User list styling */
    ul {
        text-align: left;
        margin: 0 auto;
        max-width: 400px;
        padding-left: 1.5rem;
    }
    
    /* Credits section */
    .credits {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
        font-size: 0.9rem;
        color: #666;
    }
    
    .version {
        font-size: 0.8rem;
        margin-top: 0.25rem;
        color: #999;
    }
    
    /* Responsive design */
    @media (max-width: 640px) {
        .footer-container {
            padding: 0 1rem;
        }
    }
</style>
