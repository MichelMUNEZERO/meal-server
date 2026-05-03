<script>
  let { title, children } = $props();
</script>

<div class="card fade-in">
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
    box-shadow: var(--shadow-md);
    padding: 1.5rem;
    border: 1px solid var(--color-border);
    height: 100%;
  }

  .card-title {
    font-size: 1.125rem;
    margin-bottom: 1.25rem;
    color: var(--color-text);
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 0.75rem;
  }
</style>
