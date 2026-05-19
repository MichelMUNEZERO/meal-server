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
    Upload
  } from 'lucide-svelte';

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
    { name: 'Bulk upload', path: '/admin/upload', icon: Upload }
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
    {@render children()}
  </AppShell>
</div>

<style>
  .admin-layout :global(.main-content) {
    max-width: 1280px;
  }
</style>
