<script>
  import { scannerSession } from '$lib/stores/scannerSession.js';
  import Card from '$lib/components/Card.svelte';
  import { Search, History, CheckCircle2, XCircle } from 'lucide-svelte';

  let searchQuery = $state('');

  const filteredHistory = $derived(
    $scannerSession.scanHistory.filter(scan => 
      scan.user?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scan.user?.id.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  function formatTime(date) {
    return new Intl.DateTimeFormat('default', {
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric'
    }).format(new Date(date));
  }
</script>

<svelte:head>
  <title>Recent Scanned - Meal Scanner</title>
</svelte:head>

<div class="history-page fade-in">
  <div class="header">
    <div class="header-text">
      <h1>Recent Scanned</h1>
      <p>View the real-time log of meal check-ins.</p>
    </div>
  </div>

  <Card>
    <div class="table-controls">
      <div class="search-box">
        <span class="search-icon">
          <Search size={18} />
        </span>
        <input 
          type="text" 
          placeholder="Search by name or ID..." 
          bind:value={searchQuery}
          aria-label="Search scans"
        />
      </div>
      
      <div class="filter-actions">
        <span class="scan-count">{filteredHistory.length} Scans Found</span>
      </div>
    </div>

    <div class="table-container">
      <table class="premium-table">
        <thead>
          <tr>
            <th>User Info</th>
            <th>User ID</th>
            <th>Time Scanned</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredHistory as scan}
            <tr class="table-row fade-in">
              <td>
                <div class="user-cell">
                  <div class="user-avatar" style="background-color: var(--color-primary)">
                    {scan.user?.name ? scan.user.name.charAt(0).toUpperCase() : '?'}
                  </div>
                  <div class="user-info">
                    <p class="user-name">{scan.user?.name || 'Unknown'}</p>
                  </div>
                </div>
              </td>
              
              <td>
                <span class="user-id">{scan.user?.id || '---'}</span>
              </td>
              
              <td>
                <div class="time-wrapper">
                  <span class="time-icon">
                    <History size={14} />
                  </span>
                  <span class="time-text">{formatTime(scan.timestamp)}</span>
                </div>
              </td>
              
              <td>
                <span class="status-badge {scan.success ? 'active' : 'inactive'}">
                  <div class="status-dot"></div>
                  {scan.success ? 'Granted' : 'Denied'}
                </span>
              </td>
            </tr>
          {:else}
            <tr>
              <td colspan="4">
                <div class="empty-state">
                  <span class="empty-icon">
                    <Search size={48} />
                  </span>
                  <h3>No scans found</h3>
                  <p>Check back after scanning some users.</p>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </Card>
</div>

<style>
  /* Base Layout Styles */
  .history-page {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  /* Header Section */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
  }

  .header-text h1 {
    font-size: 2rem;
    font-weight: 800;
    color: var(--color-primary);
    margin-bottom: 0.25rem;
  }

  .header-text p {
    color: var(--color-text-muted);
    font-size: 1rem;
  }

  /* Table Controls / Toolbar */
  .table-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    background-color: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-full);
    width: 100%;
    max-width: 400px;
    color: var(--color-text-muted);
    transition: all 0.2s ease;
  }

  .search-box:focus-within {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px rgba(229, 77, 56, 0.1);
  }

  .search-icon {
    color: var(--color-text-muted);
  }

  .search-box input {
    background: none;
    border: none;
    flex: 1;
    font-size: 0.875rem;
    color: var(--color-text);
  }

  .search-box input:focus { outline: none; }
  .search-box input::placeholder { color: #94A3B8; }

  .scan-count {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-text-muted);
    background-color: var(--color-bg);
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
  }

  @media (max-width: 640px) {
    .table-controls {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }
    .search-box {
      max-width: none;
    }
    .filter-actions {
      display: flex;
      justify-content: flex-end;
    }
  }

  /* Premium Table Styles */
  .table-container { 
    overflow-x: auto; 
    border-radius: var(--radius-md);
  }

  .premium-table { 
    width: 100%; 
    border-collapse: separate; 
    border-spacing: 0;
  }

  th { 
    text-align: left; 
    padding: 1rem 1.25rem; 
    font-size: 0.75rem; 
    font-weight: 700; 
    color: #64748B; 
    text-transform: uppercase; 
    letter-spacing: 0.05em;
    border-bottom: 2px solid var(--color-bg); 
    white-space: nowrap; 
    background-color: rgba(248, 250, 252, 0.5);
  }

  td { 
    padding: 1.25rem; 
    border-bottom: 1px solid var(--color-bg);
    vertical-align: middle;
  }

  .table-row {
    transition: background-color 0.2s ease;
  }

  .table-row:hover {
    background-color: rgba(248, 250, 252, 0.8);
  }

  @media (max-width: 640px) {
    th, td { padding: 1rem; }
  }

  /* User Profile Cell */
  .user-cell { 
    display: flex; 
    align-items: center; 
    gap: 1rem; 
  }

  .user-avatar { 
    width: 40px; 
    height: 40px; 
    border-radius: 12px; 
    color: white; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-weight: 700; 
    font-size: 1rem; 
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }

  .user-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .user-name { 
    font-weight: 700; 
    font-size: 0.9375rem; 
    color: var(--color-primary);
  }

  .user-id {
    font-family: monospace;
    color: var(--color-text-muted);
    background-color: var(--color-bg);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  /* Status Badge */
  .status-badge { 
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.875rem; 
    border-radius: 9999px; 
    font-size: 0.75rem; 
    font-weight: 700; 
    text-transform: capitalize;
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  .status-badge.active { 
    background-color: rgba(34, 197, 94, 0.1); 
    color: var(--color-success); 
  }
  
  .status-badge.active .status-dot {
    background-color: var(--color-success);
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
  }

  .status-badge.inactive { 
    background-color: rgba(239, 68, 68, 0.1); 
    color: var(--color-error); 
  }

  .status-badge.inactive .status-dot {
    background-color: var(--color-error);
    box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
  }

  /* Time Column */
  .time-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--color-text-muted);
  }

  .time-icon {
    opacity: 0.7;
  }

  .time-text { 
    font-weight: 600; 
    font-size: 0.875rem; 
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
  }

  .empty-icon {
    color: var(--color-border);
    margin-bottom: 1rem;
  }

  .empty-state h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: 0.5rem;
  }

  .empty-state p {
    color: var(--color-text-muted);
    font-size: 0.875rem;
  }
</style>
