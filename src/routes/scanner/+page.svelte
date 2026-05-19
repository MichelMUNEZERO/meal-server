<script>
  import { toastStore } from '$lib/stores/toast.js';
  import { scannerSession } from '$lib/stores/scannerSession.js';
  import { attendanceService } from '$lib/services/attendance.service.js';
  import { getCurrentMealWindow } from '$lib/utils/helpers.js';
  import Card from '$lib/components/Card.svelte';
  import { CheckCircle2, XCircle, Clock, Loader2, History } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  let scanInput = $state('');
  let processing = $state(false);
  let html5Qrcode = null;
  let activeMeal = $state(getCurrentMealWindow());

  onMount(() => {
    // Update active meal every minute
    const interval = setInterval(() => {
      activeMeal = getCurrentMealWindow();
    }, 60000);

    // Initialize QR Scanner when running in browser
    if (browser) {
      import('html5-qrcode').then(({ Html5Qrcode }) => {
        html5Qrcode = new Html5Qrcode("reader");
        startScanner();
      });
    }

    return () => {
      clearInterval(interval);
      if (html5Qrcode && html5Qrcode.isScanning) {
        html5Qrcode.stop().catch(console.error);
      }
    };
  });

  function startScanner() {
    if (!html5Qrcode || !activeMeal) return;
    
    // config for html5-qrcode
    const config = { fps: 10, qrbox: { width: 250, height: 250 } };
    
    html5Qrcode.start(
      { facingMode: "environment" },
      config,
      (decodedText) => {
        // On success, prevent rapid consecutive scans of the same or during processing
        if (!processing) {
            scanInput = decodedText;
            handleScan();
        }
      },
      (errorMessage) => {
        // parse error, ignore mostly as it scans continuously
      }
    ).catch((err) => {
      console.error("Failed to start scanner:", err);
    });
  }

  async function handleScan() {
    if (!scanInput || processing) return;

    processing = true;

    try {
      if (!activeMeal) {
        throw new Error('No meal session is active right now.');
      }

      // Backend integration point — verify QR with Django
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

  function formatTime(date) {
    return new Intl.DateTimeFormat('default', {
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric'
    }).format(date);
  }
</script>

<svelte:head>
  <title>Dashboard - Meal Trackers</title>
</svelte:head>

<div class="dashboard-page fade-in">
  <!-- Status Indicator: Spans the width of the main content area -->
  <div class="status-banner {activeMeal ? 'active' : 'inactive'}">
    {#if activeMeal}
      <Clock size={20} />
      <span>Current Session: <strong>{activeMeal.type}</strong> ({activeMeal.start}:00 - {activeMeal.end}:00)</span>
      <span class="status-badge live">Scanning Active</span>
    {:else}
      <Clock size={20} />
      <span>No active meal session at this time.</span>
    {/if}
  </div>

  <div class="dashboard-grid">
    <!-- Left Column: Active Scanner -->
    <div class="scanner-column">
      <Card class="h-full">
        <div class="scan-area">
          <div class="scan-header">
            <h3>QR Code Scanner</h3>
            <span class="live-indicator {activeMeal ? 'pulse' : ''}"></span>
          </div>
          
          <div class="scan-visual-container">
            {#if processing}
              <div class="processing-overlay">
                <span class="animate-spin">
                  <Loader2 size={48} />
                </span>
                <p>Verifying...</p>
              </div>
            {/if}
            
            <div id="reader" class="scanner-viewport {processing ? 'dim' : ''}"></div>
            
            <!-- Fallback styling if reader is not yet initialized visually -->
            <div class="scanner-borders">
               <div class="corner top-left"></div>
               <div class="corner top-right"></div>
               <div class="corner bottom-left"></div>
               <div class="corner bottom-right"></div>
            </div>
          </div>

          <div class="input-section">
            <p class="hint">Or simulate scan by pasting data manually:</p>
            <div class="input-wrapper">
              <input 
                type="text" 
                class="input" 
                placeholder="Paste payload..." 
                bind:value={scanInput}
                onkeydown={(e) => e.key === 'Enter' && handleScan()}
                disabled={processing || !activeMeal}
              />
              <button 
                class="btn btn-primary" 
                onclick={handleScan} 
                disabled={processing || !scanInput || !activeMeal}
              >
                Verify
              </button>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Right Column: Scan History -->
    <div class="history-column">
      <Card class="h-full">
        <div class="history-header">
          <h3>Session Scans</h3>
          <span class="history-count">{$scannerSession.scanHistory.length} Scans</span>
        </div>
        
        <div class="history-list-wrapper">
          <div class="history-list">
            {#if $scannerSession.scanHistory.length === 0}
              <div class="empty-history">
                <div class="icon-bg">
                  <History size={32} />
                </div>
                <p>No scans yet.</p>
                <span class="sub-hint">Scanned users will appear here in real-time.</span>
              </div>
            {:else}
              {#each $scannerSession.scanHistory as scan}
                <div class="history-item {scan.success ? 'success' : 'error'} slide-in">
                  <div class="item-icon">
                    {#if scan.success}
                      <CheckCircle2 size={24} />
                    {:else}
                      <XCircle size={24} />
                    {/if}
                  </div>
                  <div class="item-details">
                    <span class="item-name">{scan.user?.name}</span>
                    <span class="item-time">{formatTime(scan.timestamp)}</span>
                  </div>
                  <div class="item-status">
                    {#if scan.success}
                      <span class="badge success-badge">Granted</span>
                    {:else}
                      <span class="badge error-badge">Denied</span>
                    {/if}
                  </div>
                </div>
              {/each}
            {/if}
          </div>
        </div>
      </Card>
    </div>
  </div>
</div>

<style>
  /* Base Dashboard Layout */
  .dashboard-page {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    height: calc(100vh - 120px); /* Fill available space */
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
    width: 100%;
  }

  .status-banner.active {
    border-left: 4px solid var(--color-success);
    color: var(--color-primary);
  }

  .status-banner.inactive {
    border-left: 4px solid var(--color-accent);
    color: var(--color-text-muted);
  }

  .status-badge {
    margin-left: auto;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-sm);
  }

  .status-badge.live {
    background-color: rgba(46, 204, 113, 0.15);
    color: var(--color-success);
  }

  /* Two Column Grid */
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    flex: 1;
    min-height: 0; /* Important for scrollable children */
  }

  @media (max-width: 900px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
      height: auto;
    }
    .dashboard-page {
      height: auto;
    }
  }

  /* Left Column: Scanner */
  .scan-area {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 1.5rem;
  }

  .scan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .scan-header h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .live-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: var(--color-text-muted);
  }

  .live-indicator.pulse {
    background-color: var(--color-accent);
    box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
    animation: pulse-red 2s infinite;
  }

  @keyframes pulse-red {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
  }

  .scan-visual-container {
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
    background-color: #000;
    border-radius: var(--radius-lg);
    overflow: hidden;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .scanner-viewport {
    width: 100%;
    height: 100%;
  }

  /* Target html5-qrcode specific elements if needed to clean up their default UI */
  :global(#reader video) {
    object-fit: cover !important;
  }
  :global(#reader__dashboard_section_csr) {
    padding: 10px !important;
    background: white;
  }
  :global(#reader a) {
    display: none !important;
  }

  .processing-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(26, 42, 58, 0.85); /* Primary color with opacity */
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    gap: 1rem;
    font-weight: 600;
  }

  .dim { opacity: 0.3; }

  /* Decorative scanner borders */
  .scanner-borders .corner {
    position: absolute;
    width: 30px;
    height: 30px;
    border-color: var(--color-accent);
    border-style: solid;
    z-index: 5;
    pointer-events: none;
  }
  .scanner-borders .top-left { top: 20px; left: 20px; border-width: 3px 0 0 3px; }
  .scanner-borders .top-right { top: 20px; right: 20px; border-width: 3px 3px 0 0; }
  .scanner-borders .bottom-left { bottom: 20px; left: 20px; border-width: 0 0 3px 3px; }
  .scanner-borders .bottom-right { bottom: 20px; right: 20px; border-width: 0 3px 3px 0; }

  .input-section {
    margin-top: auto;
  }

  .hint {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    margin-bottom: 0.5rem;
  }

  .input-wrapper {
    display: flex;
    gap: 0.5rem;
  }

  /* Right Column: History */
  .history-column :global(.card) {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .history-header h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .history-count {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-accent);
    background-color: rgba(255, 107, 107, 0.1);
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-full);
  }

  .history-list-wrapper {
    flex: 1;
    overflow-y: auto;
    padding: 0;
  }

  .history-list {
    display: flex;
    flex-direction: column;
  }

  .empty-history {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: var(--color-text-muted);
  }

  .icon-bg {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background-color: var(--color-surface);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .empty-history p {
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: 0.25rem;
  }

  .sub-hint {
    font-size: 0.8125rem;
  }

  .history-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--color-border);
    transition: background-color 0.2s;
  }

  .history-item:hover {
    background-color: var(--color-surface);
  }

  .history-item.success .item-icon { color: var(--color-success); }
  .history-item.error .item-icon { color: var(--color-accent); }

  .item-details {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .item-name {
    font-weight: 600;
    color: var(--color-primary);
  }

  .item-time {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .badge {
    font-size: 0.6875rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-sm);
  }

  .success-badge {
    background-color: rgba(46, 204, 113, 0.15);
    color: var(--color-success);
  }

  .error-badge {
    background-color: rgba(255, 107, 107, 0.15);
    color: var(--color-accent);
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .slide-in {
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }
</style>
