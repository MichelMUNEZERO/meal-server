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
  <title>Overview — Admin</title>
</svelte:head>

<div class="admin-content fade-in">
  <header class="page-header">
    <h1>Overview</h1>
    <p>System activity at a glance.</p>
  </header>

  <div class="admin-stats-grid">
    {#each cards as stat}
      {@const Icon = stat.icon}
      <Card>
        <div class="stat-card">
          <div class="icon-wrap">
            <Icon size={22} />
          </div>
          <div class="meta">
            <span class="label">{stat.name}</span>
            <span class="value">{stat.value}</span>
          </div>
        </div>
      </Card>
    {/each}
  </div>

  <Card title="Quick links">
    <ul class="tips">
      <li><a href="/admin/users">User management</a> — members and password resets</li>
      <li><a href="/admin/meals">Meal packages</a> — breakfast, lunch, dinner access</li>
      <li><a href="/admin/attendance">Attendance logs</a> — view and export records</li>
      <li><a href="/admin/scanner">QR scanner</a> — scan codes at the counter</li>
      <li><a href="/admin/upload">Bulk upload</a> — import users from Excel</li>
      <li><a href="/admin/settings">Settings</a> — change your password</li>
    </ul>
  </Card>
</div>

<style>
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
    flex-shrink: 0;
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
    line-height: 1.9;
    font-size: 0.9375rem;
  }
</style>
