<script>
  import { authService } from '$lib/services/auth.service.js';
  import { toastStore } from '$lib/stores/toast.js';
  import { Mail, ArrowLeft, Loader2, CheckCircle } from 'lucide-svelte';

  let email = $state('');
  let loading = $state(false);
  let success = $state(false);

  async function handleSubmit(e) {
    e.preventDefault();
    loading = true;
    try {
      await authService.forgotPassword(email);
      success = true;
      toastStore.success('Reset link sent to your email');
    } catch (err) {
      toastStore.error('Failed to send reset link');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Forgot Password - Trackers</title>
</svelte:head>

<div class="auth-container">
  <div class="auth-card fade-in">
    {#if !success}
      <div class="header">
        <a href="/login" class="back-link">
          <ArrowLeft size={18} />
          Back to login
        </a>
        <h1>Reset Password</h1>
        <p>Enter your email and we'll send you a link to reset your password.</p>
      </div>

      <form onsubmit={handleSubmit}>
        <div class="form-group">
          <label for="email" class="label">Email Address</label>
          <div class="input-wrapper">
            <Mail class="input-icon" size={18} />
            <input 
              type="email" 
              id="email" 
              class="input" 
              bind:value={email} 
              placeholder="name@example.com"
              required
            />
          </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
          {#if loading}
            <Loader2 class="animate-spin" size={20} />
            Sending...
          {:else}
            Send Reset Link
          {/if}
        </button>
      </form>
    {:else}
      <div class="success-state fade-in">
        <div class="success-icon">
          <CheckCircle size={48} />
        </div>
        <h1>Check your email</h1>
        <p>We've sent a password reset link to <strong>{email}</strong>.</p>
        <a href="/login" class="btn btn-primary btn-block">Return to Login</a>
      </div>
    {/if}
  </div>
</div>

<style>
  .auth-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background-color: var(--color-bg);
  }

  .auth-card {
    background-color: var(--color-surface);
    width: 100%;
    max-width: 450px;
    padding: 3rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
  }

  .header {
    margin-bottom: 2rem;
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 1.5rem;
  }

  .header h1 { font-size: 1.75rem; margin-bottom: 0.75rem; }
  .header p { color: var(--color-text-muted); font-size: 0.9375rem; line-height: 1.6; }

  .form-group { margin-bottom: 1.5rem; }
  .input-wrapper { position: relative; }
  .input-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--color-text-muted); }
  .input { padding-left: 3rem; }
  .btn-block { width: 100%; margin-top: 1rem; padding: 0.75rem; }

  .success-state {
    text-align: center;
  }

  .success-icon {
    display: inline-flex;
    color: var(--color-success);
    margin-bottom: 1.5rem;
  }

  .success-state h1 { font-size: 1.75rem; margin-bottom: 1rem; }
  .success-state p { color: var(--color-text-muted); margin-bottom: 2rem; }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
