<script>
	import { onMount } from 'svelte';
	// Import the Router component for handling client-side routing
	import Router from 'svelte-spa-router';
	// Import the location store which tracks the current URL path
	import { location } from 'svelte-spa-router';
	
	// Import our components
	import Navbar from './components/Navbar.svelte';
	import Home from './components/Home.svelte';
	import CreatePost from './components/CreatePost.svelte';
	import About from './components/About.svelte';
	
	let backendStatus = 'Loading...';
	let users = [];
	let error = null;
	
	// Define routes for the SPA router
	// This maps URL paths to their corresponding components
	const routes = {
		'/': Home,        // Home page at root URL
		'/create': CreatePost,  // Create Post page
		'/about': About   // About page
	};
	
	// Function to fetch backend health
	async function checkBackendHealth() {
		try {
			const response = await fetch('http://localhost:5001/api/health');
			const data = await response.json();
			backendStatus = data.message;
		} catch (err) {
			error = "Failed to connect to backend. Make sure it's running on port 5001.";
			console.error(err);
		}
	}
	
	// Function to fetch users
	async function fetchUsers() {
		try {
			const response = await fetch('http://localhost:5001/api/users');
			users = await response.json();
		} catch (err) {
			console.error('Error fetching users:', err);
		}
	}
	
	// When component mounts, fetch data from backend
	onMount(() => {
		checkBackendHealth();
		fetchUsers();
	});
</script>

<!-- The Navbar component receives the current route path from the location store -->
<!-- The $ prefix means we're subscribing to the store's value -->
<Navbar currentPath={$location} />

<!-- Main content area where different components are rendered based on the route -->
<!-- The Router component handles switching between components -->
<div class="content">
	<Router {routes} />
</div>

<!-- Footer with backend information -->
<footer>
	<div class="card">
		<h3>Backend Connection</h3>
		{#if error}
			<p class="error">{error}</p>
		{:else}
			<p>Status: {backendStatus}</p>
		{/if}
	</div>
	
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
</footer>

<style>
	/* Content area with minimum height to push footer down */
	.content {
		min-height: calc(100vh - 200px);
	}
	
	/* Footer styling */
	footer {
		text-align: center;
		padding: 1em;
		max-width: 640px;
		margin: 0 auto;
	}

	/* Heading style in the footer */
	h3 {
		color: #ff3e00;
		font-weight: 400;
		margin-bottom: 0.5em;
	}
	
	/* Card style for info sections */
	.card {
		background-color: #f9f9f9;
		border-radius: 8px;
		padding: 1em;
		margin: 1em 0;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
	}

	/* Responsive design for larger screens */
	@media (min-width: 640px) {
		footer {
			max-width: 800px;
		}
	}
</style>