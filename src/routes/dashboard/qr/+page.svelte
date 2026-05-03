<script>
  import { onMount } from 'svelte';
  import QRCode from 'qrcode';
  import { authStore } from '$lib/stores/auth.js';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import Card from '$lib/components/Card.svelte';
  import { RefreshCw, Clock, ShieldCheck, AlertCircle } from 'lucide-svelte';

  let qrData = $state('');
  let qrImage = $state('');
  let loading = $state(true);
  let timeLeft = $state(60);
  let timer;

  async function generateNewQR() {
    loading = true;
    try {
      const data = await attendanceService.generateQR($authStore.user.id, 'Lunch');
      qrData = data;
      qrImage = await QRCode.toDataURL(data, {
        width: 300,
        margin: 2,
        color: {
          dark: '#0F172A',
          light: '#FFFFFF'
        }
      });
      timeLeft = 60;
      resetTimer();
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
    generateNewQR();
    return () => clearInterval(timer);
  });
</script>

<svelte:head>
  <title>QR Code - Meal Trackers</title>
</svelte:head>

<div class="qr-page fade-in">
  <div class="header">
    <h1>Meal Access QR</h1>
    <p>Present this code at the counter to verify your meal access.</p>
  </div>

  <div class="qr-content">
    <Card>
      <div class="qr-container">
        {#if loading && !qrImage}
          <div class="qr-placeholder">
            <RefreshCw class="animate-spin" size={48} />
          </div>
        {:else}
          <div class="qr-wrapper">
            <img src={qrImage} alt="Meal Access QR Code" class="qr-image" />
            <div class="qr-overlay">
              <ShieldCheck size={40} />
            </div>
          </div>
        {/if}

        <div class="timer-section">
          <div class="timer-bar">
            <div class="timer-progress" style="width: {(timeLeft / 60) * 100}%"></div>
          </div>
          <p class="timer-text">
            <Clock size={16} />
            Code expires in <strong>{timeLeft}s</strong>
          </p>
        </div>

        <button class="btn btn-primary btn-block" onclick={generateNewQR} disabled={loading}>
          <RefreshCw size={20} class={loading ? 'animate-spin' : ''} />
          Regenerate Code
        </button>
      </div>
    </Card>

    <div class="instructions">
      <Card title="How to use">
        <ul class="steps">
          <li>
            <div class="step-num">1</div>
            <p>Ensure your screen brightness is turned up.</p>
          </li>
          <li>
            <div class="step-num">2</div>
            <p>Hold the QR code 10-15cm away from the scanner.</p>
          </li>
          <li>
            <div class="step-num">3</div>
            <p>Wait for the beep or confirmation light.</p>
          </li>
        </ul>
        <div class="warning">
          <AlertCircle size={20} />
          <p>This code is for single use only and expires automatically.</p>
        </div>
      </Card>
    </div>
  </div>
</div>

<style>
  .header {
    margin-bottom: 2rem;
    text-align: center;
  }

  .qr-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    max-width: 900px;
    margin: 0 auto;
  }

  @media (max-width: 768px) {
    .qr-content {
      grid-template-columns: 1fr;
    }
  }

  .qr-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .qr-wrapper {
    position: relative;
    background: white;
    padding: 1rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    margin-bottom: 1.5rem;
  }

  .qr-image {
    width: 100%;
    max-width: 300px;
    display: block;
  }

  .qr-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: white;
    padding: 0.5rem;
    border-radius: 8px;
    color: var(--color-primary);
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
  }

  .qr-placeholder {
    width: 300px;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary);
    background-color: var(--color-bg);
    border-radius: var(--radius-lg);
    margin-bottom: 1.5rem;
  }

  .timer-section {
    width: 100%;
    margin-bottom: 1.5rem;
  }

  .timer-bar {
    height: 4px;
    background-color: var(--color-bg);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .timer-progress {
    height: 100%;
    background-color: var(--color-primary);
    transition: width 1s linear;
  }

  .timer-text {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: var(--color-text-muted);
  }

  .btn-block {
    width: 100%;
  }

  .steps {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .steps li {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .step-num {
    width: 28px;
    height: 28px;
    background-color: var(--color-primary);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
  }

  .warning {
    margin-top: 2rem;
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    background-color: rgba(245, 158, 11, 0.1);
    border-radius: var(--radius-md);
    color: var(--color-accent);
    font-size: 0.875rem;
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
