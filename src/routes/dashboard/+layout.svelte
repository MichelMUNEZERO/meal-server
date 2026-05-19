<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.js';
  import { requireRole } from '$lib/utils/guards.js';
  import { ROLES } from '$lib/utils/constants.js';
  import AppShell from '$lib/components/AppShell.svelte';
  import { LayoutDashboard, QrCode, History, Settings } from 'lucide-svelte';

  let { children } = $props();

  onMount(() => {
    requireRole(ROLES.USER);
  });

  function logout() {
    authStore.logout();
    goto('/login');
  }

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { name: 'QR Code', path: '/dashboard/qr', icon: QrCode },
    { name: 'History', path: '/dashboard/history', icon: History },
    { name: 'Account', path: '/dashboard/settings', icon: Settings }
  ];
</script>

<AppShell
  brand="Meal Trackers"
  brandInitial="M"
  {navItems}
  userName={$authStore.user?.name}
  userRole="Member"
  onlogout={logout}
>
  {@render children()}
</AppShell>
