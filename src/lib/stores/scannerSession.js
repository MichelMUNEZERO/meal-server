import { writable } from 'svelte/store';

const initialState = {
  scanHistory: [],
  totalScans: 0
};

function createScannerSession() {
  const { subscribe, set, update } = writable(initialState);

  return {
    subscribe,
    addScan: (result) => update(state => {
      // Add the new scan at the beginning of the history
      const newHistory = [
        { ...result, timestamp: new Date() },
        ...state.scanHistory
      ];
      
      return {
        scanHistory: newHistory,
        // Only increment total scans if the check-in was successful
        totalScans: result.success ? state.totalScans + 1 : state.totalScans
      };
    }),
    clearSession: () => set(initialState)
  };
}

export const scannerSession = createScannerSession();
