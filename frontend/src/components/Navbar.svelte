<script>
	// Import the push function from svelte-spa-router to handle navigation programmatically
	import { push } from 'svelte-spa-router';
	
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
</script>

<!-- Main navigation component -->
<nav>
	<div class="navbar-container">
		<!-- Logo section on the left side -->
		<div class="logo">
			<!-- Logo link with click handler to navigate to home -->
			<!-- on:click|preventDefault prevents default behavior and calls our custom navigate function -->
			<a href="/" on:click|preventDefault={(e) => navigate('/', e)}>My Blog</a>
		</div>
		
		<!-- Navigation links on the right side -->
		<ul class="nav-links">
			<!-- Each list item represents a navigation link -->
			<!-- class:active={} is a special Svelte directive that conditionally adds the 'active' class -->
			<!-- when the condition is true, highlighting the current page -->
			<li class:active={currentPath === '/'}>
				<a href="/" on:click|preventDefault={(e) => navigate('/', e)}>Home</a>
			</li>
			<li class:active={currentPath === '/about'}>
				<a href="/about" on:click|preventDefault={(e) => navigate('/about', e)}>About</a>
			</li>
		</ul>
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
		display: flex; /* Use flexbox for layout */
		justify-content: space-between; /* Put logo on left, links on right */
		align-items: center; /* Center items vertically */
		max-width: 1200px;
		margin: 0 auto; /* Center the container horizontally */
		height: 60px;
	}

	/* Styling for the logo text */
	.logo a {
		color: white;
		font-size: 1.5rem;
		font-weight: bold;
		text-decoration: none;
	}

	/* Make the navigation links display in a row */
	.nav-links {
		display: flex;
		list-style: none;
		margin: 0;
		padding: 0;
	}

	/* Add spacing between navigation links */
	.nav-links li {
		margin-left: 1.5rem;
	}

	/* Style the navigation link text */
	.nav-links a {
		color: #ccc; /* Light gray for non-active links */
		text-decoration: none;
		font-size: 1rem;
		transition: color 0.3s; /* Smooth color transition on hover */
	}

	/* Change link color on hover for better user feedback */
	.nav-links a:hover {
		color: white;
	}

	/* Style for the currently active page link */
	.active a {
		color: white;
		font-weight: 600;
	}

	/* Responsive design for mobile screens */
	@media (max-width: 600px) {
		/* Stack the logo and links vertically on small screens */
		.navbar-container {
			flex-direction: column;
			height: auto;
			padding: 1rem 0;
		}

		/* Add space above the links when they're below the logo */
		.nav-links {
			margin-top: 1rem;
		}

		/* Adjust spacing for horizontally arranged links on mobile */
		.nav-links li {
			margin: 0 0.75rem;
		}
	}
</style> 