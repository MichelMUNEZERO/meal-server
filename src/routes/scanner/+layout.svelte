<script>
  import { authStore } from "$lib/stores/auth.js";
  import { scannerSession } from "$lib/stores/scannerSession.js";
  import { goto } from "$app/navigation";
  import { LogOut, Scan, Users } from "lucide-svelte";
  import { onMount } from "svelte";
  import Toast from "$lib/components/Toast.svelte";

  let { children } = $props();

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

  <!-- Premium Top Navigation Bar for Scanner -->
  <header class="scanner-header">
    <div class="logo-section">
      <div class="logo-icon">
        <Scan size={20} />
      </div>
      <span>Meal Scanner</span>
    </div>

    <!-- Centralized Scan Summary Badge -->
    <div class="header-center">
      <div class="scan-summary">
        <Users size={18} class="summary-icon" />
        <span class="summary-count">{$scannerSession.totalScans}</span>
        <span class="summary-label">Scanned</span>
      </div>
    </div>

    <!-- User Profile & Actions -->
    <div class="user-actions">
      <div class="scanner-user">
        <p class="user-name">{$authStore.user?.name || "Scanner Agent"}</p>
        <p class="scanner-role">Scanner Access</p>
      </div>
      <button class="logout-btn" onclick={logout} aria-label="Sign Out">
        <LogOut size={18} />
        <span class="btn-text">Sign Out</span>
      </button>
    </div>
  </header>

  <!-- Dynamic Content Area -->
  <main class="scanner-content">
    {@render children()}
  </main>
</div>

<style>
  /* Layout Shell */
  .scanner-shell {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: var(--color-bg);
  }

  /* Premium Header Design */
  .scanner-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    height: 72px;
    background-color: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  }

  /* Mobile Responsiveness for Header */
  @media (max-width: 768px) {
    .scanner-header {
      padding: 1rem;
      height: auto;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .header-center {
      order: 3;
      width: 100%;
      justify-content: flex-start !important;
    }

    .btn-text {
      display: none;
    }
    
    .logout-btn {
      padding: 0.5rem !important;
    }
  }

  /* Logo Styling */
  .logo-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 800;
    font-size: 1.25rem;
    color: var(--color-primary);
  }

  .logo-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background-color: var(--color-accent);
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(229, 77, 56, 0.2);
  }

  /* Center Area */
  .header-center {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
  }

  /* Scan Summary Badge */
  .scan-summary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    background-color: rgba(46, 204, 113, 0.1);
    color: var(--color-success);
    border-radius: 9999px;
    font-weight: 700;
    border: 1px solid rgba(46, 204, 113, 0.2);
  }

  .summary-count {
    font-size: 1.125rem;
  }

  .summary-label {
    font-size: 0.8125rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* User Actions */
  .user-actions {
    display: flex;
    align-items: center;
    gap: 1.25rem;
  }

  .scanner-user {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .user-name {
    font-weight: 700;
    font-size: 0.9375rem;
    color: var(--color-text);
  }

  .scanner-role {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    text-transform: capitalize;
  }

  /* Logout Button */
  .logout-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: rgba(229, 77, 56, 0.05);
    color: var(--color-accent);
    border: 1px solid rgba(229, 77, 56, 0.2);
    border-radius: var(--radius-full);
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .logout-btn:hover {
    background-color: var(--color-accent);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(229, 77, 56, 0.2);
  }

  /* Main Content Area */
  .scanner-content {
    flex: 1;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  @media (max-width: 768px) {
    .scanner-content {
      padding: 1rem;
    }
  }
</style>
