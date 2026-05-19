<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.js';
  import { scannerSession } from '$lib/stores/scannerSession.js';
  import { requireRole } from '$lib/utils/guards.js';
  import { ROLES } from '$lib/utils/constants.js';
  import AppShell from '$lib/components/AppShell.svelte';
  import { LayoutDashboard, History, Users, Settings } from 'lucide-svelte';
  import '$lib/styles/admin-pages.css';

  let { children } = $props();

  onMount(() => {
    requireRole(ROLES.SCANNER);
  });

  function logout() {
    authStore.logout();
    goto('/login');
  }

  const navItems = [
    { name: 'Scanner', path: '/scanner', icon: LayoutDashboard },
    { name: 'Recent scans', path: '/scanner/history', icon: History },
    { name: 'Settings', path: '/scanner/settings', icon: Settings }
  ];
</script>

<AppShell
  brand="Scanner"
  brandInitial="S"
  {navItems}
  userName={$authStore.user?.name}
  userRole="Scanner access"
  onlogout={logout}
>
  {#snippet footerSlot()}
    <div class="scan-summary">
      <Users size={18} />
      <div>
        <span class="count">{$scannerSession.totalScans}</span>
        <span class="label">Scans this session</span>
      </div>
    </div>
  {/snippet}
  <div class="scanner-content-wrapper">
    {@render children()}
  </div>
</AppShell>

<style>
  .scanner-content-wrapper {
    width: 100%;
    max-width: 56rem;
    margin: 0 auto;
  }

  .scan-summary {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1rem;
    background: rgba(22, 163, 74, 0.12);
    border: 1px solid rgba(22, 163, 74, 0.2);
    border-radius: var(--radius-md);
    color: var(--color-success);
  }

  .count {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.2;
  }

  .label {
    font-size: 0.6875rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
    opacity: 0.9;
  }
</style>
