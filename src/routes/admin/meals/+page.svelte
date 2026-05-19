<script>
  import { onMount } from 'svelte';
  import { usersService } from '$lib/services/users.service.js';
  import { mealsService } from '$lib/services/meals.service.js';
  import { toastStore } from '$lib/stores/toast.js';
  import Card from '$lib/components/Card.svelte';
  import { Save, Loader2 } from 'lucide-svelte';

  let users = $state([]);
  let selectedId = $state('');
  let plan = $state({
    breakfast: false,
    lunch: false,
    dinner: false,
    daysRemaining: 0,
    totalDays: 30
  });
  let loading = $state(true);
  let saving = $state(false);

  onMount(async () => {
    try {
      users = await usersService.getAll();
      if (users.length) {
        selectedId = users[0].id;
        await loadPlan(selectedId);
      }
    } catch (err) {
      toastStore.error(err.message || 'Failed to load users');
    } finally {
      loading = false;
    }
  });

  async function loadPlan(userId) {
    // Backend integration point
    plan = await mealsService.getPlanForUser(userId);
  }

  async function onUserChange(e) {
    selectedId = e.target.value;
    await loadPlan(selectedId);
  }

  async function savePlan() {
    if (!selectedId) return;
    saving = true;
    try {
      // Backend integration point
      await mealsService.updatePlanForUser(selectedId, plan);
      toastStore.success('Meal package updated');
    } catch (err) {
      toastStore.error(err.message || 'Could not save plan');
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head>
  <title>Meal packages — Admin</title>
</svelte:head>

<div class="meals-page fade-in">
  <header class="page-header">
    <h1>Meal packages</h1>
    <p>Assign breakfast, lunch, and dinner access per member.</p>
  </header>

  <Card>
    {#if loading}
      <p class="muted">Loading…</p>
    {:else}
      <div class="field">
        <label for="user" class="label">Select member</label>
        <select id="user" class="input" value={selectedId} onchange={onUserChange}>
          {#each users as user}
            <option value={user.id}>{user.name} ({user.email})</option>
          {/each}
        </select>
      </div>

      <div class="checks">
        <label class="check">
          <input type="checkbox" bind:checked={plan.breakfast} />
          Breakfast
        </label>
        <label class="check">
          <input type="checkbox" bind:checked={plan.lunch} />
          Lunch
        </label>
        <label class="check">
          <input type="checkbox" bind:checked={plan.dinner} />
          Dinner
        </label>
      </div>

      <div class="row">
        <label for="days" class="label">Days remaining</label>
        <input
          id="days"
          type="number"
          class="input"
          min="0"
          max={plan.totalDays}
          bind:value={plan.daysRemaining}
        />
      </div>

      <button type="button" class="btn btn-primary" onclick={savePlan} disabled={saving}>
        {#if saving}
          <span class="spin"><Loader2 size={18} /></span>
        {:else}
          <Save size={18} />
        {/if}
        Save package
      </button>
    {/if}
  </Card>
</div>

<style>
  .meals-page {
    max-width: 560px;
  }

  .field {
    margin-bottom: 1.25rem;
  }

  .checks {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
    padding: 1rem;
    background: var(--color-bg);
    border-radius: var(--radius-md);
  }

  .check {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    font-weight: 500;
    cursor: pointer;
  }

  .check input {
    width: 1rem;
    height: 1rem;
    accent-color: var(--color-accent);
  }

  .row {
    margin-bottom: 1.25rem;
  }

  .muted {
    color: var(--color-text-muted);
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
