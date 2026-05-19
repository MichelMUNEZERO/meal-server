<script>
  import { authStore } from '$lib/stores/auth.js';
  import Card from '$lib/components/Card.svelte';
  import { progressPercent } from '$lib/utils/helpers.js';
  import { Coffee, Utensils, Moon, Clock, Calendar, CheckCircle2 } from 'lucide-svelte';

  const user = $derived($authStore.user);
  const plan = $derived(user?.mealPlan);
  const progress = $derived(
    plan ? progressPercent(plan.daysRemaining, plan.totalDays) : 0
  );
</script>

<svelte:head>
  <title>Dashboard — Meal Trackers</title>
</svelte:head>

{#if user && plan}
  <div class="dashboard-page fade-in">
    <header class="page-header">
      <h1>Hello, {user.name}</h1>
      <p>Your meal plan overview for today.</p>
    </header>

    <div class="stats-grid">
      <Card>
        <div class="stat-row">
          <div class="stat-icon"><Calendar size={22} /></div>
          <div>
            <span class="stat-label">Days remaining</span>
            <span class="stat-value">{plan.daysRemaining} / {plan.totalDays}</span>
            <div class="progress-bar">
              <div class="progress-fill" style="width: {progress}%"></div>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div class="stat-row">
          <div class="stat-icon success">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <span class="stat-label">Plan status</span>
            <span class="stat-value">Active</span>
            <span class="stat-sub">
              Valid until {plan.validUntil
                ? new Date(plan.validUntil).toLocaleDateString()
                : '—'}
            </span>
          </div>
        </div>
      </Card>
    </div>

    <h2 class="section-title">Your meals</h2>
    <div class="meal-grid">
      <Card>
        <article class="meal-item" class:inactive={!plan.breakfast}>
          <Coffee size={22} />
          <h3>Breakfast</h3>
          <p><Clock size={14} /> 07:00 – 09:30</p>
          <span class="meal-badge">{plan.breakfast ? 'Included' : 'Not included'}</span>
        </article>
      </Card>
      <Card>
        <article class="meal-item" class:inactive={!plan.lunch}>
          <Utensils size={22} />
          <h3>Lunch</h3>
          <p><Clock size={14} /> 12:30 – 14:30</p>
          <span class="meal-badge">{plan.lunch ? 'Included' : 'Not included'}</span>
        </article>
      </Card>
      <Card>
        <article class="meal-item" class:inactive={!plan.dinner}>
          <Moon size={22} />
          <h3>Dinner</h3>
          <p><Clock size={14} /> 19:30 – 21:30</p>
          <span class="meal-badge">{plan.dinner ? 'Included' : 'Not included'}</span>
        </article>
      </Card>
    </div>

    <Card title="Quick actions">
      <div class="actions">
        <a href="/dashboard/qr" class="btn btn-primary">Generate QR code</a>
        <a href="/dashboard/history" class="btn btn-outline">View history</a>
      </div>
    </Card>
  </div>
{/if}

<style>
  .dashboard-page {
    max-width: 960px;
    margin: 0 auto;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2rem;
  }

  .stat-row {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: var(--color-primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-icon.success {
    background: var(--color-success);
  }

  .stat-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-text-muted);
    margin-bottom: 0.25rem;
  }

  .stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .stat-sub {
    font-size: 0.8125rem;
    color: var(--color-success);
    font-weight: 600;
  }

  .progress-bar {
    height: 6px;
    background: var(--color-bg);
    border-radius: 3px;
    margin-top: 0.625rem;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--color-accent);
    border-radius: 3px;
    transition: width 0.6s ease;
  }

  .section-title {
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }

  .meal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .meal-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    color: var(--color-accent);
  }

  .meal-item h3 {
    font-size: 1.0625rem;
    color: var(--color-primary);
  }

  .meal-item p {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.875rem;
    color: var(--color-text-muted);
    margin-bottom: 0.5rem;
  }

  .meal-badge {
    align-self: flex-start;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.625rem;
    border-radius: var(--radius-full);
    background: rgba(22, 163, 74, 0.1);
    color: var(--color-success);
  }

  .meal-item.inactive {
    opacity: 0.65;
  }

  .meal-item.inactive .meal-badge {
    background: var(--color-bg);
    color: var(--color-text-muted);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }
</style>
