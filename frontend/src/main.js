import App from './App.svelte';

const app = new App({
	target: document.getElementById('app') || document.body,
	props: {
		name: 'world'
	}
});

export default app;