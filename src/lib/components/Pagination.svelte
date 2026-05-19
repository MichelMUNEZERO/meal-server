<script>
  import { ChevronLeft, ChevronRight } from 'lucide-svelte';

  let {
    page = $bindable(1),
    totalPages = 1,
    total = 0,
    start = 0,
    end = 0
  } = $props();
</script>

<div class="pagination">
  <p class="pagination-info">
    {#if total === 0}
      No records
    {:else}
      Showing {start}–{end} of {total}
    {/if}
  </p>
  <div class="pagination-btns">
    <button
      type="button"
      class="btn btn-outline btn-sm"
      disabled={page <= 1}
      onclick={() => (page = Math.max(1, page - 1))}
      aria-label="Previous page"
    >
      <ChevronLeft size={16} />
    </button>
    <span class="page-indicator">{page} / {totalPages}</span>
    <button
      type="button"
      class="btn btn-outline btn-sm"
      disabled={page >= totalPages}
      onclick={() => (page = Math.min(totalPages, page + 1))}
      aria-label="Next page"
    >
      <ChevronRight size={16} />
    </button>
  </div>
</div>

<style>
  .pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid var(--color-border);
    gap: 1rem;
    flex-wrap: wrap;
  }

  .pagination-info {
    font-size: 0.875rem;
    color: var(--color-text-muted);
  }

  .pagination-btns {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .page-indicator {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--color-text-muted);
    min-width: 3rem;
    text-align: center;
  }
</style>
