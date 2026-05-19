<script>
  /**
   * Reusable password input with a show/hide toggle.
   * Usage: bind:value={password} and pass id + label for accessibility.
   */
  import { Lock, Eye, EyeOff } from 'lucide-svelte';

  let {
    id,
    label = '',
    value = $bindable(''),
    placeholder = '',
    autocomplete = 'current-password',
    required = false,
    minlength
  } = $props();

  // When true, the user can read what they typed (type="text" instead of "password")
  let showPassword = $state(false);
</script>

<div class="password-field">
  {#if label}
    <label for={id} class="label">{label}</label>
  {/if}

  <div class="input-wrap">
    <Lock size={18} class="field-icon" aria-hidden="true" />

    <input
      {id}
      type={showPassword ? 'text' : 'password'}
      class="input"
      bind:value
      {placeholder}
      {autocomplete}
      {required}
      {minlength}
    />

    <button
      type="button"
      class="toggle-btn"
      onclick={() => (showPassword = !showPassword)}
      aria-label={showPassword ? 'Hide password' : 'Show password'}
      aria-pressed={showPassword}
    >
      {#if showPassword}
        <EyeOff size={18} />
      {:else}
        <Eye size={18} />
      {/if}
    </button>
  </div>
</div>

<style>
  .password-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
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

  .input {
    padding-left: 2.75rem;
    padding-right: 2.75rem;
  }

  .toggle-btn {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    border: none;
    background: transparent;
    color: var(--color-text-muted);
    border-radius: var(--radius-sm);
  }

  .toggle-btn:hover {
    color: var(--color-accent);
    background: var(--color-bg);
  }
</style>
