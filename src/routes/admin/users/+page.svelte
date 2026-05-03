<script>
  // Import mock data for user listing
  import { mockUsers } from '$lib/services/mock-data.js';
  // Import the reusable Card component for layout containers
  import Card from '$lib/components/Card.svelte';
  // Import required icons from lucide-svelte
  import { Search, Plus, MoreVertical, Edit2, Trash2, UserPlus, Shield, Utensils } from 'lucide-svelte';

  // State variable to track the search input
  let searchQuery = $state('');
  
  // Derived state to automatically filter users when the search query changes
  const filteredUsers = $derived(
    mockUsers.filter(u => 
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );
</script>

<svelte:head>
  <title>User Management - Trackers Admin</title>
</svelte:head>

<div class="user-management fade-in">
  <!-- Page Header Section -->
  <div class="header">
    <div class="header-text">
      <h1>User Management</h1>
      <p>Manage member accounts, roles, and access status.</p>
    </div>
    <button class="btn btn-primary shadow-hover">
      <UserPlus size={18} />
      <span>Add New User</span>
    </button>
  </div>

  <!-- Main Content Card -->
  <Card>
    <!-- Table Controls / Toolbar -->
    <div class="table-controls">
      <div class="search-box">
        <Search size={18} class="search-icon" />
        <input 
          type="text" 
          placeholder="Search by name or email..." 
          bind:value={searchQuery}
          aria-label="Search users"
        />
      </div>
      
      <!-- Optional: Add filters here if needed in the future -->
      <div class="filter-actions">
        <span class="user-count">{filteredUsers.length} Users Found</span>
      </div>
    </div>

    <!-- Responsive Table Container -->
    <div class="table-container">
      <table class="premium-table">
        <thead>
          <tr>
            <th>User Profile</th>
            <th>Account Status</th>
            <th>Meal Plan</th>
            <th class="actions-col">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredUsers as user}
            <tr class="table-row fade-in">
              <!-- User Profile Column -->
              <td>
                <div class="user-cell">
                  <!-- Generate a random color or use primary for the avatar -->
                  <div class="user-avatar" style="background-color: var(--color-primary)">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div class="user-info">
                    <p class="user-name">{user.name}</p>
                    <p class="user-email">{user.email}</p>
                  </div>
                </div>
              </td>
              
               <!-- Account Status Column -->
              <td>
                <span class="status-badge {user.status.toLowerCase()}">
                  <div class="status-dot"></div>
                  {user.status}
                </span>
              </td>
              
               <!-- Meal Plan Column -->
              <td>
                <div class="plan-wrapper">
                  <Utensils size={14} class="plan-icon" />
                  <span class="plan-tag">{user.plan}</span>
                </div>
              </td>
              
               <!-- Actions Column -->
              <td class="actions-col">
                <div class="actions">
                  <button class="icon-btn edit-btn" aria-label="Edit User" title="Edit User">
                    <Edit2 size={16} />
                  </button>
                  <button class="icon-btn danger-btn" aria-label="Delete User" title="Delete User">
                    <Trash2 size={16} />
                  </button>
                </div>
              </td>
            </tr>
          {:else}
            <!-- Empty State when no users match search -->
            <tr>
              <td colspan="4">
                <div class="empty-state">
                  <Search size={48} class="empty-icon" />
                  <h3>No users found</h3>
                  <p>Try adjusting your search query.</p>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </Card>
</div>

<style>
  /* Base Layout Styles */
  .user-management {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  /* Header Section */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
  }

  .header-text h1 {
    font-size: 2rem;
    font-weight: 800;
    color: var(--color-primary);
    margin-bottom: 0.25rem;
  }

  .header-text p {
    color: var(--color-text-muted);
    font-size: 1rem;
  }

  .shadow-hover {
    box-shadow: 0 4px 15px rgba(229, 77, 56, 0.3);
    transition: all 0.3s ease;
  }
  
  .shadow-hover:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(229, 77, 56, 0.4);
  }

  @media (max-width: 640px) {
    .header {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .header .btn {
      width: 100%;
      justify-content: center;
    }
  }

  /* Table Controls / Toolbar */
  .table-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    background-color: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-full);
    width: 100%;
    max-width: 400px;
    color: var(--color-text-muted);
    transition: all 0.2s ease;
  }

  .search-box:focus-within {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px rgba(229, 77, 56, 0.1);
  }

  .search-icon {
    color: var(--color-text-muted);
  }

  .search-box input {
    background: none;
    border: none;
    flex: 1;
    font-size: 0.875rem;
    color: var(--color-text);
  }

  .search-box input:focus { outline: none; }
  .search-box input::placeholder { color: #94A3B8; }

  .user-count {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-text-muted);
    background-color: var(--color-bg);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
  }

  @media (max-width: 640px) {
    .table-controls {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }
    .search-box {
      max-width: none;
    }
    .filter-actions {
      display: flex;
      justify-content: flex-end;
    }
  }

  /* Premium Table Styles */
  .table-container { 
    overflow-x: auto; 
    border-radius: var(--radius-md);
  }

  .premium-table { 
    width: 100%; 
    border-collapse: separate; 
    border-spacing: 0;
  }

  th { 
    text-align: left; 
    padding: 1rem 1.25rem; 
    font-size: 0.75rem; 
    font-weight: 700; 
    color: #64748B; 
    text-transform: uppercase; 
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--color-bg); 
    white-space: nowrap; 
    background-color: rgba(248, 250, 252, 0.5);
  }

  td { 
    padding: 1.25rem; 
    border-bottom: 1px solid var(--color-bg);
    vertical-align: middle;
  }

  .table-row {
    transition: background-color 0.2s ease;
  }

  .table-row:hover {
    background-color: rgba(248, 250, 252, 0.8);
  }

  @media (max-width: 640px) {
    th, td { padding: 1rem; }
  }

  /* User Profile Cell */
  .user-cell { 
    display: flex; 
    align-items: center; 
    gap: 1rem; 
  }

  .user-avatar { 
    width: 40px; 
    height: 40px; 
    border-radius: 12px; 
    color: white; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-weight: 700; 
    font-size: 1rem; 
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }

  .user-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .user-name { 
    font-weight: 700; 
    font-size: 0.9375rem; 
    color: var(--color-primary);
  }

  .user-email { 
    font-size: 0.8125rem; 
    color: var(--color-text-muted); 
  }

  /* Status Badge */
  .status-badge { 
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.875rem; 
    border-radius: 9999px; 
    font-size: 0.75rem; 
    font-weight: 700; 
    text-transform: capitalize;
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  .status-badge.active { 
    background-color: rgba(34, 197, 94, 0.1); 
    color: var(--color-success); 
  }
  
  .status-badge.active .status-dot {
    background-color: var(--color-success);
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
  }

  .status-badge.inactive { 
    background-color: #F1F5F9; 
    color: #64748B; 
  }

  .status-badge.inactive .status-dot {
    background-color: #94A3B8;
  }

  /* Meal Plan Column */
  .plan-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background-color: var(--color-bg);
    padding: 0.375rem 0.875rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
  }

  .plan-icon {
    color: var(--color-accent);
  }

  .plan-tag { 
    font-weight: 700; 
    color: var(--color-primary); 
    font-size: 0.8125rem; 
  }

  /* Actions Column */
  .actions-col {
    text-align: right;
  }

  .actions { 
    display: flex; 
    gap: 0.5rem; 
    justify-content: flex-end;
  }

  .icon-btn { 
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background-color: white; 
    border: 1px solid var(--color-border); 
    color: var(--color-text-muted); 
    border-radius: 8px; 
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .icon-btn:hover { 
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  }

  .edit-btn:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  .danger-btn:hover { 
    border-color: var(--color-error);
    color: var(--color-error);
    background-color: rgba(239, 68, 68, 0.05);
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
  }

  .empty-icon {
    color: var(--color-border);
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: 0.5rem;
  }

  .empty-state p {
    color: var(--color-text-muted);
    font-size: 0.875rem;
  }
</style>
