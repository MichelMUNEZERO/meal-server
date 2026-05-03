<script>
  import { authStore } from "$lib/stores/auth.js";
  import { goto } from "$app/navigation";
  import {
    LayoutDashboard,
    Users,
    Utensils,
    ClipboardList,
    Upload,
    LogOut,
    Search,
    Bell,
    Menu,
  } from "lucide-svelte";
  import { onMount } from "svelte";
  import Toast from "$lib/components/Toast.svelte";

  let { children } = $props();
  let mobileMenuOpen = $state(false);

  onMount(() => {
    if (!$authStore.isAuthenticated || $authStore.role !== "admin") {
      goto("/login");
    }
  });

  function logout() {
    authStore.logout();
    goto("/login");
  }

  const navItems = [
    { name: "Overview", path: "/admin", icon: LayoutDashboard },
    { name: "User Management", path: "/admin/users", icon: Users },
    { name: "Meal Packages", path: "/admin/meals", icon: Utensils },
    { name: "Attendance Logs", path: "/admin/attendance", icon: ClipboardList },
    { name: "Bulk Upload", path: "/admin/upload", icon: Upload },
  ];
</script>

<div class="admin-shell">
  <Toast />

  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-box">A</div>
      <span class="logo-text">Trackers Admin</span>
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
      <div class="admin-info">
        <p class="admin-name">{$authStore.user?.name || "Admin"}</p>
        <p class="admin-role">System Administrator</p>
      </div>
      <button class="logout-btn" onclick={logout}>
        <LogOut size={18} />
        Sign Out
      </button>
    </div>
  </aside>

  <!-- Admin Mobile Header -->
  <header class="admin-mobile-header">
    <button class="menu-btn" onclick={() => (mobileMenuOpen = true)}>
      <Menu size={24} />
    </button>

    <span class="logo-text">Admin Panel</span>
    <div class="admin-avatar-small">AD</div>
  </header>

  {#if mobileMenuOpen}
    <div
      class="mobile-overlay"
      onclick={() => (mobileMenuOpen = false)}
      onkeydown={(e) => e.key === "Escape" && (mobileMenuOpen = false)}
      role="button"
      tabindex="0"
      aria-label="Close menu"
    ></div>
    <div class="mobile-menu">
      <div class="mobile-menu-header">
        <span class="logo-text">Trackers Admin</span>
        <button class="close-btn" onclick={() => (mobileMenuOpen = false)}>
          <LogOut size={24} style="transform: rotate(180deg)" />
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

  <div class="main-wrapper">
    <header class="topbar">
      <div class="search-bar">
        <Search size={18} />
        <input
          type="text"
          placeholder="Search for users, records, or settings..."
        />
      </div>
      <div class="topbar-actions">
        <button class="icon-btn">
          <Bell size={20} />
          <span class="notification-dot"></span>
        </button>
        <div class="admin-avatar">AD</div>
      </div>
    </header>

    <main class="main-content">
      {@render children()}
    </main>
  </div>
</div>

<style>
  .admin-shell {
    display: flex;
    min-height: 100vh;
    background-color: var(--color-bg);
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

  .logo-box {
    width: 40px;
    height: 40px;
    background-color: var(--color-accent);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: white;
    box-shadow: 0 5px 15px rgba(229, 77, 56, 0.3);
  }

  .logo-text {
    font-weight: 700;
    font-size: 1.25rem;
    letter-spacing: -0.02em;
    color: white;
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
    text-decoration: none;
  }

  .nav-link:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
  }

  .sidebar-footer {
    padding: 1.5rem;
    background-color: rgba(0, 0, 0, 0.2);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }

  .admin-info {
    margin-bottom: 1.25rem;
  }

  .admin-name {
    font-weight: 700;
    font-size: 0.9375rem;
  }

  .admin-role {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 500;
  }

  .logout-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background-color: rgba(229, 77, 56, 0.1);
    color: var(--color-accent);
    border: 1px solid rgba(229, 77, 56, 0.2);
    border-radius: var(--radius-full);
    font-weight: 700;
    font-size: 0.875rem;
  }

  .logout-btn:hover {
    background-color: var(--color-accent);
    color: white;
  }

  .main-wrapper {
    flex: 1;
    margin-left: 280px;
    background-color: var(--color-bg);
    min-height: 100vh;
  }

  @media (max-width: 1024px) {
    .main-wrapper {
      margin-left: 0;
    }
  }

  .admin-mobile-header {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background-color: var(--color-primary);
    color: white;
    padding: 0 1rem;
    align-items: center;
    justify-content: space-between;
    z-index: 150;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 1024px) {
    .admin-mobile-header {
      display: flex;
    }
  }

  .menu-btn {
    background: none;
    border: none;
    color: white;
    padding: 0.5rem;
    cursor: pointer;
  }

  .admin-avatar-small {
    width: 32px;
    height: 32px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .mobile-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(26, 42, 58, 0.6);
    backdrop-filter: blur(8px);
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
    box-shadow: 20px 0 50px rgba(0, 0, 0, 0.2);
  }

  .mobile-menu-header {
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-primary);
    color: white;
  }

  .mobile-menu-header .logo-text {
    color: white;
  }

  .close-btn {
    background: none;
    border: none;
    color: white;
    padding: 0.5rem;
    cursor: pointer;
  }

  .mobile-nav {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1;
  }

  .mobile-nav-link {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    color: var(--color-text);
    text-decoration: none;
    font-weight: 600;
    border-radius: var(--radius-md);
    transition: all 0.2s;
  }

  .mobile-nav-link:hover {
    background-color: var(--color-bg);
    color: var(--color-accent);
  }

  .mobile-logout-btn {
    margin: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    color: var(--color-error);
    background-color: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.1);
    border-radius: var(--radius-md);
    font-weight: 700;
    text-align: left;
    cursor: pointer;
  }

  .topbar {
    height: 72px;
    background-color: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    position: sticky;
    top: 0;
    z-index: 80;
  }

  @media (max-width: 1024px) {
    .topbar {
      display: none;
    }
  }

  .search-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background-color: var(--color-bg);
    padding: 0.5rem 1.25rem;
    border-radius: 9999px;
    width: 100%;
    max-width: 500px;
    color: var(--color-text-muted);
  }

  .search-bar input {
    background: none;
    border: none;
    flex: 1;
    font-size: 0.875rem;
    color: var(--color-text);
  }

  .search-bar input:focus {
    outline: none;
  }

  .topbar-actions {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .icon-btn {
    position: relative;
    background: none;
    border: none;
    color: var(--color-text-muted);
  }

  .notification-dot {
    position: absolute;
    top: -2px;
    right: -2px;
    width: 8px;
    height: 8px;
    background-color: var(--color-error);
    border-radius: 50%;
    border: 2px solid var(--color-surface);
  }

  .admin-avatar {
    width: 40px;
    height: 40px;
    background-color: var(--color-primary);
    color: white;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.875rem;
  }

  .main-content {
    padding: 2.5rem;
  }

  @media (max-width: 1024px) {
    .main-content {
      padding: 6rem 1.25rem 2rem;
    }
  }
</style>
