<script>
  import { page } from '$app/stores';
  import { Menu, X, LogOut } from 'lucide-svelte';

  /**
   * @typedef {{ name: string, path: string, icon: import('svelte').Component }}
   */
  let {
    brand = 'Meal Trackers',
    brandInitial = 'M',
    navItems = [],
    userName = '',
    userRole = '',
    footerSlot,
    children,
    onlogout
  } = $props();

  let mobileMenuOpen = $state(false);

  function isActive(path) {
    const current = $page.url.pathname;
    const exactPaths = ['/admin', '/dashboard', '/scanner'];
    if (exactPaths.includes(path)) {
      return current === path || current === `${path}/`;
    }
    return current === path || current.startsWith(`${path}/`);
  }
</script>

<div class="app-shell">
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="brand-initial">{brandInitial}</span>
      <span class="brand-name">{brand}</span>
    </div>

    <nav class="sidebar-nav" aria-label="Main navigation">
      {#each navItems as item}
        {@const Icon = item.icon}
        <a href={item.path} class="nav-link" class:active={isActive(item.path)}>
          <Icon size={20} />
          {item.name}
        </a>
      {/each}
    </nav>

    {#if footerSlot}
      <div class="sidebar-extra">
        {@render footerSlot()}
      </div>
    {/if}

    <div class="sidebar-footer">
      {#if userName}
        <div class="user-meta">
          <p class="user-name">{userName}</p>
          {#if userRole}
            <p class="user-role">{userRole}</p>
          {/if}
        </div>
      {/if}
      <button type="button" class="logout-btn" onclick={onlogout}>
        <LogOut size={18} />
        Sign out
      </button>
    </div>
  </aside>

  <header class="mobile-header">
    <button type="button" class="menu-btn" onclick={() => (mobileMenuOpen = true)} aria-label="Open menu">
      <Menu size={24} />
    </button>
    <span class="brand-name mobile">{brand}</span>
    <button type="button" class="menu-btn logout-mobile" onclick={onlogout} aria-label="Sign out">
      <LogOut size={20} />
    </button>
  </header>

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
        <span class="brand-name">{brand}</span>
        <button type="button" class="menu-btn" onclick={() => (mobileMenuOpen = false)} aria-label="Close menu">
          <X size={24} />
        </button>
      </div>
      <nav class="mobile-nav">
        {#each navItems as item}
          {@const Icon = item.icon}
          <a
            href={item.path}
            class="mobile-nav-link"
            class:active={isActive(item.path)}
            onclick={() => (mobileMenuOpen = false)}
          >
            <Icon size={20} />
            {item.name}
          </a>
        {/each}
      </nav>
      <button type="button" class="mobile-logout-btn" onclick={onlogout}>
        <LogOut size={20} />
        Sign out
      </button>
    </div>
  {/if}

  <main class="main-content">
    {@render children()}
  </main>
</div>

<style>
  .app-shell {
    display: flex;
    min-height: 100vh;
    background: var(--color-bg);
  }

  .sidebar {
    width: var(--sidebar-width);
    background: var(--color-primary);
    color: white;
    display: flex;
    flex-direction: column;
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 100;
  }

  @media (max-width: 1024px) {
    .sidebar { transform: translateX(-100%); }
  }

  .sidebar-header {
    padding: 1.75rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .brand-initial {
    width: 36px;
    height: 36px;
    background: var(--color-accent);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1rem;
  }

  .brand-name {
    font-weight: 700;
    font-size: 1.0625rem;
    color: white;
  }

  .brand-name.mobile {
    color: var(--color-primary);
    font-size: 1rem;
  }

  .sidebar-nav {
    flex: 1;
    padding: 0 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    color: rgba(255, 255, 255, 0.7);
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: 0.875rem;
    text-decoration: none;
    transition: background 0.2s, color 0.2s;
  }

  .nav-link:hover,
  .nav-link.active {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .sidebar-extra {
    padding: 0 1rem 1rem;
  }

  .sidebar-footer {
    padding: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .user-meta {
    margin-bottom: 0.75rem;
  }

  .user-name {
    font-weight: 600;
    font-size: 0.875rem;
  }

  .user-role {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.55);
  }

  .logout-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.625rem;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: var(--radius-md);
    color: white;
    font-weight: 600;
    font-size: 0.875rem;
  }

  .logout-btn:hover {
    background: var(--color-accent);
    border-color: var(--color-accent);
  }

  .mobile-header {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: var(--header-height);
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    padding: 0 1rem;
    align-items: center;
    justify-content: space-between;
    z-index: 90;
  }

  @media (max-width: 1024px) {
    .mobile-header { display: flex; }
  }

  .menu-btn {
    background: none;
    border: none;
    color: var(--color-primary);
    padding: 0.5rem;
  }

  .logout-mobile {
    color: var(--color-text-muted);
  }

  .mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: 200;
  }

  .mobile-menu {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: var(--sidebar-width);
    background: var(--color-surface);
    z-index: 201;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-lg);
  }

  .mobile-menu-header {
    padding: 1rem 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--color-border);
  }

  .mobile-menu-header .brand-name {
    color: var(--color-primary);
  }

  .mobile-nav {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
  }

  .mobile-nav-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1rem;
    border-radius: var(--radius-md);
    color: var(--color-text);
    font-weight: 500;
    text-decoration: none;
  }

  .mobile-nav-link:hover,
  .mobile-nav-link.active {
    background: var(--color-bg);
    color: var(--color-accent);
  }

  .mobile-logout-btn {
    margin: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1rem;
    background: none;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    color: var(--color-error);
    font-weight: 600;
  }

  .main-content {
    flex: 1;
    margin-left: var(--sidebar-width);
    padding: 2rem;
    min-height: 100vh;
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
  }

  @media (max-width: 1024px) {
    .main-content {
      margin-left: 0;
      padding: calc(var(--header-height) + 1rem) 0.875rem 2rem;
    }
  }
</style>
