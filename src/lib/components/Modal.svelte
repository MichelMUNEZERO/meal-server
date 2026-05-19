<script>
  import { X } from 'lucide-svelte';

  let {
    open = $bindable(false),
    title = '',
    children,
    onclose
  } = $props();

  function close() {
    open = false;
    onclose?.();
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') close();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div class="modal-backdrop">
    <div
      class="overlay"
      onclick={close}
      onkeydown={(e) => e.key === 'Enter' && close()}
      role="button"
      tabindex="0"
      aria-label="Close dialog"
    ></div>
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div class="modal-header">
        <h2 id="modal-title">{title}</h2>
        <button type="button" class="close-btn" onclick={close} aria-label="Close">
          <X size={20} />
        </button>
      </div>
      <div class="modal-body">
        {@render children()}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1000;
  }

  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(4px);
    z-index: 1000;
  }

  .modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(480px, calc(100vw - 2rem));
    max-height: calc(100vh - 2rem);
    overflow-y: auto;
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    z-index: 1001;
    border: 1px solid var(--color-border);
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .modal-header h2 {
    font-size: 1.125rem;
  }

  .close-btn {
    background: none;
    border: none;
    color: var(--color-text-muted);
    padding: 0.25rem;
    border-radius: var(--radius-sm);
  }

  .close-btn:hover {
    background: var(--color-bg);
    color: var(--color-text);
  }

  .modal-body {
    padding: 1.5rem;
  }
</style>
