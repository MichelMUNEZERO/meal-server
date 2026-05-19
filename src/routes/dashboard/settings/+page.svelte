<script>
  import { authStore } from '$lib/stores/auth.js';
  import { usersService } from '$lib/services/users.service.js';
  import { toastStore } from '$lib/stores/toast.js';
  import { isStrongPassword } from '$lib/utils/helpers.js';
  import Card from '$lib/components/Card.svelte';
  import { Lock, Mail, User, Loader2 } from 'lucide-svelte';

  let currentPassword = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let loading = $state(false);

  async function handleChangePassword(e) {
    e.preventDefault();

    if (!isStrongPassword(newPassword)) {
      toastStore.error('New password must be at least 8 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      toastStore.error('Passwords do not match');
      return;
    }

    loading = true;
    try {
      // Backend integration point — authenticated password change
      await usersService.changePassword(currentPassword, newPassword);
      toastStore.success('Password updated successfully');
      currentPassword = '';
      newPassword = '';
      confirmPassword = '';
    } catch (err) {
      toastStore.error(err.message || 'Could not update password');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Account settings — Meal Trackers</title>
</svelte:head>

<div class="settings-page fade-in">
  <header class="page-header">
    <h1>Account settings</h1>
    <p>Manage your profile and security.</p>
  </header>

  <div class="grid">
    <Card title="Profile">
      <div class="profile-row">
        <User size={18} />
        <div>
          <span class="meta-label">Name</span>
          <p>{$authStore.user?.name}</p>
        </div>
      </div>
      <div class="profile-row">
        <Mail size={18} />
        <div>
          <span class="meta-label">Email</span>
          <p>{$authStore.user?.email}</p>
        </div>
      </div>
    </Card>

    <Card title="Change password">
      <form class="password-form" onsubmit={handleChangePassword}>
        <div class="field">
          <label for="current" class="label">Current password</label>
          <input
            id="current"
            type="password"
            class="input"
            bind:value={currentPassword}
            autocomplete="current-password"
            required
          />
        </div>
        <div class="field">
          <label for="new" class="label">New password</label>
          <input
            id="new"
            type="password"
            class="input"
            bind:value={newPassword}
            minlength="8"
            autocomplete="new-password"
            required
          />
        </div>
        <div class="field">
          <label for="confirm" class="label">Confirm new password</label>
          <input
            id="confirm"
            type="password"
            class="input"
            bind:value={confirmPassword}
            minlength="8"
            autocomplete="new-password"
            required
          />
        </div>
        <button type="submit" class="btn btn-primary" disabled={loading}>
          {#if loading}
            <span class="spin"><Loader2 size={18} /></span>
            Saving…
          {:else}
            <Lock size={18} />
            Update password
          {/if}
        </button>
      </form>
    </Card>
  </div>
</div>

<style>
  .settings-page {
    max-width: 800px;
    margin: 0 auto;
  }

  .grid {
    display: grid;
    gap: 1.5rem;
  }

  .profile-row {
    display: flex;
    gap: 1rem;
    padding: 0.75rem 0;
    color: var(--color-text-muted);
  }

  .profile-row:not(:last-child) {
    border-bottom: 1px solid var(--color-border);
  }

  .profile-row p {
    color: var(--color-text);
    font-weight: 600;
  }

  .meta-label {
    display: block;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.125rem;
  }

  .password-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
