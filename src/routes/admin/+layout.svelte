<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.js';
  import { requireRole } from '$lib/utils/guards.js';
  import { ROLES } from '$lib/utils/constants.js';
  import AppShell from '$lib/components/AppShell.svelte';
  import {
    LayoutDashboard,
    Users,
    Utensils,
    ClipboardList,
    Upload,
    ScanLine,
    Settings
  } from 'lucide-svelte';
  import '$lib/styles/admin-pages.css';

  let { children } = $props();

  onMount(() => {
    requireRole(ROLES.ADMIN);
  });

  function logout() {
    authStore.logout();
    goto('/login');
  }

  const navItems = [
    { name: 'Overview', path: '/admin', icon: LayoutDashboard },
    { name: 'Users', path: '/admin/users', icon: Users },
    { name: 'Meal packages', path: '/admin/meals', icon: Utensils },
    { name: 'Attendance', path: '/admin/attendance', icon: ClipboardList },
    { name: 'QR scanner', path: '/admin/scanner', icon: ScanLine },
    { name: 'Bulk upload', path: '/admin/upload', icon: Upload },
    { name: 'Settings', path: '/admin/settings', icon: Settings }
  ];
</script>

<div class="admin-layout">
  <AppShell
    brand="Admin"
    brandInitial="A"
    {navItems}
    userName={$authStore.user?.name}
    userRole="Administrator"
    onlogout={logout}
  >
    <div class="admin-content-wrapper">
      {@render children()}
    </div>
  </AppShell>
</div>

<style>
  .admin-layout :global(.main-content) {
    width: 100%;
    max-width: 100%;
  }

  .admin-content-wrapper {
    width: 100%;
    max-width: 56rem;
    margin: 0 auto;
  }
</style>
