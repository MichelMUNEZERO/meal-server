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
      const result = await usersService.adminSendPasswordReset(user.id);
      toastStore.success(`Reset email sent to ${result.email || user.email}`);
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

<div class="admin-content fade-in">
  <header class="page-header page-header-row">
    <div>
      <h1>User management</h1>
      <p>Manage members, status, and password resets.</p>
    </div>
    <div class="page-actions">
      <button type="button" class="btn btn-primary" disabled title="Available after API integration">
        <UserPlus size={18} />
        Add user
      </button>
    </div>
  </header>

  <Card>
    <div class="data-toolbar">
      <div class="search-field">
        <Search size={18} />
        <input type="search" placeholder="Search name or email…" bind:value={searchQuery} />
      </div>
      <span class="toolbar-meta">{filteredUsers.length} users</span>
    </div>

    {#if loading}
      <p class="data-empty">Loading users…</p>
    {:else if !filteredUsers.length}
      <p class="data-empty">No users match your search.</p>
    {:else}
      <!-- Mobile: stacked cards -->
      <ul class="data-cards">
        {#each filteredUsers as user}
          <li class="data-card">
            <div class="data-card-head">
              <div>
                <p class="data-card-title">{user.name}</p>
                <p class="data-card-sub">{user.email}</p>
              </div>
              <StatusBadge status={user.status} />
            </div>
            <div class="data-card-row">
              <span>Plan: <strong>{user.plan}</strong></span>
            </div>
            <div class="data-card-actions">
              <button type="button" class="btn btn-outline btn-sm" onclick={() => openEdit(user)}>
                <Edit2 size={16} />
                Edit
              </button>
              <button
                type="button"
                class="btn btn-primary btn-sm"
                onclick={() => sendPasswordReset(user)}
                disabled={resetLoading === user.id}
              >
                {#if resetLoading === user.id}
                  <Loader2 size={16} class="spin" />
                {:else}
                  <KeyRound size={16} />
                {/if}
                Reset password
              </button>
            </div>
          </li>
        {/each}
      </ul>

      <!-- Desktop: table -->
      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Member</th>
              <th>Status</th>
              <th>Plan</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredUsers as user}
              <tr>
                <td>
                  <p class="cell-title">{user.name}</p>
                  <p class="cell-sub">{user.email}</p>
                </td>
                <td><StatusBadge status={user.status} /></td>
                <td><span class="plan-tag">{user.plan}</span></td>
                <td>
                  <div class="table-actions">
                    <button type="button" class="btn btn-ghost btn-sm" onclick={() => openEdit(user)} aria-label="Edit">
                      <Edit2 size={16} />
                    </button>
                    <button
                      type="button"
                      class="btn btn-outline btn-sm"
                      onclick={() => sendPasswordReset(user)}
                      disabled={resetLoading === user.id}
                    >
                      {#if resetLoading === user.id}
                        <Loader2 size={16} class="spin" />
                      {:else}
                        <KeyRound size={16} />
                      {/if}
                      Reset
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
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
  .cell-title {
    font-weight: 600;
    color: var(--color-primary);
  }

  .cell-sub {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
  }

  .plan-tag {
    font-weight: 600;
    font-size: 0.875rem;
  }

  .table-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
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

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }
</style>
