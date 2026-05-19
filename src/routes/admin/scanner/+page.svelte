<script>
  import QrScannerPanel from '$lib/components/QrScannerPanel.svelte';
  import Card from '$lib/components/Card.svelte';
  import { scannerSession } from '$lib/stores/scannerSession.js';
  import { CheckCircle2, XCircle } from 'lucide-svelte';

  function formatTime(date) {
    return new Intl.DateTimeFormat(undefined, {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(date));
  }
</script>

<svelte:head>
  <title>QR scanner — Admin</title>
</svelte:head>

<div class="admin-content fade-in admin-scanner-page">
  <header class="page-header">
    <h1>QR scanner</h1>
    <p>Scan member meal codes at the counter, same as the scanner role.</p>
  </header>

  <div class="scanner-layout">
    <QrScannerPanel />

    <Card title="Recent scans (this session)">
      <p class="session-count">{$scannerSession.totalScans} successful check-ins</p>
      <ul class="recent-list">
        {#each $scannerSession.scanHistory.slice(0, 8) as scan}
          <li class="recent-item" class:ok={scan.success}>
            {#if scan.success}
              <CheckCircle2 size={18} />
            {:else}
              <XCircle size={18} />
            {/if}
            <div class="recent-text">
              <span class="name">{scan.user?.name || 'Unknown'}</span>
              <span class="time">{formatTime(scan.timestamp)}</span>
            </div>
            <span class="badge-mini">{scan.success ? 'Granted' : 'Denied'}</span>
          </li>
        {:else}
          <li class="data-empty">No scans yet this session.</li>
        {/each}
      </ul>
    </Card>
  </div>
</div>

<style>
  .scanner-layout {
    display: grid;
    gap: 1.25rem;
  }

  @media (min-width: 900px) {
    .scanner-layout {
      grid-template-columns: 1fr 1fr;
      align-items: start;
    }
  }

  .session-count {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    margin-bottom: 1rem;
  }

  .recent-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 24rem;
    overflow-y: auto;
  }

  .recent-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.625rem 0.75rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    font-size: 0.875rem;
  }

  .recent-item.ok {
    color: var(--color-success);
  }

  .recent-item:not(.ok) {
    color: var(--color-error);
  }

  .recent-text {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }

  .recent-text .name {
    font-weight: 600;
    color: var(--color-text);
  }

  .recent-text .time {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .badge-mini {
    font-size: 0.6875rem;
    font-weight: 700;
    text-transform: uppercase;
    flex-shrink: 0;
  }
</style>
