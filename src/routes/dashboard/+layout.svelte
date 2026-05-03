<script>
  import { authStore } from "$lib/stores/auth.js";
  import { goto } from "$app/navigation";
  import {
    LayoutDashboard,
    QrCode,
    History,
    LogOut,
    User,
    Menu,
    X,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import Toast from "$lib/components/Toast.svelte";

  let { children } = $props();
  let mobileMenuOpen = $state(false);

  onMount(() => {
    if (!$authStore.isAuthenticated) {
      goto("/login");
    }
  });

  function logout() {
    authStore.logout();
    goto("/login");
  }

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "QR Code", path: "/dashboard/qr", icon: QrCode },
    { name: "History", path: "/dashboard/history", icon: History },
  ];
</script>

<div class="dashboard-shell">
  <Toast />

  <!-- Sidebar for desktop -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-circle">M</div>
      <span class="logo-text">MealTrack</span>
    </div>

    <nav class="sidebar-nav">
      {#each navItems as item}
        {@const Icon = item.icon}
        <a href={item.path} class="nav-link">
          <Icon size={20} />
          {item.name}
        </a>
      {/each}
    </nav>

    <div class="sidebar-footer">
      <button class="logout-btn" onclick={logout}>
        <LogOut size={20} />
        Logout
      </button>
    </div>
  </aside>

  <!-- Mobile Topbar -->
  <header class="mobile-header">
    <button class="menu-btn" onclick={() => (mobileMenuOpen = true)}>
      <Menu size={24} />
    </button>
    <span class="logo-text">MealTrack</span>
    <div class="user-avatar">
      <User size={20} />
    </div>
  </header>

  <!-- Mobile Menu Overlay -->
  {#if mobileMenuOpen}
    <div 
      class="mobile-overlay" 
      onclick={() => (mobileMenuOpen = false)}
      onkeydown={(e) => e.key === 'Escape' && (mobileMenuOpen = false)}
      role="button"
      tabindex="0"
      aria-label="Close menu"
    ></div>
    <div class="mobile-menu">
      <div class="mobile-menu-header">
        <span class="logo-text">MealTrack</span>
        <button class="close-btn" onclick={() => (mobileMenuOpen = false)}>
          <X size={24} />
        </button>
      </div>
      <nav class="mobile-nav">
        {#each navItems as item}
          {@const Icon = item.icon}
          <a
            href={item.path}
            class="mobile-nav-link"
            onclick={() => (mobileMenuOpen = false)}
          >
            <Icon size={20} />
            {item.name}
          </a>
        {/each}
        <button class="mobile-logout-btn" onclick={logout}>
          <LogOut size={20} />
          Logout
        </button>
      </nav>
    </div>
  {/if}

  <!-- Main Content -->
  <main class="main-content">
    {@render children()}
  </main>
</div>

<style>
  .dashboard-shell {
    display: flex;
    min-height: 100vh;
  }

  /* Sidebar Styles */
  .sidebar {
    width: 280px;
    background-color: var(--color-primary);
    color: white;
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
    left: 0;
    top: 0;
    z-index: 100;
    box-shadow: 10px 0 30px rgba(0, 0, 0, 0.03);
    transition: transform 0.3s ease;
  }

  @media (max-width: 1024px) {
    .sidebar {
      transform: translateX(-100%);
    }
  }

  .sidebar-header {
    padding: 2.5rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .logo-circle {
    width: 40px;
    height: 40px;
    background-color: var(--color-accent);
    color: white;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.25rem;
    box-shadow: 0 5px 15px rgba(229, 77, 56, 0.3);
  }

  .logo-text {
    font-weight: 700;
    font-size: 1.25rem;
    color: white;
    letter-spacing: -0.02em;
  }

  .sidebar-nav {
    flex: 1;
    padding: 0 1rem;
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.875rem 1.25rem;
    color: rgba(255, 255, 255, 0.6);
    border-radius: var(--radius-md);
    font-weight: 600;
    transition: all 0.3s ease;
    margin-bottom: 0.25rem;
  }

  .nav-link:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
  }

  .sidebar-footer {
    padding: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }

  .logout-btn {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1.25rem;
    color: white;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-full);
    font-weight: 600;
  }

  .logout-btn:hover {
    background-color: var(--color-accent);
    border-color: var(--color-accent);
  }

  /* Mobile Styles */
  .mobile-header {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background-color: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    padding: 0 1rem;
    align-items: center;
    justify-content: space-between;
    z-index: 90;
  }

  @media (max-width: 1024px) {
    .mobile-header {
      display: flex;
    }
    .mobile-header .logo-text {
      color: var(--color-primary);
    }
  }

  .menu-btn {
    background: none;
    border: none;
    color: var(--color-primary);
    padding: 0.5rem;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    background-color: var(--color-bg);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary);
  }

  .mobile-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(26, 42, 58, 0.4);
    backdrop-filter: blur(4px);
    z-index: 200;
  }

  .mobile-menu {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    background-color: var(--color-surface);
    z-index: 201;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-lg);
  }

  .mobile-menu-header {
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-bg);
  }

  .mobile-menu-header .logo-text {
    color: var(--color-primary);
  }

  .mobile-nav {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .mobile-nav-link {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    color: var(--color-text);
    text-decoration: none;
    font-weight: 600;
    border-radius: var(--radius-md);
  }

  .mobile-nav-link:hover {
    background-color: var(--color-bg);
    color: var(--color-accent);
  }

  .mobile-logout-btn {
    margin-top: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    color: var(--color-accent);
    background: none;
    border: none;
    font-weight: 700;
    text-align: left;
    border-top: 1px solid var(--color-border);
  }

  /* Main Content Styles */
  .main-content {
    flex: 1;
    padding: 2.5rem;
    margin-left: 280px;
    background-color: var(--color-bg);
    min-height: 100vh;
  }

  @media (max-width: 1024px) {
    .main-content {
      margin-left: 0;
      padding: 6rem 1.25rem 2rem;
    }
  }
</style>
