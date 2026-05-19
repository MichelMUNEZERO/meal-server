<script>
  import { onMount } from 'svelte';
  import * as XLSX from 'xlsx';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import { authStore } from '$lib/stores/auth.js';
  import Card from '$lib/components/Card.svelte';
  import Pagination from '$lib/components/Pagination.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Search, Download } from 'lucide-svelte';
  import { paginate } from '$lib/utils/helpers.js';
  import { PAGINATION_DEFAULT_SIZE } from '$lib/utils/constants.js';

  let history = $state([]);
  let loading = $state(true);
  let searchQuery = $state('');
  let mealFilter = $state('all');
  let page = $state(1);

  onMount(async () => {
    try {
      // Backend integration point
      history = await attendanceService.getHistory($authStore.user?.id);
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  });

  const filtered = $derived(
    history.filter((item) => {
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        item.type.toLowerCase().includes(q) || item.date.includes(searchQuery);
      const matchesMeal = mealFilter === 'all' || item.type === mealFilter;
      return matchesSearch && matchesMeal;
    })
  );

  const paged = $derived(paginate(filtered, page, PAGINATION_DEFAULT_SIZE));

  $effect(() => {
    if (page > paged.totalPages) page = paged.totalPages;
  });

  function exportCsv() {
    const worksheet = XLSX.utils.json_to_sheet(filtered);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'History');
    const date = new Date().toISOString().split('T')[0];
    XLSX.writeFile(workbook, `My_Attendance_${date}.xlsx`);
  }
</script>

<svelte:head>
  <title>History — Meal Trackers</title>
</svelte:head>

<div class="history-page fade-in">
  <header class="page-header">
    <h1>Attendance history</h1>
    <p>Your past meal check-ins.</p>
  </header>

  <Card>
    <div class="toolbar">
      <div class="search-wrap">
        <Search size={18} />
        <input
          type="search"
          class="input"
          placeholder="Search date or meal…"
          bind:value={searchQuery}
        />
      </div>
      <select class="input filter-select" bind:value={mealFilter}>
        <option value="all">All meals</option>
        <option value="Breakfast">Breakfast</option>
        <option value="Lunch">Lunch</option>
        <option value="Dinner">Dinner</option>
      </select>
      <button type="button" class="btn btn-outline" onclick={exportCsv} disabled={!filtered.length}>
        <Download size={18} />
        Export
      </button>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Meal</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {#if loading}
            {#each Array(3) as _}
              <tr><td colspan="4"><div class="skeleton"></div></td></tr>
            {/each}
          {:else if !paged.items.length}
            <tr><td colspan="4" class="empty">No records found.</td></tr>
          {:else}
            {#each paged.items as item}
              <tr>
                <td>{new Date(item.date).toLocaleDateString(undefined, { dateStyle: 'medium' })}</td>
                <td>{item.type}</td>
                <td>{item.time}</td>
                <td><StatusBadge status={item.status} /></td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>

    <Pagination
      bind:page
      totalPages={paged.totalPages}
      total={paged.total}
      start={paged.start}
      end={paged.end}
    />
  </Card>
</div>

<style>
  .history-page {
    max-width: 960px;
    margin: 0 auto;
  }

  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
  }

  .search-wrap {
    flex: 1;
    min-width: 200px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
  }

  .search-wrap .input {
    border: none;
    padding-left: 0;
    box-shadow: none;
  }

  .search-wrap .input:focus {
    box-shadow: none;
  }

  .filter-select {
    width: auto;
    min-width: 140px;
  }

  .table-wrap {
    overflow-x: auto;
    margin-bottom: 0.5rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th {
    text-align: left;
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-text-muted);
    border-bottom: 1px solid var(--color-border);
  }

  td {
    padding: 0.875rem 1rem;
    border-bottom: 1px solid var(--color-border);
    font-size: 0.875rem;
  }

  .skeleton {
    height: 1rem;
    background: var(--color-bg);
    border-radius: 4px;
    animation: pulse 1.2s ease infinite;
  }

  .empty {
    text-align: center;
    padding: 2rem;
    color: var(--color-text-muted);
  }

  @keyframes pulse {
    50% { opacity: 0.5; }
  }
</style>
