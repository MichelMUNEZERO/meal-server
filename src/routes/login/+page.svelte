<script>
  import { authService } from '$lib/services/auth.service.js';
  import { authStore } from '$lib/stores/auth.js';
  import { toastStore } from '$lib/stores/toast.js';
  import PasswordField from '$lib/components/PasswordField.svelte';
  import { goto } from '$app/navigation';
  import { LogIn, Mail, Loader2, ArrowLeft } from 'lucide-svelte';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);

  async function handleLogin(e) {
    e.preventDefault();
    if (!email.trim() || !password) {
      toastStore.error('Please enter your email and password');
      return;
    }

    loading = true;
    try {
      const { user, token } = await authService.login(email.trim(), password);
      authStore.login(user, token);
      toastStore.success(`Welcome back, ${user.name}`);

      if (user.role === 'admin') goto('/admin');
      else if (user.role === 'scanner') goto('/scanner');
      else goto('/dashboard');
    } catch (err) {
      toastStore.error(err.message || 'Login failed');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Sign in — Meal Trackers</title>
</svelte:head>

<div class="auth-page">
  <div class="auth-card">
    <a href="/" class="back-home">
      <ArrowLeft size={16} />
      Back to home
    </a>

    <div class="auth-brand">
      <div class="logo-icon" aria-hidden="true">
        <LogIn size={28} />
      </div>
      <h1>Sign in</h1>
      <p>Enter your email and password to continue.</p>
    </div>

    <form class="auth-form" onsubmit={handleLogin}>
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
            autocomplete="email"
            required
          />
        </div>
      </div>

      <div class="field">
        <div class="field-label-row">
          <span class="label-spacer"></span>
          <a href="/forgot-password" class="link-sm">Forgot password?</a>
        </div>
        <PasswordField
          id="password"
          label="Password"
          bind:value={password}
          placeholder="Your password"
          autocomplete="current-password"
          required
        />
      </div>

      <button type="submit" class="btn btn-primary submit-btn" disabled={loading}>
        {#if loading}
          <span class="spin"><Loader2 size={18} /></span>
          Signing in…
        {:else}
          Sign in
        {/if}
      </button>
    </form>

    {#if import.meta.env.DEV}
      <p class="dev-note">
        Dev tip: mock accounts are listed in the project README.
      </p>
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
    background: linear-gradient(160deg, var(--color-bg) 0%, #e2e8f0 100%);
  }

  .auth-card {
    width: 100%;
    max-width: 420px;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 2.5rem 2rem;
    box-shadow: var(--shadow-lg);
  }

  .back-home {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 600;
    margin-bottom: 1.25rem;
    color: var(--color-text-muted);
    text-decoration: none;
  }

  .back-home:hover {
    color: var(--color-accent);
  }

  .auth-brand {
    text-align: center;
    margin-bottom: 2rem;
  }

  .logo-icon {
    display: inline-flex;
    padding: 0.875rem;
    background: var(--color-primary);
    color: white;
    border-radius: var(--radius-md);
    margin-bottom: 1rem;
  }

  .auth-brand h1 {
    font-size: 1.5rem;
    margin-bottom: 0.375rem;
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

  .field-label-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: -0.25rem;
  }

  .link-sm {
    font-size: 0.8125rem;
    font-weight: 600;
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
    pointer-events: none;
  }

  .input-wrap .input {
    padding-left: 2.75rem;
    width: 100%;
  }

  .submit-btn {
    width: 100%;
    margin-top: 0.5rem;
    padding: 0.75rem;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .dev-note {
    margin-top: 1.5rem;
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    color: var(--color-text-muted);
    background: var(--color-bg);
    border-radius: var(--radius-md);
    text-align: center;
  }
</style>
