<script>
  import { authStore } from '$lib/stores/auth.js';
  import Card from '$lib/components/Card.svelte';
  import { Coffee, Utensils, Moon, Clock, Calendar, CheckCircle2 } from 'lucide-svelte';

  const user = $authStore.user;
  const progress = (user.mealPlan.daysRemaining / user.mealPlan.totalDays) * 100;
</script>

<svelte:head>
  <title>Dashboard - Meal Trackers</title>
</svelte:head>

<div class="dashboard-page fade-in">
  <div class="welcome-section">
    <h1>Hello, {user.name}</h1>
    <p>Here's your meal plan overview for today.</p>
  </div>

  <div class="stats-grid">
    <Card>
      <div class="stat-card">
        <div class="stat-icon days">
          <Calendar size={24} />
        </div>
        <div class="stat-info">
          <span class="stat-label">Days Remaining</span>
          <span class="stat-value">{user.mealPlan.daysRemaining} / {user.mealPlan.totalDays}</span>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
          </div>
        </div>
      </div>
    </Card>

    <Card>
      <div class="stat-card">
        <div class="stat-icon status">
          <CheckCircle2 size={24} />
        </div>
        <div class="stat-info">
          <span class="stat-label">Plan Status</span>
          <span class="stat-value">Active</span>
          <span class="stat-sub">Valid until May 30, 2026</span>
        </div>
      </div>
    </Card>
  </div>

  <h2 class="section-title">Your Meal Plan</h2>
  <div class="meal-grid">
    <Card>
      <div class="meal-card {user.mealPlan.breakfast ? 'active' : 'inactive'}">
        <div class="meal-header">
          <Coffee size={24} />
          <h3>Breakfast</h3>
        </div>
        <p class="meal-time"><Clock size={14} /> 07:00 AM - 09:30 AM</p>
        <span class="status-badge">{user.mealPlan.breakfast ? 'Included' : 'Not Included'}</span>
      </div>
    </Card>

    <Card>
      <div class="meal-card {user.mealPlan.lunch ? 'active' : 'inactive'}">
        <div class="meal-header">
          <Utensils size={24} />
          <h3>Lunch</h3>
        </div>
        <p class="meal-time"><Clock size={14} /> 12:30 PM - 02:30 PM</p>
        <span class="status-badge">{user.mealPlan.lunch ? 'Included' : 'Not Included'}</span>
      </div>
    </Card>

    <Card>
      <div class="meal-card {user.mealPlan.dinner ? 'active' : 'inactive'}">
        <div class="meal-header">
          <Moon size={24} />
          <h3>Dinner</h3>
        </div>
        <p class="meal-time"><Clock size={14} /> 07:30 PM - 09:30 PM</p>
        <span class="status-badge">{user.mealPlan.dinner ? 'Included' : 'Not Included'}</span>
      </div>
    </Card>
  </div>

  <div class="quick-action-section">
    <Card title="Quick Access">
      <div class="quick-actions">
        <a href="/dashboard/qr" class="btn btn-primary">
          Generate QR Code
        </a>
        <a href="/dashboard/history" class="btn btn-outline">
          View History
        </a>
      </div>
    </Card>
  </div>
</div>

<style>
  .dashboard-page {
    max-width: 1100px;
    margin: 0 auto;
  }

  .welcome-section {
    margin-bottom: 3rem;
  }

  .welcome-section h1 {
    font-size: 2.25rem;
    margin-bottom: 0.5rem;
    color: var(--color-primary);
  }

  .welcome-section p {
    color: var(--color-text-muted);
    font-size: 1.125rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 4rem;
  }

  .stat-card {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
  }

  .stat-icon.days { background-color: var(--color-primary); }
  .stat-icon.status { background-color: var(--color-success); }

  .stat-info {
    flex: 1;
  }

  .stat-label {
    display: block;
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }

  .stat-value {
    display: block;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .stat-sub {
    font-size: 0.75rem;
    color: var(--color-success);
    font-weight: 700;
  }

  .progress-bar {
    height: 8px;
    background-color: #EDF2F7;
    border-radius: 4px;
    margin-top: 0.75rem;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background-color: var(--color-accent);
    border-radius: 4px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .section-title {
    font-size: 1.5rem;
    margin-bottom: 2rem;
    position: relative;
    padding-left: 1rem;
  }

  .section-title::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.25rem;
    bottom: 0.25rem;
    width: 4px;
    background-color: var(--color-accent);
    border-radius: 2px;
  }

  .meal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin-bottom: 4rem;
  }

  .meal-card {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .meal-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.25rem;
    color: var(--color-accent);
  }

  .meal-header h3 {
    font-size: 1.25rem;
    color: var(--color-primary);
  }

  .meal-time {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    font-size: 0.9375rem;
    color: var(--color-text-muted);
    margin-bottom: 2rem;
  }

  .status-badge {
    align-self: flex-start;
    padding: 0.5rem 1.25rem;
    border-radius: var(--radius-full);
    font-size: 0.8125rem;
    font-weight: 700;
  }

  .active .status-badge {
    background-color: rgba(102, 198, 106, 0.1);
    color: var(--color-success);
  }

  .inactive .status-badge {
    background-color: #F1F5F9;
    color: #94A3B8;
  }

  .inactive {
    opacity: 0.7;
    filter: grayscale(0.5);
  }

  .quick-actions {
    display: flex;
    gap: 1.25rem;
  }

  @media (max-width: 640px) {
    .quick-actions {
      flex-direction: column;
    }
  }
</style>
