<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { usersService } from '$lib/services/users.service.js';
  import { toastStore } from '$lib/stores/toast.js';
  import { isStrongPassword } from '$lib/utils/helpers.js';
  import PasswordField from '$lib/components/PasswordField.svelte';
  import { Loader2, CheckCircle, ArrowLeft } from 'lucide-svelte';

  let password = $state('');
  let confirmPassword = $state('');
  let loading = $state(false);
  let success = $state(false);
  let token = $state('');

  onMount(() => {
    token = $page.url.searchParams.get('token') || '';
    if (!token) {
      toastStore.error('Invalid or missing reset link');
    }
  });

  async function handleSubmit(e) {
    e.preventDefault();

    if (!token) {
      toastStore.error('Invalid reset link');
      return;
    }

    if (!isStrongPassword(password)) {
      toastStore.error('Password must be at least 8 characters');
      return;
    }

    if (password !== confirmPassword) {
      toastStore.error('Passwords do not match');
      return;
    }

    loading = true;
    try {
      // Backend integration point
      await usersService.resetPasswordWithToken(token, password);
      success = true;
      toastStore.success('Password updated successfully');
    } catch (err) {
      toastStore.error(err.message || 'Could not reset password');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Set new password — Meal Trackers</title>
</svelte:head>

<div class="auth-page">
  <div class="auth-card fade-in">
    {#if !success}
      <a href="/login" class="back-link">
        <ArrowLeft size={18} />
        Back to sign in
      </a>

      <div class="auth-brand align-left">
        <h1>Set new password</h1>
        <p>Choose a strong password for your account.</p>
      </div>

      <form class="auth-form" onsubmit={handleSubmit}>
        <PasswordField
          id="password"
          label="New password"
          bind:value={password}
          autocomplete="new-password"
          required
          minlength={8}
        />

        <PasswordField
          id="confirm"
          label="Confirm password"
          bind:value={confirmPassword}
          autocomplete="new-password"
          required
          minlength={8}
        />

        <button type="submit" class="btn btn-primary submit-btn" disabled={loading || !token}>
          {#if loading}
            <span class="spin"><Loader2 size={18} /></span>
            Updating…
          {:else}
            Update password
          {/if}
        </button>
      </form>
    {:else}
      <div class="success-state">
        <CheckCircle size={48} class="success-icon" />
        <h1>Password updated</h1>
        <p>You can now sign in with your new password.</p>
        <button type="button" class="btn btn-primary submit-btn" onclick={() => goto('/login')}>
          Go to sign in
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .auth-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    background: var(--color-bg);
  }

  .auth-card {
    width: 100%;
    max-width: 420px;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 2.5rem 2rem;
    box-shadow: var(--shadow-md);
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
  }

  .auth-brand.align-left {
    text-align: left;
    margin-bottom: 1.75rem;
  }

  .auth-brand h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .auth-brand p {
    color: var(--color-text-muted);
    font-size: 0.9375rem;
  }

  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .submit-btn {
    width: 100%;
    padding: 0.75rem;
  }

  .success-state {
    text-align: center;
  }

  .success-state :global(.success-icon) {
    color: var(--color-success);
    margin-bottom: 1rem;
  }

  .success-state h1 {
    font-size: 1.375rem;
    margin-bottom: 0.75rem;
  }

  .success-state p {
    color: var(--color-text-muted);
    margin-bottom: 1.5rem;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
