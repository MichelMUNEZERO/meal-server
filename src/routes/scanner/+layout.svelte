<script>
  import { authStore } from "$lib/stores/auth.js";
  import { scannerSession } from "$lib/stores/scannerSession.js";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { LogOut, Scan, Users, Menu, X, LayoutDashboard, History } from "lucide-svelte";
  import { onMount } from "svelte";
  import Toast from "$lib/components/Toast.svelte";

  let { children } = $props();
  let mobileMenuOpen = $state(false);

  // Ensure only authenticated users with the 'scanner' role can access this layout
  onMount(() => {
    if (!$authStore.isAuthenticated || $authStore.role !== "scanner") {
      goto("/login");
    }
  });

  // Handle user logout and redirect
  function logout() {
    authStore.logout();
    goto("/login");
  }
</script>

<div class="scanner-shell">
  <Toast />

  <!-- Desktop Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-icon">
        <Scan size={20} />
      </div>
      <span class="logo-text">Meal Scanner</span>
    </div>

    <nav class="sidebar-nav">
      <a href="/scanner" class="nav-link {$page.url.pathname === '/scanner' ? 'active' : ''}">
        <LayoutDashboard size={20} />
        Scanner Dashboard
      </a>
      <a href="/scanner/history" class="nav-link {$page.url.pathname === '/scanner/history' ? 'active' : ''}">
        <History size={20} />
        Recent Scanned
      </a>
      
      <!-- Centralized Scan Summary Badge inside Sidebar -->
      <div class="scan-summary-container">
        <div class="scan-summary">
          <Users size={18} class="summary-icon" />
          <div class="summary-details">
            <span class="summary-count">{$scannerSession.totalScans}</span>
            <span class="summary-label">Total Scanned</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="scanner-user">
        <p class="user-name">{$authStore.user?.name || "Scanner Agent"}</p>
        <p class="scanner-role">Scanner Access</p>
      </div>
      <button class="logout-btn" onclick={logout} aria-label="Sign Out">
        <LogOut size={20} />
        Sign Out
      </button>
    </div>
  </aside>

  <!-- Mobile Topbar -->
  <header class="mobile-header">
    <button class="menu-btn" onclick={() => (mobileMenuOpen = true)}>
      <Menu size={24} />
    </button>
    <div class="mobile-logo">
      <span class="text-accent">
        <Scan size={20} />
      </span>
      <span class="logo-text">Meal Scanner</span>
    </div>
    <div class="mobile-summary">
      <Users size={16} />
      <span>{$scannerSession.totalScans}</span>
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
    <div class="mobile-menu fade-in-left">
      <div class="mobile-menu-header">
        <div class="mobile-logo">
          <span class="text-accent">
            <Scan size={20} />
          </span>
          <span class="logo-text">Meal Scanner</span>
        </div>
        <button class="close-btn" onclick={() => (mobileMenuOpen = false)}>
          <X size={24} />
        </button>
      </div>
      
      <div class="mobile-nav">
        <a href="/scanner" class="mobile-nav-link {$page.url.pathname === '/scanner' ? 'active' : ''}" onclick={() => (mobileMenuOpen = false)}>
          <LayoutDashboard size={20} />
          Scanner Dashboard
        </a>
        <a href="/scanner/history" class="mobile-nav-link {$page.url.pathname === '/scanner/history' ? 'active' : ''}" onclick={() => (mobileMenuOpen = false)}>
          <History size={20} />
          Recent Scanned
        </a>
      </div>

      <div class="mobile-menu-footer">
        <div class="scanner-user-mobile">
          <p class="user-name">{$authStore.user?.name || "Scanner Agent"}</p>
          <p class="scanner-role">Scanner Access</p>
        </div>
        <button class="mobile-logout-btn" onclick={logout}>
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </div>
  {/if}

  <!-- Dynamic Content Area -->
  <main class="main-content">
    <div class="content-wrapper">
      {@render children()}
    </div>
  </main>
</div>

<style>
  /* Layout Shell */
  .scanner-shell {
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

  .logo-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background-color: var(--color-accent);
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(229, 77, 56, 0.2);
  }

  .logo-text {
    font-weight: 700;
    font-size: 1.25rem;
    color: white;
    letter-spacing: -0.02em;
  }

  .text-accent {
    color: var(--color-accent);
  }

  .sidebar-nav {
    flex: 1;
    padding: 0 1rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
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
    text-decoration: none;
  }

  .nav-link:hover, .nav-link.active {
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
  }

  .scan-summary-container {
    padding: 1.25rem;
    margin-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }

  .scan-summary {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background-color: rgba(46, 204, 113, 0.1);
    color: var(--color-success);
    border-radius: var(--radius-md);
    border: 1px solid rgba(46, 204, 113, 0.2);
  }

  .summary-details {
    display: flex;
    flex-direction: column;
  }

  .summary-count {
    font-size: 1.25rem;
    font-weight: 800;
  }

  .summary-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
    opacity: 0.9;
  }

  .sidebar-footer {
    padding: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .scanner-user {
    display: flex;
    flex-direction: column;
  }

  .user-name {
    font-weight: 700;
    font-size: 0.9375rem;
    color: white;
  }

  .scanner-role {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
    text-transform: capitalize;
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
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .logout-btn:hover {
    background-color: var(--color-accent);
    border-color: var(--color-accent);
  }

  /* Mobile Header Styles */
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
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
    cursor: pointer;
  }

  .mobile-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 700;
  }

  .mobile-summary {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    background-color: rgba(46, 204, 113, 0.1);
    color: var(--color-success);
    padding: 0.375rem 0.75rem;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.875rem;
  }

  /* Mobile Menu Styles */
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

  .fade-in-left {
    animation: fadeInLeft 0.3s ease-out;
  }

  @keyframes fadeInLeft {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
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

  .close-btn {
    background: none;
    border: none;
    color: var(--color-text-muted);
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

  .mobile-menu-footer {
    padding: 1.25rem;
    border-top: 1px solid var(--color-border);
  }

  .scanner-user-mobile {
    margin-bottom: 1rem;
    padding: 0 1rem;
  }

  .scanner-user-mobile .user-name {
    color: var(--color-primary);
  }

  .scanner-user-mobile .scanner-role {
    color: var(--color-text-muted);
  }

  .mobile-logout-btn {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    color: var(--color-accent);
    background: none;
    border: none;
    font-weight: 700;
    text-align: left;
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: background-color 0.2s;
  }

  .mobile-logout-btn:hover {
    background-color: rgba(229, 77, 56, 0.05);
  }

  /* Main Content Styles */
  .main-content {
    flex: 1;
    margin-left: 280px;
    background-color: var(--color-bg);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .content-wrapper {
    flex: 1;
    padding: 2.5rem;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  @media (max-width: 1024px) {
    .main-content {
      margin-left: 0;
    }
    
    .content-wrapper {
      padding: 5.5rem 1rem 2rem; /* Add padding-top to account for mobile header */
    }
  }
</style>
