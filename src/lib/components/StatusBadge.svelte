<script>
  let { status = 'Active', variant } = $props();

  const resolved = $derived.by(() => {
    const normalized = status.toLowerCase();
    const resolvedVariant =
      variant ||
      (normalized === 'active' ||
      normalized === 'present' ||
      normalized === 'granted' ||
      normalized === 'success'
        ? 'success'
        : normalized === 'inactive' || normalized === 'denied' || normalized === 'error'
          ? 'error'
          : 'warning');
    return { normalized, resolvedVariant };
  });
</script>

<span class="status-badge {resolved.resolvedVariant}">
  <span class="dot" aria-hidden="true"></span>
  {status}
</span>

<style>
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .success {
    background: rgba(22, 163, 74, 0.1);
    color: var(--color-success);
  }

  .error {
    background: rgba(220, 38, 38, 0.1);
    color: var(--color-error);
  }

  .warning {
    background: rgba(217, 119, 6, 0.1);
    color: var(--color-warning);
  }
</style>
