<script>
  import { toastStore } from '$lib/stores/toast.js';
  import Card from '$lib/components/Card.svelte';
  import { QrCode, Search, CheckCircle2, XCircle, Clock, ShieldCheck, Loader2 } from 'lucide-svelte';
  import { onMount } from 'svelte';

  let scanInput = $state('');
  let processing = $state(false);
  let result = $state(null); // { success: boolean, message: string, user: object }

  const MEAL_TIMES = [
    { type: 'Breakfast', start: 6, end: 11, icon: 'Coffee' },
    { type: 'Lunch', start: 12, end: 15, icon: 'Utensils' },
    { type: 'Dinner', start: 19, end: 22, icon: 'Moon' }
  ];

  function getCurrentMeal() {
    const hour = new Date().getHours();
    return MEAL_TIMES.find(m => hour >= m.start && hour < m.end);
  }

  let activeMeal = $state(getCurrentMeal());

  // Update active meal every minute
  onMount(() => {
    const interval = setInterval(() => {
      activeMeal = getCurrentMeal();
    }, 60000);
    return () => clearInterval(interval);
  });

  async function handleScan() {
    if (!scanInput) return;
    
    processing = true;
    result = null;
    
    // Simulate verification
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    try {
      // For demo, we assume scanInput is a JSON string from our QR generator
      const data = JSON.parse(scanInput);
      
      if (!activeMeal) {
        throw new Error('No meal session currently active.');
      }

      // Check if user has access to this meal type
      // In a real app, this would be a server-side check
      // For demo, we'll simulate a check
      const hasAccess = true; // mock check

      if (hasAccess) {
        result = {
          success: true,
          message: `Check-in successful for ${activeMeal.type}`,
          user: { name: 'Michel Munezero', id: 'u1' }
        };
        toastStore.success('Verified!');
      } else {
        throw new Error(`User does not have access to ${activeMeal.type}.`);
      }
    } catch (err) {
      result = {
        success: false,
        message: err.message || 'Invalid QR code'
      };
      toastStore.error(result.message);
    } finally {
      processing = false;
      scanInput = '';
    }
  }
</script>

<svelte:head>
  <title>Scanner - Meal Trackers</title>
</svelte:head>

<div class="scanner-page fade-in">
  <div class="status-banner {activeMeal ? 'active' : 'inactive'}">
    {#if activeMeal}
      <Clock size={20} />
      <span>Current Session: <strong>{activeMeal.type}</strong> ({activeMeal.start}:00 - {activeMeal.end}:00)</span>
    {:else}
      <Clock size={20} />
      <span>No active meal session at this time.</span>
    {/if}
  </div>

  <Card>
    <div class="scan-area">
      <div class="scan-visual">
        {#if processing}
          <div class="scanner-line scanning"></div>
        {/if}
        <QrCode size={120} class={processing ? 'dim' : ''} />
      </div>

      <div class="input-section">
        <p class="hint">Simulate a scan by pasting the QR data here:</p>
        <div class="input-wrapper">
          <input 
            type="text" 
            class="input" 
            placeholder="Paste QR payload..." 
            bind:value={scanInput}
            onkeydown={(e) => e.key === 'Enter' && handleScan()}
            disabled={processing || !activeMeal}
          />
          <button 
            class="btn btn-primary" 
            onclick={handleScan} 
            disabled={processing || !scanInput || !activeMeal}
          >
            {#if processing}
              <Loader2 class="animate-spin" size={20} />
            {:else}
              Verify
            {/if}
          </button>
        </div>
      </div>
    </div>
  </Card>

  {#if result}
    <div class="result-card fade-in {result.success ? 'success' : 'error'}">
      <div class="result-icon">
        {#if result.success}
          <CheckCircle2 size={48} />
        {:else}
          <XCircle size={48} />
        {/if}
      </div>
      <div class="result-info">
        <h3>{result.success ? 'Access Granted' : 'Access Denied'}</h3>
        <p>{result.message}</p>
        {#if result.user}
          <div class="user-detail">
            <span class="label">Attendee</span>
            <span class="value">{result.user.name}</span>
          </div>
        {/if}
      </div>
      <button class="close-result" onclick={() => result = null}>&times;</button>
    </div>
  {/if}
</div>

<style>
  .scanner-page {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .status-banner {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    border-radius: var(--radius-md);
    font-size: 0.9375rem;
    background-color: var(--color-surface);
    box-shadow: var(--shadow-sm);
  }

  .status-banner.active {
    border-left: 4px solid var(--color-success);
    color: var(--color-primary);
  }

  .status-banner.inactive {
    border-left: 4px solid var(--color-accent);
    color: var(--color-text-muted);
  }

  .scan-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 0;
    text-align: center;
  }

  .scan-visual {
    position: relative;
    padding: 2rem;
    background-color: var(--color-bg);
    border-radius: var(--radius-lg);
    margin-bottom: 2.5rem;
    color: var(--color-primary);
    overflow: hidden;
  }

  .dim { opacity: 0.3; }

  .scanner-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background-color: var(--color-accent);
    box-shadow: 0 0 15px var(--color-accent);
    z-index: 10;
  }

  .scanning {
    animation: scan 1.5s ease-in-out infinite;
  }

  @keyframes scan {
    0%, 100% { top: 0; }
    50% { top: 100%; }
  }

  .input-section {
    width: 100%;
    max-width: 400px;
  }

  .hint {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    margin-bottom: 0.75rem;
  }

  .input-wrapper {
    display: flex;
    gap: 0.5rem;
  }

  .result-card {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem;
    border-radius: var(--radius-lg);
    color: white;
    position: relative;
    box-shadow: var(--shadow-lg);
  }

  .result-card.success { background-color: var(--color-success); }
  .result-card.error { background-color: var(--color-accent); }

  .result-icon { flex-shrink: 0; }

  .result-info h3 {
    color: white;
    font-size: 1.25rem;
    margin-bottom: 0.25rem;
  }

  .result-info p {
    opacity: 0.9;
    font-size: 0.9375rem;
    margin-bottom: 1rem;
  }

  .user-detail {
    background-color: rgba(255, 255, 255, 0.2);
    padding: 0.75rem 1.25rem;
    border-radius: var(--radius-md);
    display: flex;
    flex-direction: column;
    text-align: left;
  }

  .user-detail .label {
    font-size: 0.6875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
    opacity: 0.8;
  }

  .user-detail .value {
    font-weight: 700;
    font-size: 1.125rem;
  }

  .close-result {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    opacity: 0.6;
  }

  .close-result:hover { opacity: 1; }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
