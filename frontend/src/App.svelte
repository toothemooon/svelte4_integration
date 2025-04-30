<script>
	import { onMount } from 'svelte';
	// Import the Router component for handling client-side routing
	import Router from 'svelte-spa-router';
	// Import the location store which tracks the current URL path
	import { location } from 'svelte-spa-router';
	
	// Import our components
	import Navbar from './components/Navbar.svelte';
	import Footer from './components/Footer.svelte';
	import Home from './components/Home.svelte';
	import Post from './components/Post.svelte';
	import About from './components/About.svelte';
	
	// let backendStatus = 'Loading...';
	let users = [];
	let error = null;
	
	// Define routes for the SPA router
	// This maps URL paths to their corresponding components
	const routes = {
		'/': Home,        // Home page at root URL
		'/post/:id': Post,  // Post detail page with ID parameter
		'/about': About   // About page
	};
	
	// Function to fetch backend health
	async function checkBackendHealth() {
		try {
			const response = await fetch('http://localhost:5001/api/health');
			const data = await response.json();
			// backendStatus = data.message;
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

<div class="app-container">
	<!-- The Navbar component receives the current route path from the location store -->
	<!-- The $ prefix means we're subscribing to the store's value -->
	<Navbar currentPath={$location} />

	<!-- Main content area where different components are rendered based on the route -->
	<!-- The Router component handles switching between components -->
	<div class="content">
		<Router {routes} />
	</div>

	<!-- Footer component with backend status and user info -->
	<Footer {backendStatus} {users} {error} />
</div>

<style>
	/* Overall app container */
	.app-container {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	/* Content area that grows to fill available space */
	.content {
		flex: 1;
		margin-bottom: 2rem;
	}
</style>