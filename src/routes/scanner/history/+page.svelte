<script>
  import { scannerSession } from '$lib/stores/scannerSession.js';
  import Card from '$lib/components/Card.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { Search, History } from 'lucide-svelte';

  let searchQuery = $state('');

  const filteredHistory = $derived(
    $scannerSession.scanHistory.filter(
      (scan) =>
        scan.user?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scan.user?.id?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  function formatTime(date) {
    return new Intl.DateTimeFormat(undefined, {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(date));
  }
</script>

<svelte:head>
  <title>Recent scanned — Scanner</title>
</svelte:head>

<div class="admin-content fade-in">
  <header class="page-header">
    <h1>Recent scanned</h1>
    <p>Real-time log of meal check-ins this session.</p>
  </header>

  <Card>
    <div class="data-toolbar">
      <div class="search-field">
        <Search size={18} />
        <input
          type="search"
          placeholder="Search by name or ID…"
          bind:value={searchQuery}
          aria-label="Search scans"
        />
      </div>
      <span class="toolbar-meta">{filteredHistory.length} scans</span>
    </div>

    {#if !filteredHistory.length}
      <div class="data-empty">
        <Search size={40} strokeWidth={1.25} />
        <p>No scans found</p>
        <span>Check back after scanning users.</span>
      </div>
    {:else}
      <ul class="data-cards">
        {#each filteredHistory as scan}
          <li class="data-card">
            <div class="data-card-head">
              <div class="avatar">
                {(scan.user?.name || '?').charAt(0).toUpperCase()}
              </div>
              <div>
                <p class="data-card-title">{scan.user?.name || 'Unknown'}</p>
                <p class="data-card-sub">ID: {scan.user?.id || '—'}</p>
              </div>
              <StatusBadge status={scan.success ? 'Granted' : 'Denied'} />
            </div>
            <div class="data-card-row">
              <History size={14} />
              <span>{formatTime(scan.timestamp)}</span>
            </div>
          </li>
        {/each}
      </ul>

      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Member</th>
              <th>User ID</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredHistory as scan}
              <tr>
                <td class="cell-title">{scan.user?.name || 'Unknown'}</td>
                <td><code class="id-code">{scan.user?.id || '—'}</code></td>
                <td>{formatTime(scan.timestamp)}</td>
                <td><StatusBadge status={scan.success ? 'Granted' : 'Denied'} /></td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </Card>
</div>

<style>
  .data-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 2rem 1rem;
    color: var(--color-text-muted);
    text-align: center;
  }

  .data-empty p {
    font-weight: 600;
    color: var(--color-primary);
  }

  .avatar {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: var(--color-primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    flex-shrink: 0;
  }

  .data-card-head {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .data-card-head > div:nth-child(2) {
    flex: 1;
    min-width: 0;
  }

  .cell-title {
    font-weight: 600;
  }

  .id-code {
    font-size: 0.8125rem;
    background: var(--color-bg);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
  }
</style>
