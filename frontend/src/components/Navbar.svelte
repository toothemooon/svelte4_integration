<script>
	// Import the push function from svelte-spa-router to handle navigation programmatically
	import { push, link } from 'svelte-spa-router';
	import { isLoggedIn, logout, userRole } from '../authStore.js'; // Import store and actions
	import { onMount } from 'svelte';
	
	// This prop receives the current path from the parent component (App.svelte)
	// It's used to highlight the active navigation link
	export let currentPath = '/';
	
	// Custom navigation function that prevents default browser navigation
	// and uses the router's push function to navigate without page reloads
	function navigate(path, event) {
		// Prevent the default link behavior (page reload)
		event.preventDefault();
		// Navigate to the specified path using the router
		push(path);
	}
	
	// Debug: Log when role changes
	onMount(() => {
		const unsubscribe = userRole.subscribe(role => {
			console.log('Current user role in Navbar:', role);
		});
		
		return unsubscribe;
	});
</script>

<!-- Main navigation component -->
<nav>
	<div class="navbar-container">
		<!-- Logo section on the left side -->
		<div class="logo">
			<!-- Logo link with click handler to navigate to home -->
			<a href="/" use:link class="brand">My Blog</a>
		</div>
		
		<!-- Navigation links on the right side -->
		<div class="nav-section">
			<a href="/" use:link class="nav-link" class:active={currentPath === '/'}>Home</a>
			<a href="/about" use:link class="nav-link" class:active={currentPath === '/about'}>About</a>
			{#if $isLoggedIn}
				<!-- Debug: Show current role -->
				<span class="nav-link" style="color: grey;">Role: {$userRole || 'none'}</span>
				
				{#if $userRole === 'admin'}
					<a href="/create-post" use:link class="nav-link">Create Post</a>
				{/if}
				<button on:click={logout} class="nav-link logout-btn">Logout</button>
			{:else}
				<a href="/auth" use:link class="nav-link login-btn">Login</a>
			{/if}
		</div>
	</div>
</nav>

<style>
	/* Styling for the entire navbar */
	nav {
		background-color: #333;
		color: white;
		padding: 0 1rem;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	/* Container to center and limit the width of navbar content */
	.navbar-container {
		display: flex;
		justify-content: space-between;
		align-items: center;
		max-width: 1200px;
		margin: 0 auto;
		height: 60px;
	}

	/* Styling for the logo text */
	.logo a {
		color: white;
		font-size: 1.5rem;
		font-weight: bold;
		text-decoration: none;
	}

	/* Right side navigation section */
	.nav-section {
		display: flex;
		align-items: center;
	}

	/* Common styling for all navigation items */
	.nav-link {
		color: #ccc;
		text-decoration: none;
		padding: 0.5rem 0.75rem;
		margin: 0 0.25rem;
		font-size: 1rem;
		cursor: pointer;
		transition: color 0.3s;
		background: none;
		border: none;
		font-family: inherit;
	}

	/* Active and hover states */
	.active, .nav-link:hover {
		color: white;
	}
	
	/* Logout button styling */
	.logout-btn {
		border: 1px solid #e74c3c;
		color: #e74c3c;
		border-radius: 4px;
		margin-left: 0.5rem;
	}
	
	.logout-btn:hover {
		background-color: #e74c3c;
		color: white;
	}
	
	/* Login button styling */
	.login-btn {
		background-color: #4a90e2;
		color: white;
		border-radius: 4px;
		margin-left: 0.5rem;
	}
	
	.login-btn:hover {
		background-color: #357abD;
	}

	/* Responsive design for mobile screens */
	@media (max-width: 768px) {
		/* Stack the elements vertically on small screens */
		.navbar-container {
			flex-direction: column;
			height: auto;
			padding: 1rem 0;
		}

		.nav-section {
			flex-wrap: wrap;
			justify-content: center;
			margin-top: 1rem;
		}

		.nav-link {
			margin: 0.25rem;
		}
		
		.logout-btn, .login-btn {
			margin-left: 0.25rem;
		}
	}
</style> 


