<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.js';

  onMount(() => {
    if ($authStore.isAuthenticated) {
      if ($authStore.role === 'admin') {
        goto('/admin');
      } else {
        goto('/dashboard');
      }
    } else {
      goto('/login');
    }
  });
</script>

<div class="loading">
  <div class="spinner"></div>
</div>

<style>
  .loading {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(13, 148, 136, 0.1);
    border-left-color: var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
