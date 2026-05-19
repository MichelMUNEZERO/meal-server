<script>
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.js';
	import Toast from '$lib/components/Toast.svelte';

	let { children } = $props();

	onMount(() => {
		return authStore.initSessionListener();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<Toast />
{@render children()}
