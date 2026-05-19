<script>
  import { onMount } from 'svelte';
  import QRCode from 'qrcode';
  import { authStore } from '$lib/stores/auth.js';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import { getCurrentMealWindow } from '$lib/utils/helpers.js';
  import { QR_EXPIRY_SECONDS } from '$lib/utils/constants.js';
  import Card from '$lib/components/Card.svelte';
  import { RefreshCw, Clock, ShieldCheck, AlertCircle } from 'lucide-svelte';

  let qrImage = $state('');
  let loading = $state(true);
  let timeLeft = $state(QR_EXPIRY_SECONDS);
  let activeMeal = $state(getCurrentMealWindow());
  /** @type {ReturnType<typeof setInterval> | undefined} */
  let timer;

  async function generateNewQR() {
    const user = $authStore.user;
    if (!user) return;

    loading = true;
    try {
      // Backend integration point — server may return signed payload
      const data = await attendanceService.generateQR(
        user.id,
        user.name,
        activeMeal?.type
      );
      qrImage = await QRCode.toDataURL(data, {
        width: 280,
        margin: 2,
        color: { dark: '#0f172a', light: '#ffffff' }
      });
      timeLeft = QR_EXPIRY_SECONDS;
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(() => {
      if (timeLeft > 0) {
        timeLeft -= 1;
      } else {
        generateNewQR();
      }
    }, 1000);
  }

  onMount(() => {
    activeMeal = getCurrentMealWindow();
    generateNewQR().then(resetTimer);
    return () => clearInterval(timer);
  });
</script>

<svelte:head>
  <title>QR code — Meal Trackers</title>
</svelte:head>

<div class="qr-page fade-in">
  <header class="page-header">
    <h1>Meal access QR</h1>
    <p>
      {#if activeMeal}
        Present this code for <strong>{activeMeal.type}</strong> ({activeMeal.start}:00–{activeMeal.end}:00).
      {:else}
        No meal window is active right now. Your code will refresh when a session starts.
      {/if}
    </p>
  </header>

  <div class="qr-grid">
    <Card>
      <div class="qr-panel">
        {#if loading && !qrImage}
          <div class="qr-placeholder" aria-busy="true">
            <RefreshCw size={40} class="spin" />
          </div>
        {:else}
          <div class="qr-wrap">
            <img src={qrImage} alt="Meal access QR code" class="qr-image" />
            <div class="qr-badge" aria-hidden="true">
              <ShieldCheck size={28} />
            </div>
          </div>
        {/if}

        <div class="timer">
          <div class="timer-track">
            <div class="timer-fill" style="width: {(timeLeft / QR_EXPIRY_SECONDS) * 100}%"></div>
          </div>
          <p><Clock size={16} /> Expires in <strong>{timeLeft}s</strong></p>
        </div>

        <button type="button" class="btn btn-primary btn-block" onclick={generateNewQR} disabled={loading}>
          <RefreshCw size={18} class={loading ? 'spin' : ''} />
          Regenerate
        </button>
      </div>
    </Card>

    <Card title="How to use">
      <ol class="steps">
        <li>Increase screen brightness.</li>
        <li>Hold the code 10–15 cm from the scanner.</li>
        <li>Wait for confirmation before closing the screen.</li>
      </ol>
      <p class="note">
        <AlertCircle size={18} />
        Single-use codes expire automatically for security.
      </p>
    </Card>
  </div>
</div>

<style>
  .qr-page {
    max-width: 880px;
    margin: 0 auto;
  }

  .qr-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }

  @media (max-width: 768px) {
    .qr-grid { grid-template-columns: 1fr; }
  }

  .qr-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.25rem;
  }

  .qr-placeholder {
    width: 280px;
    height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-bg);
    border-radius: var(--radius-md);
    color: var(--color-accent);
  }

  .qr-wrap {
    position: relative;
    padding: 0.75rem;
    background: white;
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
  }

  .qr-image {
    display: block;
    width: 260px;
    height: 260px;
  }

  .qr-badge {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 0.375rem;
    border-radius: var(--radius-sm);
    color: var(--color-accent);
    box-shadow: var(--shadow-sm);
  }

  .timer {
    width: 100%;
    text-align: center;
  }

  .timer-track {
    height: 4px;
    background: var(--color-bg);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .timer-fill {
    height: 100%;
    background: var(--color-accent);
    transition: width 1s linear;
  }

  .timer p {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.375rem;
    font-size: 0.875rem;
    color: var(--color-text-muted);
  }

  .btn-block {
    width: 100%;
  }

  .steps {
    padding-left: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    font-size: 0.9375rem;
    color: var(--color-text-muted);
    margin-bottom: 1.25rem;
  }

  .note {
    display: flex;
    gap: 0.5rem;
    padding: 0.875rem;
    background: rgba(217, 119, 6, 0.08);
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    color: var(--color-warning);
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
