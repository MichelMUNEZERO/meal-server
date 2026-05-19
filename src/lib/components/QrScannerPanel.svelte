<script>
  /**
   * Camera QR scanner + manual verify — used by scanner and admin roles.
   */
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { toastStore } from '$lib/stores/toast.js';
  import { scannerSession } from '$lib/stores/scannerSession.js';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import { getCurrentMealWindow } from '$lib/utils/helpers.js';
  import Card from '$lib/components/Card.svelte';
  import { Clock, Loader2, RefreshCw } from 'lucide-svelte';

  let { compact = false } = $props();

  let scanInput = $state('');
  let processing = $state(false);
  let html5Qrcode = null;
  let activeMeal = $state(getCurrentMealWindow());
  const readerId = 'qr-reader-' + Math.random().toString(36).slice(2, 9);

  onMount(() => {
    const interval = setInterval(() => {
      activeMeal = getCurrentMealWindow();
    }, 60000);

    if (browser) {
      import('html5-qrcode').then(({ Html5Qrcode }) => {
        html5Qrcode = new Html5Qrcode(readerId);
        startScanner();
      });
    }

    return () => {
      clearInterval(interval);
      if (html5Qrcode?.isScanning) {
        html5Qrcode.stop().catch(() => {});
      }
    };
  });

  function startScanner() {
    if (!html5Qrcode || !activeMeal) return;

    html5Qrcode
      .start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 220, height: 220 } },
        (decodedText) => {
          if (!processing) {
            scanInput = decodedText;
            handleScan();
          }
        },
        () => {}
      )
      .catch((err) => {
        console.error('Scanner start failed:', err);
        toastStore.error('Could not access camera. Use manual entry below.');
      });
  }

  async function handleScan() {
    if (!scanInput || processing) return;
    processing = true;

    try {
      if (!activeMeal) {
        throw new Error('No meal session is active right now.');
      }

      // Backend integration point
      const verified = await attendanceService.verifyScan(scanInput);
      const result = {
        success: true,
        message: 'Check-in successful',
        user: { name: verified.user.name, id: verified.user.id }
      };
      toastStore.success(`${verified.user.name} — ${verified.mealType}`);
      scannerSession.addScan(result);
    } catch (err) {
      const result = {
        success: false,
        message: err.message || 'Invalid QR code',
        user: { name: 'Unknown', id: '—' }
      };
      toastStore.error(result.message);
      scannerSession.addScan(result);
    } finally {
      processing = false;
      scanInput = '';
    }
  }
</script>

<div class="scanner-panel" class:compact>
  <div class="session-banner" class:active={!!activeMeal}>
    <Clock size={18} />
    {#if activeMeal}
      <span>Active: <strong>{activeMeal.type}</strong> ({activeMeal.start}:00–{activeMeal.end}:00)</span>
    {:else}
      <span>No meal window active right now</span>
    {/if}
  </div>

  <Card>
    <div class="scan-body">
      <h3>Scan QR code</h3>

      <div class="viewport-wrap">
        {#if processing}
          <div class="processing">
            <Loader2 size={40} class="spin" />
            <p>Verifying…</p>
          </div>
        {/if}
        <div id={readerId} class="viewport" class:dim={processing}></div>
      </div>

      <p class="hint">Or paste a code manually:</p>
      <div class="manual-row">
        <input
          type="text"
          class="input"
          placeholder="Paste QR payload…"
          bind:value={scanInput}
          disabled={processing || !activeMeal}
          onkeydown={(e) => e.key === 'Enter' && handleScan()}
        />
        <button
          type="button"
          class="btn btn-primary"
          onclick={handleScan}
          disabled={processing || !scanInput || !activeMeal}
        >
          Verify
        </button>
      </div>
    </div>
  </Card>
</div>

<style>
  .scanner-panel {
    width: 100%;
  }

  .session-banner {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    border-radius: var(--radius-md);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    font-size: 0.875rem;
    color: var(--color-text-muted);
  }

  .session-banner.active {
    border-left: 3px solid var(--color-success);
    color: var(--color-text);
  }

  .scan-body h3 {
    font-size: 1rem;
    margin-bottom: 1rem;
  }

  .viewport-wrap {
    position: relative;
    width: 100%;
    max-width: 320px;
    margin: 0 auto 1rem;
    aspect-ratio: 1;
    background: #0f172a;
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .viewport {
    width: 100%;
    height: 100%;
  }

  .viewport.dim {
    opacity: 0.4;
  }

  .processing {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.85);
    color: white;
    z-index: 2;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  :global(.viewport video) {
    object-fit: cover !important;
    width: 100% !important;
    height: 100% !important;
  }

  :global([id^='qr-reader-'] a) {
    display: none !important;
  }

  .hint {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    margin-bottom: 0.5rem;
  }

  .manual-row {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  @media (min-width: 480px) {
    .manual-row {
      flex-direction: row;
    }

    .manual-row .input {
      flex: 1;
      min-width: 0;
    }
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
