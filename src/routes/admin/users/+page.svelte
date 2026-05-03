<script>
  import { mockUsers } from '$lib/services/mock-data.js';
  import Card from '$lib/components/Card.svelte';
  import { Search, Plus, MoreVertical, Edit2, Trash2, UserPlus } from 'lucide-svelte';

  let searchQuery = $state('');
  
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
  <div class="header">
    <div>
      <h1>User Management</h1>
      <p>Manage member accounts, roles, and access status.</p>
    </div>
    <button class="btn btn-primary">
      <UserPlus size={18} />
      Add New User
    </button>
  </div>

  <Card>
    <div class="table-controls">
      <div class="search-box">
        <Search size={18} />
        <input 
          type="text" 
          placeholder="Search by name or email..." 
          bind:value={searchQuery}
        />
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Status</th>
            <th>Meal Plan</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredUsers as user}
            <tr>
              <td>
                <div class="user-cell">
                  <div class="user-avatar">{user.name.charAt(0)}</div>
                  <div>
                    <p class="user-name">{user.name}</p>
                    <p class="user-email">{user.email}</p>
                  </div>
                </div>
              </td>
              <td>
                <span class="status-badge {user.status.toLowerCase()}">{user.status}</span>
              </td>
              <td>
                <span class="plan-tag">{user.plan}</span>
              </td>
              <td>
                <div class="actions">
                  <button class="icon-btn"><Edit2 size={16} /></button>
                  <button class="icon-btn danger"><Trash2 size={16} /></button>
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
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
    gap: 1.5rem;
  }

  @media (max-width: 640px) {
    .header {
      flex-direction: column;
      align-items: flex-start;
      margin-bottom: 2rem;
    }

    .header .btn {
      width: 100%;
      justify-content: center;
    }
  }

  .table-controls {
    margin-bottom: 1.5rem;
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1rem;
    background-color: var(--color-bg);
    border-radius: 8px;
    max-width: 400px;
    color: var(--color-text-muted);
  }

  @media (max-width: 640px) {
    .search-box {
      max-width: none;
    }
  }

  .search-box input {
    background: none;
    border: none;
    flex: 1;
    font-size: 0.875rem;
    color: var(--color-text);
  }

  .search-box input:focus { outline: none; }

  .table-container { overflow-x: auto; }

  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 1rem; font-size: 0.75rem; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase; border-bottom: 1px solid var(--color-bg); white-space: nowrap; }
  td { padding: 1rem; border-bottom: 1px solid var(--color-bg); }

  @media (max-width: 640px) {
    th, td { padding: 0.75rem; }
  }

  .user-cell { display: flex; align-items: center; gap: 1rem; }
  .user-avatar { width: 36px; height: 36px; border-radius: 50%; background-color: var(--color-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.875rem; }
  .user-name { font-weight: 600; font-size: 0.9375rem; }
  .user-email { font-size: 0.75rem; color: var(--color-text-muted); }

  .status-badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; }
  .status-badge.active { background-color: rgba(34, 197, 94, 0.1); color: var(--color-success); }
  .status-badge.inactive { background-color: #F1F5F9; color: #64748B; }

  .plan-tag { font-weight: 600; color: var(--color-primary); font-size: 0.875rem; }

  .actions { display: flex; gap: 0.5rem; }
  .icon-btn { padding: 0.5rem; background: none; border: none; color: var(--color-text-muted); border-radius: 6px; }
  .icon-btn:hover { background-color: var(--color-bg); color: var(--color-primary); }
  .icon-btn.danger:hover { color: var(--color-error); }
</style>
