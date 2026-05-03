<script>
  import { authStore } from '$lib/stores/auth.js';
  import { goto } from '$app/navigation';
  import { LogOut, Scan, History, User } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import Toast from '$lib/components/Toast.svelte';

  let { children } = $props();

  onMount(() => {
    if (!$authStore.isAuthenticated || $authStore.role !== 'scanner') {
      goto('/login');
    }
  });

  function logout() {
    authStore.logout();
    goto('/login');
  }
</script>

<div class="scanner-shell">
  <Toast />
  
  <header class="scanner-header">
    <div class="logo">
      <Scan size={24} class="logo-icon" />
      <span>Meal Scanner</span>
    </div>
    <div class="user-actions">
      <div class="scanner-user">
        <User size={18} />
        <span class="user-name">{$authStore.user?.name}</span>
      </div>
      <button class="icon-btn" onclick={logout} title="Logout">
        <LogOut size={20} />
      </button>
    </div>
  </header>

  <main class="scanner-content">
    {@render children()}
  </main>
</div>

<style>
  .scanner-shell {
    min-height: 100vh;
    background-color: var(--color-bg);
    display: flex;
    flex-direction: column;
  }

  .scanner-header {
    height: 70px;
    background-color: var(--color-primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 700;
    font-size: 1.25rem;
  }

  .logo-icon {
    color: var(--color-accent);
  }

  .user-actions {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .scanner-user {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    background-color: rgba(255, 255, 255, 0.1);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
  }

  .icon-btn {
    background: none;
    border: none;
    color: white;
    opacity: 0.8;
    transition: opacity 0.2s;
  }

  .icon-btn:hover {
    opacity: 1;
  }

  .scanner-content {
    flex: 1;
    padding: 1.5rem;
    max-width: 600px;
    margin: 0 auto;
    width: 100%;
  }

  @media (max-width: 640px) {
    .user-name { display: none; }
    .scanner-header { padding: 0 1rem; }
  }
</style>
