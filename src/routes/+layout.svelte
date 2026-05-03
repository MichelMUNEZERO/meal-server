<script>
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.js';

	let { children } = $props();

	// Initialize the single device login enforcement
	onMount(() => {
		authStore.initSessionListener();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
