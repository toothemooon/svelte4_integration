<script>
	import { onMount } from 'svelte';
	
	let name = 'world';
	let backendStatus = 'Loading...';
	let users = [];
	let error = null;
	
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

<main>
	<h1>Hello {name}!</h1>
	
	<div class="card">
		<h2>Backend Connection</h2>
		{#if error}
			<p class="error">{error}</p>
		{:else}
			<p>Status: {backendStatus}</p>
		{/if}
	</div>
	
	<div class="card">
		<h2>Users from Database</h2>
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
	
	<p>Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to build Svelte apps.</p>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 640px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}
	
	.card {
		background-color: #f9f9f9;
		border-radius: 8px;
		padding: 1em;
		margin: 1em 0;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}
	
	.error {
		color: #d33;
	}
	
	ul {
		text-align: left;
		margin: 0 auto;
		max-width: 400px;
	}

	@media (min-width: 640px) {
		main {
			max-width: 800px;
		}
	}
</style>