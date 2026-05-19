<script>
  import { onMount } from 'svelte';
  import { usersService } from '$lib/services/users.service.js';
  import { toastStore } from '$lib/stores/toast.js';
  import Card from '$lib/components/Card.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Search, UserPlus, Edit2, KeyRound, Loader2 } from 'lucide-svelte';

  let users = $state([]);
  let loading = $state(true);
  let searchQuery = $state('');
  let editOpen = $state(false);
  let editUser = $state(null);
  let saving = $state(false);
  let resetLoading = $state(null);

  onMount(async () => {
    try {
      users = await usersService.getAll();
    } catch (err) {
      toastStore.error(err.message || 'Failed to load users');
    } finally {
      loading = false;
    }
  });

  const filteredUsers = $derived(
    users.filter(
      (u) =>
        u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.email.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  function openEdit(user) {
    editUser = { ...user };
    editOpen = true;
  }

  async function saveEdit() {
    if (!editUser) return;
    saving = true;
    try {
      // Backend integration point
      const updated = await usersService.update(editUser.id, {
        name: editUser.name,
        email: editUser.email,
        status: editUser.status
      });
      users = users.map((u) => (u.id === updated.id ? { ...u, ...updated } : u));
      toastStore.success('User updated');
      editOpen = false;
    } catch (err) {
      toastStore.error(err.message || 'Could not update user');
    } finally {
      saving = false;
    }
  }

  async function sendPasswordReset(user) {
    resetLoading = user.id;
    try {
      // Backend integration point — triggers reset email for this user
      const result = await usersService.adminSendPasswordReset(user.id);
      toastStore.success(`Password reset email sent to ${result.email || user.email}`);
    } catch (err) {
      toastStore.error(err.message || 'Could not send reset email');
    } finally {
      resetLoading = null;
    }
  }
</script>

<svelte:head>
  <title>Users — Admin</title>
</svelte:head>

<div class="users-page fade-in">
  <header class="page-header row">
    <div>
      <h1>User management</h1>
      <p>Manage members, status, and password resets.</p>
    </div>
    <button type="button" class="btn btn-primary" disabled title="Available after API integration">
      <UserPlus size={18} />
      Add user
    </button>
  </header>

  <Card>
    <div class="toolbar">
      <div class="search">
        <Search size={18} />
        <input type="search" placeholder="Search name or email…" bind:value={searchQuery} />
      </div>
      <span class="count">{filteredUsers.length} users</span>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Member</th>
            <th>Status</th>
            <th>Plan</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#if loading}
            <tr><td colspan="4" class="muted">Loading users…</td></tr>
          {:else if !filteredUsers.length}
            <tr><td colspan="4" class="muted">No users match your search.</td></tr>
          {:else}
            {#each filteredUsers as user}
              <tr>
                <td>
                  <p class="name">{user.name}</p>
                  <p class="email">{user.email}</p>
                </td>
                <td><StatusBadge status={user.status} /></td>
                <td><span class="plan">{user.plan}</span></td>
                <td class="actions">
                  <button type="button" class="btn btn-ghost btn-sm" onclick={() => openEdit(user)} aria-label="Edit">
                    <Edit2 size={16} />
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline btn-sm"
                    onclick={() => sendPasswordReset(user)}
                    disabled={resetLoading === user.id}
                    title="Send password reset email"
                  >
                    {#if resetLoading === user.id}
                      <Loader2 size={16} class="spin" />
                    {:else}
                      <KeyRound size={16} />
                    {/if}
                    Reset password
                  </button>
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </Card>
</div>

<Modal bind:open={editOpen} title="Edit member" onclose={() => (editUser = null)}>
  {#if editUser}
    <form class="edit-form" onsubmit={(e) => { e.preventDefault(); saveEdit(); }}>
      <div class="field">
        <label class="label" for="name">Name</label>
        <input id="name" class="input" bind:value={editUser.name} required />
      </div>
      <div class="field">
        <label class="label" for="email">Email</label>
        <input id="email" type="email" class="input" bind:value={editUser.email} required />
      </div>
      <div class="field">
        <label class="label" for="status">Status</label>
        <select id="status" class="input" bind:value={editUser.status}>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </select>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick={() => (editOpen = false)}>Cancel</button>
        <button type="submit" class="btn btn-primary" disabled={saving}>
          {#if saving}<Loader2 size={16} class="spin" />{:else}Save{/if}
        </button>
      </div>
    </form>
  {/if}
</Modal>

<style>
  .page-header.row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .search {
    flex: 1;
    min-width: 220px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .search input {
    flex: 1;
    border: none;
    padding: 0.625rem 0;
    font-size: 0.875rem;
    background: transparent;
  }

  .search input:focus {
    outline: none;
  }

  .count {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    font-weight: 600;
  }

  .table-wrap {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th {
    text-align: left;
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-text-muted);
    border-bottom: 1px solid var(--color-border);
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid var(--color-border);
    vertical-align: middle;
  }

  .name {
    font-weight: 600;
    color: var(--color-primary);
  }

  .email {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
  }

  .plan {
    font-weight: 600;
    font-size: 0.875rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .muted {
    text-align: center;
    color: var(--color-text-muted);
    padding: 2rem;
  }

  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
