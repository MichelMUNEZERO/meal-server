<script>
  let { title, class: className = '', children } = $props();
</script>

<div class="card fade-in {className}">
  {#if title}
    <h3 class="card-title">{title}</h3>
  {/if}
  <div class="card-content">
    {@render children()}
  </div>
</div>

<style>
  .card {
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: 1.5rem;
    border: 1px solid var(--color-border);
  }

  .card-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text);
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--color-border);
  }
</style>
