<script>
  import { onMount } from 'svelte';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import { authStore } from '$lib/stores/auth.js';
  import Card from '$lib/components/Card.svelte';
  import { Search, Filter, Download, ChevronLeft, ChevronRight } from 'lucide-svelte';

  let history = $state([]);
  let loading = $state(true);
  let searchQuery = $state('');

  onMount(async () => {
    try {
      history = await attendanceService.getHistory($authStore.user.id);
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  });

  const filteredHistory = $derived(
    history.filter(item => 
      item.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.date.includes(searchQuery)
    )
  );
</script>

<svelte:head>
  <title>History - Meal Trackers</title>
</svelte:head>

<div class="history-page fade-in">
  <div class="header">
    <h1>Attendance History</h1>
    <p>View your past meal check-ins and activity.</p>
  </div>

  <Card>
    <div class="table-controls">
      <div class="search-wrapper">
        <span class="search-icon">
          <Search size={18} />
        </span>
        <input 
          type="text" 
          placeholder="Search by date or meal type..." 
          class="input"
          bind:value={searchQuery}
        />
      </div>
      <div class="action-buttons">
        <button class="btn btn-outline">
          <Filter size={18} />
          Filter
        </button>
        <button class="btn btn-outline">
          <Download size={18} />
          Export
        </button>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Meal Type</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {#if loading}
            {#each Array(3) as _}
              <tr class="skeleton-row">
                <td><div class="skeleton"></div></td>
                <td><div class="skeleton"></div></td>
                <td><div class="skeleton"></div></td>
                <td><div class="skeleton"></div></td>
              </tr>
            {/each}
          {:else if filteredHistory.length === 0}
            <tr>
              <td colspan="4" class="empty-state">No records found.</td>
            </tr>
          {:else}
            {#each filteredHistory as item}
              <tr>
                <td>{new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</td>
                <td>
                  <span class="meal-type">{item.type}</span>
                </td>
                <td>{item.time}</td>
                <td>
                  <span class="status-badge success">Present</span>
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <p class="pagination-info">Showing {filteredHistory.length} records</p>
      <div class="pagination-btns">
        <button class="btn btn-outline btn-sm" disabled>
          <ChevronLeft size={16} />
        </button>
        <button class="btn btn-outline btn-sm" disabled>
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  </Card>
</div>

<style>
  .header {
    margin-bottom: 2rem;
  }

  .table-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  @media (max-width: 640px) {
    .table-controls {
      flex-direction: column;
      align-items: stretch;
    }
  }

  .search-wrapper {
    position: relative;
    flex: 1;
    max-width: 400px;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-muted);
  }

  .search-wrapper .input {
    padding-left: 2.75rem;
  }

  .action-buttons {
    display: flex;
    gap: 0.75rem;
  }

  .table-container {
    overflow-x: auto;
    margin-bottom: 1.5rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
  }

  th {
    padding: 1rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--color-text-muted);
    border-bottom: 2px solid var(--color-bg);
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid var(--color-bg);
    font-size: 0.875rem;
  }

  .meal-type {
    font-weight: 600;
    color: var(--color-primary);
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .status-badge.success {
    background-color: rgba(34, 197, 94, 0.1);
    color: var(--color-success);
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--color-text-muted);
  }

  .pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid var(--color-bg);
  }

  .pagination-info {
    font-size: 0.875rem;
    color: var(--color-text-muted);
  }

  .pagination-btns {
    display: flex;
    gap: 0.5rem;
  }

  .btn-sm {
    padding: 0.4rem;
  }

  /* Skeleton loading */
  .skeleton {
    height: 1rem;
    background-color: var(--color-bg);
    border-radius: 4px;
    animation: pulse 1.5s infinite ease-in-out;
  }

  @keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
  }
</style>
