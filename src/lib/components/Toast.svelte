<script>
  import { toastStore } from '$lib/stores/toast.js';
  import { fade, fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { XCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-svelte';

  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertTriangle,
    info: Info
  };
</script>

<div class="toast-container">
  {#each $toastStore as toast (toast.id)}
    {@const Icon = icons[toast.type]}
    <div 
      class="toast toast-{toast.type}" 
      animate:flip={{ duration: 300 }}
      in:fly={{ y: 20, duration: 300 }}
      out:fade={{ duration: 200 }}
    >
      <Icon size={20} />
      <span class="message">{toast.message}</span>
      <button class="close-btn" onclick={() => toastStore.remove(toast.id)}>
        <X size={16} />
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    z-index: 9999;
    max-width: 24rem;
  }

  .toast {
    display: flex;
    align-items: center;
    padding: 1rem;
    border-radius: var(--radius-md);
    background-color: var(--color-surface);
    box-shadow: var(--shadow-lg);
    border-left: 4px solid transparent;
    gap: 0.75rem;
    animation: slideIn 0.3s ease-out;
  }

  .toast-success { border-left-color: var(--color-success); }
  .toast-error { border-left-color: var(--color-error); }
  .toast-warning { border-left-color: var(--color-accent); }
  .toast-info { border-left-color: var(--color-primary); }

  .message {
    flex: 1;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .close-btn {
    background: none;
    border: none;
    color: var(--color-text-muted);
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-btn:hover {
    color: var(--color-text);
  }

  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
</style>
