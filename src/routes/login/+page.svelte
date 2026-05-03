<script>
  import { authService } from '$lib/services/auth.service.js';
  import { authStore } from '$lib/stores/auth.js';
  import { toastStore } from '$lib/stores/toast.js';
  import { goto } from '$app/navigation';
  import { LogIn, Mail, Lock, Loader2 } from 'lucide-svelte';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);

  async function handleLogin(e) {
    e.preventDefault();
    if (!email || !password) {
      toastStore.error('Please fill in all fields');
      return;
    }

    loading = true;
    try {
      const { user, token } = await authService.login(email, password);
      authStore.login(user, token);
      toastStore.success(`Welcome back, ${user.name}!`);
      
      if (user.role === 'admin') {
        goto('/admin');
      } else if (user.role === 'scanner') {
        goto('/scanner');
      } else {
        goto('/dashboard');
      }
    } catch (err) {
      toastStore.error(err.message || 'Login failed');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Login - Meal Trackers</title>
</svelte:head>

<div class="login-container">
  <div class="login-card fade-in">
    <div class="logo">
      <div class="logo-icon">
        <LogIn size={32} />
      </div>
      <h1>Meal Trackers</h1>
      <p>Sign in to your account</p>
    </div>

    <form onsubmit={handleLogin}>
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

      <div class="form-group">
        <div class="label-row">
          <label for="password" class="label">Password</label>
          <a href="/forgot-password" class="forgot-link">Forgot password?</a>
        </div>
        <div class="input-wrapper">
          <Lock class="input-icon" size={18} />
          <input 
            type="password" 
            id="password" 
            class="input" 
            bind:value={password} 
            placeholder="••••••••"
            required
          />
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
        {#if loading}
          <Loader2 class="animate-spin" size={20} />
          Logging in...
        {:else}
          Sign In
        {/if}
      </button>
    </form>

    <div class="demo-hints">
      <p><strong>Demo Access:</strong></p>
      <p>User: <code>michel@example.com</code> / <code>password</code></p>
      <p>Admin: <code>admin@trackers.com</code> / <code>Mich540el12!</code></p>
      <p>Scanner: <code>scanner@trackers.com</code> / <code>scanner123</code></p>
    </div>
  </div>
</div>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background-color: var(--color-bg);
    background-image: radial-gradient(circle at 10% 20%, rgba(26, 42, 58, 0.03) 0%, rgba(26, 42, 58, 0) 90%),
                      radial-gradient(circle at 90% 80%, rgba(229, 77, 56, 0.03) 0%, rgba(229, 77, 56, 0) 90%);
  }

  .login-card {
    background-color: var(--color-surface);
    width: 100%;
    max-width: 440px;
    padding: 3.5rem 2.5rem;
    border-radius: var(--radius-lg);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(26, 42, 58, 0.05);
  }

  .logo {
    text-align: center;
    margin-bottom: 3rem;
  }

  .logo-icon {
    display: inline-flex;
    padding: 1.25rem;
    background-color: var(--color-primary);
    color: white;
    border-radius: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 20px rgba(26, 42, 58, 0.2);
  }

  .logo h1 {
    font-size: 1.75rem;
    margin-bottom: 0.5rem;
    letter-spacing: -0.03em;
  }

  .logo p {
    color: var(--color-text-muted);
    font-size: 0.9375rem;
  }

  .form-group {
    margin-bottom: 1.75rem;
  }

  .label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .forgot-link {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--color-accent);
  }

  .input-wrapper {
    position: relative;
  }

  .input-icon {
    position: absolute;
    left: 1.25rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-muted);
    opacity: 0.5;
  }

  .input {
    padding-left: 3.25rem;
    height: 3.5rem;
    font-family: inherit;
  }

  .btn-block {
    width: 100%;
    margin-top: 1.5rem;
    height: 3.5rem;
  }

  .demo-hints {
    margin-top: 3rem;
    padding: 1.25rem;
    background-color: #F8FAFC;
    border-radius: var(--radius-md);
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    line-height: 1.8;
    border: 1px dashed var(--color-border);
  }

  .demo-hints code {
    background-color: white;
    padding: 0.125rem 0.375rem;
    border-radius: 4px;
    color: var(--color-primary);
    font-weight: 600;
    border: 1px solid var(--color-border);
  }

  @media (max-width: 480px) {
    .login-card {
      padding: 2.5rem 1.5rem;
    }

    .logo h1 {
      font-size: 1.5rem;
    }

    .logo {
      margin-bottom: 2rem;
    }

    .demo-hints {
      margin-top: 2rem;
      padding: 1rem;
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
