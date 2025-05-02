<!-- frontend/src/components/Auth.svelte -->
<script>
    import { register, login, errorMsg, clearError, isLoggedIn, token, userRole } from '../authStore.js'; // Import real actions
    import { onMount } from 'svelte';

    let username = '';
    let password = '';
    let isLoginMode = true; // Toggle between Login and Register

    // Add a subscription to see the token and role after login
    let currentToken = null;
    let currentRole = null;
    
    // Subscribe to token changes
    token.subscribe(value => {
        currentToken = value;
    });
    
    // Subscribe to role changes
    userRole.subscribe(value => {
        currentRole = value;
    });

    // Clear any previous errors when the component mounts or mode changes
    onMount(clearError);
    $: if (isLoginMode !== undefined) clearError(); // Clear error on mode toggle

    function toggleMode() {
        isLoginMode = !isLoginMode;
        username = ''; // Clear fields on mode switch
        password = '';
    }

    async function handleAuth() {
        if (!username.trim() || !password.trim()) {
            // Basic local validation (authStore handles API errors)
            return; 
        }
        if (isLoginMode) {
            await login(username, password); // Call login action from store
        } else {
            await register(username, password); // Call register action from store
            // Optionally switch to login mode after successful registration
            // isLoginMode = true; 
        }
        // Login/Register functions in authStore handle redirects on success
    }
</script>

<div class="auth-wrapper">
    <div class="page auth-page">
        <h1>{isLoginMode ? 'Login' : 'Register'}</h1>

        {#if $errorMsg}
            <div class="message error">{$errorMsg}</div>
        {/if}

        <form on:submit|preventDefault={handleAuth} class="auth-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" bind:value={username} required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" bind:value={password} required>
            </div>
            <button type="submit" class="submit-button">
                {isLoginMode ? 'Login' : 'Register'}
            </button>
        </form>

        <div class="toggle-mode">
            <button on:click={toggleMode} class="link-button">
                {isLoginMode ? 'Need an account? Register' : 'Already have an account? Login'}
            </button>
        </div>

        <!-- Add debugging info at the bottom of the form, only shown when logged in -->
        {#if $isLoggedIn}
        <div class="debug-info">
            <h3>Debug Information</h3>
            <p><strong>Logged in:</strong> {$isLoggedIn}</p>
            <p><strong>Role:</strong> {currentRole || 'none'}</p>
            <p><strong>Token:</strong> {currentToken ? (currentToken.length > 30 ? currentToken.substring(0, 30) + '...' : currentToken) : 'none'}</p>
        </div>
        {/if}
    </div>
</div>

<style>
    .auth-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: calc(100vh - 200px);
        padding: 0 1rem;
    }
    
    .auth-page {
        width: 100%;
        max-width: 500px; /* Increased from 400px for a wider form */
    }
    
    h1 {
        text-align: center;
        color: #ff3e00;
        margin-bottom: 1.5rem;
        font-size: 1.8rem; /* Slightly larger heading */
    }
    
    .auth-form {
        background-color: #f9f9f9;
        padding: 2.5rem; /* Increased padding for more space inside */
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
    
    input[type="text"], input[type="password"] {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box; 
    }
    
    .submit-button {
        background-color: #ff3e00;
        color: white;
        border: none;
        padding: 0.8rem; /* Slightly taller button */
        width: 100%; 
        font-size: 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
        display: block;
        margin-top: 1rem;
    }
    
    .submit-button:hover {
        background-color: #e63600;
    }
    
    .toggle-mode {
        text-align: center;
        margin-top: 1.5rem;
    }
    
    .link-button {
        background: none;
        border: none;
        color: #ff3e00;
        cursor: pointer;
        text-decoration: underline;
        font-size: 0.9rem;
    }
    
    .message {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
        text-align: center;
    }
    
    .error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .debug-info {
        margin-top: 2rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    
    .debug-info h3 {
        margin-top: 0;
        color: #333;
    }
</style> 