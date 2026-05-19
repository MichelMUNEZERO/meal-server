<script>
  import { usersService } from '$lib/services/users.service.js';
  import { toastStore } from '$lib/stores/toast.js';
  import { isValidEmail } from '$lib/utils/helpers.js';
  import { Mail, ArrowLeft, Loader2, CheckCircle } from 'lucide-svelte';

  let email = $state('');
  let loading = $state(false);
  let success = $state(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!isValidEmail(email.trim())) {
      toastStore.error('Please enter a valid email address');
      return;
    }

    loading = true;
    try {
      // Backend integration point
      await usersService.requestPasswordReset(email.trim());
      success = true;
      toastStore.success('Check your inbox for reset instructions');
    } catch {
      toastStore.error('Could not send reset email. Try again later.');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Reset password — Meal Trackers</title>
</svelte:head>

<div class="auth-page">
  <div class="auth-card fade-in">
    {#if !success}
      <a href="/login" class="back-link">
        <ArrowLeft size={18} />
        Back to sign in
      </a>

      <div class="auth-brand align-left">
        <h1>Reset password</h1>
        <p>Enter your email and we will send you a link to choose a new password.</p>
      </div>

      <form class="auth-form" onsubmit={handleSubmit}>
        <div class="field">
          <label for="email" class="label">Email</label>
          <div class="input-wrap">
            <Mail size={18} class="field-icon" />
            <input
              id="email"
              type="email"
              class="input"
              bind:value={email}
              placeholder="you@example.com"
              required
            />
          </div>
        </div>

        <button type="submit" class="btn btn-primary submit-btn" disabled={loading}>
          {#if loading}
            <span class="spin"><Loader2 size={18} /></span>
            Sending…
          {:else}
            Send reset link
          {/if}
        </button>
      </form>
    {:else}
      <div class="success-state">
        <CheckCircle size={48} class="success-icon" />
        <h1>Check your email</h1>
        <p>
          If an account exists for <strong>{email}</strong>, you will receive password reset
          instructions shortly.
        </p>
        <a href="/login" class="btn btn-primary submit-btn">Return to sign in</a>
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

  .input-wrap {
    position: relative;
  }

  .input-wrap :global(.field-icon) {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-muted);
  }

  .input-wrap .input {
    padding-left: 2.75rem;
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
    line-height: 1.6;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
