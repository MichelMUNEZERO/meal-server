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

<div class="admin-content fade-in">
  <header class="page-header">
    <h1>Meal packages</h1>
    <p>Assign breakfast, lunch, and dinner access per member.</p>
  </header>

  <Card>
    {#if loading}
      <p class="data-empty">Loading…</p>
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
          Breakfast (07:00–09:30)
        </label>
        <label class="check">
          <input type="checkbox" bind:checked={plan.lunch} />
          Lunch (12:30–14:30)
        </label>
        <label class="check">
          <input type="checkbox" bind:checked={plan.dinner} />
          Dinner (19:30–21:30)
        </label>
      </div>

      <div class="field">
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

      <button type="button" class="btn btn-primary save-btn" onclick={savePlan} disabled={saving}>
        {#if saving}
          <Loader2 size={18} class="spin" />
        {:else}
          <Save size={18} />
        {/if}
        Save package
      </button>
    {/if}
  </Card>
</div>

<style>
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
    border: 1px solid var(--color-border);
  }

  .check {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    font-weight: 500;
    cursor: pointer;
    font-size: 0.9375rem;
  }

  .check input {
    width: 1.125rem;
    height: 1.125rem;
    accent-color: var(--color-accent);
  }

  .save-btn {
    width: 100%;
  }

  @media (min-width: 480px) {
    .save-btn {
      width: auto;
    }
  }
</style>
