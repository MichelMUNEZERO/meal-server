<script>
  import { onMount } from 'svelte';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import Card from '$lib/components/Card.svelte';
  import * as XLSX from 'xlsx';
  import { Search, Filter, Download, Calendar, Clock, User } from 'lucide-svelte';

  let logs = $state([]);
  let loading = $state(true);
  let searchQuery = $state('');

  onMount(async () => {
    try {
      logs = await attendanceService.getHistory(); // Admin gets all history
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  });

  const filteredLogs = $derived(
    logs.filter(log => 
      log.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.date.includes(searchQuery)
    )
  );

  function exportToExcel() {
    const worksheet = XLSX.utils.json_to_sheet(filteredLogs);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Attendance");
    
    // Generate filename with timestamp
    const date = new Date().toISOString().split('T')[0];
    XLSX.writeFile(workbook, `Attendance_Report_${date}.xlsx`);
  }
</script>

<svelte:head>
  <title>Attendance Logs - Trackers Admin</title>
</svelte:head>

<div class="attendance-logs fade-in">
  <div class="header">
    <div>
      <h1>Attendance Logs</h1>
      <p>View and export all meal attendance records.</p>
    </div>
    <button class="btn btn-primary" onclick={exportToExcel} disabled={logs.length === 0}>
      <Download size={18} />
      Export to Excel
    </button>
  </div>

  <Card>
    <div class="table-controls">
      <div class="search-box">
        <Search size={18} />
        <input 
          type="text" 
          placeholder="Search by name, meal, or date..." 
          bind:value={searchQuery}
        />
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Attendee</th>
            <th>Date</th>
            <th>Meal Type</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {#if loading}
            {#each Array(5) as _}
              <tr class="skeleton-row">
                <td colspan="5"><div class="skeleton"></div></td>
              </tr>
            {/each}
          {:else if filteredLogs.length === 0}
            <tr>
              <td colspan="5" class="empty-state">No records found.</td>
            </tr>
          {:else}
            {#each filteredLogs as log}
              <tr>
                <td>
                  <div class="user-cell">
                    <User size={16} />
                    <span>{log.userName}</span>
                  </div>
                </td>
                <td>
                  <div class="date-cell">
                    <Calendar size={14} />
                    {log.date}
                  </div>
                </td>
                <td>
                  <span class="meal-tag">{log.type}</span>
                </td>
                <td>
                  <div class="time-cell">
                    <Clock size={14} />
                    {log.time}
                  </div>
                </td>
                <td>
                  <span class="status-badge success">Present</span>
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </Card>
</div>

<style>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
    gap: 1.5rem;
  }

  @media (max-width: 640px) {
    .header {
      flex-direction: column;
      align-items: flex-start;
      margin-bottom: 2rem;
    }

    .header .btn {
      width: 100%;
      justify-content: center;
    }
  }

  .table-controls {
    margin-bottom: 1.5rem;
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1rem;
    background-color: var(--color-bg);
    border-radius: 8px;
    max-width: 400px;
    color: var(--color-text-muted);
  }

  @media (max-width: 640px) {
    .search-box {
      max-width: none;
    }
  }

  .search-box input {
    background: none;
    border: none;
    flex: 1;
    font-size: 0.875rem;
    color: var(--color-text);
  }

  .search-box input:focus { outline: none; }

  .table-container { overflow-x: auto; }

  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 1rem; font-size: 0.75rem; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase; border-bottom: 1px solid var(--color-bg); white-space: nowrap; }
  td { padding: 1rem; border-bottom: 1px solid var(--color-bg); font-size: 0.875rem; white-space: nowrap; }

  @media (max-width: 640px) {
    th, td { padding: 0.75rem; }
  }

  .user-cell, .date-cell, .time-cell {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .meal-tag {
    font-weight: 600;
    color: var(--color-primary);
  }

  .status-badge {
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .status-badge.success {
    background-color: rgba(102, 198, 106, 0.1);
    color: var(--color-success);
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--color-text-muted);
  }

  .skeleton {
    height: 1.5rem;
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
