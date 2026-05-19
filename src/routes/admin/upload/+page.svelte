<script>
  import { toastStore } from '$lib/stores/toast.js';
  import Card from '$lib/components/Card.svelte';
  import * as XLSX from 'xlsx';
  import { Upload, FileSpreadsheet, Check, X, AlertCircle, Loader2 } from 'lucide-svelte';

  let dragging = $state(false);
  let file = $state(null);
  let data = $state([]);
  let processing = $state(false);

  let mealAccess = $state({
    breakfast: true,
    lunch: true,
    dinner: false
  });

  function handleFile(f) {
    if (!f.name.match(/\.(xlsx|xls|csv)$/)) {
      toastStore.error('Please upload an Excel or CSV file');
      return;
    }
    file = f;
    parseExcel(f);
  }

  function parseExcel(f) {
    processing = true;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const bstr = e.target.result;
        const wb = XLSX.read(bstr, { type: 'binary' });
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        data = XLSX.utils.sheet_to_json(ws);
        
        if (data.length === 0) {
          toastStore.error('The uploaded file is empty');
          processing = false;
          return;
        }

        // Validate headers if needed
        const headers = Object.keys(data[0] || {});
        const required = ['id', 'name', 'email'];
        const missing = required.filter(h => !headers.some(head => head.toLowerCase().includes(h)));
        
        if (missing.length > 0) {
          toastStore.warn(`Warning: Missing columns: ${missing.join(', ')}`);
        } else {
          toastStore.success(`Successfully parsed ${data.length} rows`);
        }
      } catch (err) {
        toastStore.error('Failed to parse file');
      } finally {
        processing = false;
      }
    };
    reader.readAsBinaryString(f);
  }

  async function uploadData() {
    processing = true;
    const payload = {
      users: data,
      access: mealAccess
    };

    // Backend integration point — POST /api/users/bulk-import/
    console.log('Uploading payload:', payload);

    await new Promise((resolve) => setTimeout(resolve, 2000));
    toastStore.success('Users imported and permissions set!');
    data = [];
    file = null;
    processing = false;
  }
</script>

<svelte:head>
  <title>Bulk Upload - Trackers Admin</title>
</svelte:head>

<div class="admin-content fade-in">
  <header class="page-header">
    <h1>Bulk user import</h1>
    <p>Upload an Excel file to create users and assign event access.</p>
  </header>

  <div class="upload-grid">
    <div class="upload-section">
      <Card>
        <div class="access-config">
          <h3>1. Define Global Access</h3>
          <p>Set which meals these users can access during the event.</p>
          <div class="checkbox-group">
            <label class="checkbox-item">
              <input type="checkbox" bind:checked={mealAccess.breakfast} />
              <span>Breakfast (06:00-11:00)</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" bind:checked={mealAccess.lunch} />
              <span>Lunch (12:00-15:00)</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" bind:checked={mealAccess.dinner} />
              <span>Dinner (19:00-22:00)</span>
            </label>
          </div>
        </div>

        <div class="divider"></div>

        <h3>2. Upload File</h3>
        <div 
          class="dropzone {dragging ? 'dragging' : ''}"
          role="button"
          tabindex="0"
          ondragover={(e) => { e.preventDefault(); dragging = true; }}
          ondragleave={() => dragging = false}
          ondrop={(e) => { e.preventDefault(); dragging = false; handleFile(e.dataTransfer.files[0]); }}
          onclick={() => document.getElementById('fileInput').click()}
          onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); document.getElementById('fileInput').click(); } }}
        >
          <div class="drop-icon">
            <Upload size={48} />
          </div>
          <h3>Click or drag file to upload</h3>
          <p>Columns: ID Number, Full Name, Email, Phone/Reg Number</p>
          <input 
            type="file" 
            id="fileInput" 
            hidden 
            accept=".xlsx,.xls,.csv"
            onchange={(e) => handleFile(e.target.files[0])}
          />
          <button class="btn btn-primary" tabindex="-1">
            Select File
          </button>
        </div>
      </Card>
    </div>

    <div class="info-section">
      <Card title="Required Format">
        <div class="instructions">
          <div class="inst-item">
            <span class="check">
              <Check size={18} />
            </span>
            <p><strong>id:</strong> Unique ID number</p>
          </div>
          <div class="inst-item">
            <span class="check">
              <Check size={18} />
            </span>
            <p><strong>name:</strong> Full Names</p>
          </div>
          <div class="inst-item">
            <span class="check">
              <Check size={18} />
            </span>
            <p><strong>email:</strong> Valid email address</p>
          </div>
          <div class="inst-item">
            <span class="check">
              <Check size={18} />
            </span>
            <p><strong>phone:</strong> Phone or Reg number</p>
          </div>
        </div>
      </Card>
    </div>
  </div>

  {#if file}
    <div class="preview-section fade-in">
      <Card title="File Preview: {file.name}">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                {#if data.length > 0}
                  {#each Object.keys(data[0]) as key}
                    <th>{key}</th>
                  {/each}
                {/if}
              </tr>
            </thead>
            <tbody>
              {#each data.slice(0, 5) as row}
                <tr>
                  {#each Object.values(row) as val}
                    <td>{val}</td>
                  {/each}
                </tr>
              {/each}
              {#if data.length > 5}
                <tr>
                  <td colspan="100" class="more-rows">And {data.length - 5} more rows...</td>
                </tr>
              {/if}
            </tbody>
          </table>
        </div>
        
        <div class="preview-footer">
          <button class="btn btn-outline" onclick={() => { file = null; data = []; }}>
            <X size={18} />
            Cancel
          </button>
          <button class="btn btn-primary" onclick={uploadData} disabled={processing}>
            {#if processing}
              <span class="animate-spin">
                <Loader2 size={18} />
              </span>
              Processing...
            {:else}
              <Check size={18} />
              Confirm & Set Access ({data.length} users)
            {/if}
          </button>
        </div>
      </Card>
    </div>
  {/if}
</div>

<style>
  .access-config { margin-bottom: 2rem; }
  .access-config h3 { margin-bottom: 0.5rem; font-size: 1.125rem; }
  .access-config p { color: var(--color-text-muted); font-size: 0.875rem; margin-bottom: 1.25rem; }

  .checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    background-color: var(--color-bg);
    padding: 1.5rem;
    border-radius: var(--radius-md);
  }

  .checkbox-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
  }

  .checkbox-item input {
    width: 20px;
    height: 20px;
    accent-color: var(--color-accent);
  }

  .divider {
    height: 1px;
    background-color: var(--color-border);
    margin: 2rem 0;
  }

  .upload-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
  }

  @media (max-width: 1024px) {
    .upload-grid { grid-template-columns: 1fr; }
  }

  .dropzone {
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-lg);
    padding: 3rem 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    background-color: var(--color-bg);
    transition: all 0.2s;
    text-align: center;
    cursor: pointer;
  }

  .dropzone:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }

  .dropzone.dragging {
    border-color: var(--color-accent);
    background-color: rgba(229, 77, 56, 0.05);
  }

  .drop-icon {
    width: 80px;
    height: 80px;
    background-color: var(--color-surface);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-accent);
    box-shadow: var(--shadow-sm);
  }

  .preview-section { margin-top: 2.5rem; }

  .table-container {
    overflow-x: auto;
    margin: 1.5rem 0;
    max-height: 400px;
  }

  table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  th { padding: 0.75rem 1rem; background-color: var(--color-bg); text-align: left; font-weight: 600; }
  td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--color-bg); }

  .preview-footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border);
  }

  @media (max-width: 479px) {
    .preview-footer {
      flex-direction: column;
    }

    .preview-footer .btn {
      width: 100%;
      justify-content: center;
    }
  }

  .instructions { display: flex; flex-direction: column; gap: 1.25rem; }
  .inst-item { display: flex; gap: 0.75rem; font-size: 0.875rem; }
  .inst-item .check { color: var(--color-success); }

  .animate-spin { animation: spin 1s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
