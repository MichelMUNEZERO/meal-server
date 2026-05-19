<script>
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { usersService } from '$lib/services/users.service.js';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import { Users, Utensils, ClipboardCheck, UserCheck } from 'lucide-svelte';

  let stats = $state({
    totalUsers: 0,
    activeUsers: 0,
    servedToday: 0,
    checkinsWeek: 0
  });

  onMount(async () => {
    try {
      // Backend integration point — replace with /api/admin/stats/
      const [users, logs] = await Promise.all([
        usersService.getAll(),
        attendanceService.getHistory()
      ]);

      const today = new Date().toISOString().split('T')[0];
      stats = {
        totalUsers: users.length,
        activeUsers: users.filter((u) => u.status === 'Active').length,
        servedToday: logs.filter((l) => l.date === today).length,
        checkinsWeek: logs.length
      };
    } catch {
      /* keep zeros */
    }
  });

  const cards = $derived([
    { name: 'Total members', value: stats.totalUsers, icon: Users },
    { name: 'Active plans', value: stats.activeUsers, icon: UserCheck },
    { name: 'Check-ins today', value: stats.servedToday, icon: ClipboardCheck },
    { name: 'Recent records', value: stats.checkinsWeek, icon: Utensils }
  ]);
</script>

<svelte:head>
  <title>Admin overview</title>
</svelte:head>

<div class="overview fade-in">
  <header class="page-header">
    <h1>Overview</h1>
    <p>System activity at a glance.</p>
  </header>

  <div class="stats-grid">
    {#each cards as stat}
      {@const Icon = stat.icon}
      <Card>
        <div class="stat-card">
          <div class="icon-wrap"><Icon size={22} /></div>
          <div class="meta">
            <span class="label">{stat.name}</span>
            <span class="value">{stat.value}</span>
          </div>
        </div>
      </Card>
    {/each}
  </div>

  <Card title="Getting started">
    <ul class="tips">
      <li>Upload members via <a href="/admin/upload">Bulk upload</a>.</li>
      <li>Assign meals under <a href="/admin/meals">Meal packages</a>.</li>
      <li>Export logs from <a href="/admin/attendance">Attendance</a>.</li>
    </ul>
  </Card>
</div>

<style>
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-card {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
    background: var(--color-accent-muted);
    color: var(--color-accent);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .meta .label {
    display: block;
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    margin-bottom: 0.125rem;
  }

  .meta .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .tips {
    padding-left: 1.25rem;
    color: var(--color-text-muted);
    line-height: 1.8;
    font-size: 0.9375rem;
  }
</style>
