<script>
  import Card from '$lib/components/Card.svelte';
  import { Users, Utensils, ClipboardCheck, TrendingUp, ArrowUpRight, ArrowDownRight } from 'lucide-svelte';

  const stats = [
    { name: 'Total Users', value: '1,284', icon: Users, color: 'blue', change: '+12%', up: true },
    { name: 'Active Plans', value: '942', icon: Utensils, color: 'teal', change: '+5%', up: true },
    { name: 'Served Today', value: '458', icon: ClipboardCheck, color: 'orange', change: '-2%', up: false },
    { name: 'Revenue', value: '$12,450', icon: TrendingUp, color: 'purple', change: '+18%', up: true }
  ];
</script>

<svelte:head>
  <title>Admin Overview - Trackers</title>
</svelte:head>

<div class="admin-overview fade-in">
  <div class="header">
    <div>
      <h1>Admin Dashboard</h1>
      <p>System status and performance metrics.</p>
    </div>
    <button class="btn btn-primary">
      <ArrowUpRight size={18} />
      Generate Report
    </button>
  </div>

  <div class="stats-grid">
    {#each stats as stat}
      {@const Icon = stat.icon}
      <Card>
        <div class="stat-card">
          <div class="stat-main">
            <div class="stat-icon-box {stat.color}">
              <Icon size={24} />
            </div>
            <div>
              <p class="stat-label">{stat.name}</p>
              <h3 class="stat-value">{stat.value}</h3>
            </div>
          </div>
          <div class="stat-footer">
            <span class="change-tag {stat.up ? 'up' : 'down'}">
              {#if stat.up}
                <ArrowUpRight size={14} />
              {:else}
                <ArrowDownRight size={14} />
              {/if}
              {stat.change}
            </span>
            <span class="stat-period">vs last month</span>
          </div>
        </div>
      </Card>
    {/each}
  </div>

  <div class="charts-row">
    <div class="chart-main">
      <Card title="Attendance Trends">
        <div class="placeholder-chart">
          <!-- Placeholder for a real chart library like Chart.js or LayerCake -->
          <div class="bar-chart">
            {#each Array(12) as _, i}
              <div class="bar" style="height: {Math.random() * 80 + 20}%"></div>
            {/each}
          </div>
          <div class="chart-labels">
            <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
            <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
          </div>
        </div>
      </Card>
    </div>
    <div class="recent-activity">
      <Card title="Recent Activity">
        <div class="activity-list">
          {#each [1, 2, 3, 4, 5] as i}
            <div class="activity-item">
              <div class="activity-dot"></div>
              <div class="activity-content">
                <p><strong>User check-in</strong>: Michel Munezero scanned for Lunch</p>
                <span class="activity-time">2 minutes ago</span>
              </div>
            </div>
          {/each}
        </div>
      </Card>
    </div>
  </div>
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

    .header h1 {
      font-size: 1.5rem;
    }

    .header .btn {
      width: 100%;
      justify-content: center;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2.5rem;
  }

  .stat-card {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .stat-main {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .stat-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .stat-icon-box.blue { background-color: #3B82F6; }
  .stat-icon-box.teal { background-color: #0D9488; }
  .stat-icon-box.orange { background-color: #F59E0B; }
  .stat-icon-box.purple { background-color: #8B5CF6; }

  .stat-label {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    font-weight: 500;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
  }

  .stat-footer {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .change-tag {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .change-tag.up { background-color: rgba(34, 197, 94, 0.1); color: var(--color-success); }
  .change-tag.down { background-color: rgba(239, 68, 68, 0.1); color: var(--color-error); }

  .stat-period {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .charts-row {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
  }

  @media (max-width: 1200px) {
    .charts-row { grid-template-columns: 1fr; }
  }

  .placeholder-chart {
    height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
  }

  .bar-chart {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 240px;
    gap: 8px;
  }

  .bar {
    flex: 1;
    background: linear-gradient(to top, var(--color-primary), #5EEAD4);
    border-radius: 4px 4px 0 0;
    transition: height 0.5s ease-out;
  }

  .chart-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .activity-item {
    display: flex;
    gap: 1rem;
    position: relative;
  }

  .activity-item:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 7px;
    top: 20px;
    bottom: -15px;
    width: 2px;
    background-color: var(--color-bg);
  }

  .activity-dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: var(--color-primary);
    border: 3px solid var(--color-surface);
    box-shadow: 0 0 0 1px var(--color-primary);
    z-index: 1;
    margin-top: 4px;
  }

  .activity-content p {
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
  }

  .activity-time {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }
</style>
