<script>
  import { onMount } from 'svelte';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import Card from '$lib/components/Card.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import * as XLSX from 'xlsx';
  import { Search, Download, Calendar, Clock } from 'lucide-svelte';

  let logs = $state([]);
  let loading = $state(true);
  let searchQuery = $state('');

  onMount(async () => {
    try {
      logs = await attendanceService.getHistory();
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  });

  const filteredLogs = $derived(
    logs.filter(
      (log) =>
        log.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        log.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        log.date.includes(searchQuery)
    )
  );

  function exportToExcel() {
    const worksheet = XLSX.utils.json_to_sheet(filteredLogs);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Attendance');
    const date = new Date().toISOString().split('T')[0];
    XLSX.writeFile(workbook, `Attendance_Report_${date}.xlsx`);
  }
</script>

<svelte:head>
  <title>Attendance — Admin</title>
</svelte:head>

<div class="admin-content fade-in">
  <header class="page-header page-header-row">
    <div>
      <h1>Attendance logs</h1>
      <p>View and export all meal attendance records.</p>
    </div>
    <div class="page-actions">
      <button
        type="button"
        class="btn btn-primary"
        onclick={exportToExcel}
        disabled={filteredLogs.length === 0}
      >
        <Download size={18} />
        Export to Excel
      </button>
    </div>
  </header>

  <Card>
    <div class="data-toolbar">
      <div class="search-field">
        <Search size={18} />
        <input type="search" placeholder="Search name, meal, or date…" bind:value={searchQuery} />
      </div>
      <span class="toolbar-meta">{filteredLogs.length} records</span>
    </div>

    {#if loading}
      <p class="data-empty">Loading records…</p>
    {:else if !filteredLogs.length}
      <p class="data-empty">No records found.</p>
    {:else}
      <ul class="data-cards">
        {#each filteredLogs as log}
          <li class="data-card">
            <div class="data-card-head">
              <div>
                <p class="data-card-title">{log.userName}</p>
                <p class="data-card-sub">{log.type}</p>
              </div>
              <StatusBadge status={log.status} />
            </div>
            <div class="data-card-row">
              <Calendar size={14} />
              <span>{log.date}</span>
            </div>
            <div class="data-card-row">
              <Clock size={14} />
              <span>{log.time}</span>
            </div>
          </li>
        {/each}
      </ul>

      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Attendee</th>
              <th>Date</th>
              <th>Meal</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredLogs as log}
              <tr>
                <td class="cell-title">{log.userName}</td>
                <td>{log.date}</td>
                <td>{log.type}</td>
                <td>{log.time}</td>
                <td><StatusBadge status={log.status} /></td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </Card>
</div>

<style>
  .cell-title {
    font-weight: 600;
  }
</style>
