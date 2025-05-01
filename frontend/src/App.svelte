<script>
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
	
	// Define routes for the SPA router
	// This maps URL paths to their corresponding components
	const routes = {
		'/': Home,        // Home page at root URL
		'/post/:id': Post,  // Post detail page with ID parameter
		'/about': About   // About page
	};
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

	<!-- Footer component with credits only -->
	<Footer />
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