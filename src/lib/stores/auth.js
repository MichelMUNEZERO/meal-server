import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  role: null, // 'user', 'admin', or 'scanner'
  sessionId: null
};

const storedAuth = browser ? localStorage.getItem('auth') : null;
const auth = writable(storedAuth ? JSON.parse(storedAuth) : initialState);

if (browser) {
  auth.subscribe((value) => {
    localStorage.setItem('auth', JSON.stringify(value));
  });
}

function generateSessionId() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export const authStore = {
  subscribe: auth.subscribe,
  login: (userData, token) => {
    const sessionId = generateSessionId();
    
    auth.set({
      user: userData,
      token: token,
      isAuthenticated: true,
      role: userData.role || 'user',
      sessionId: sessionId
    });

    if (browser && userData.id) {
      // 1. Instant cross-tab sync using localStorage
      localStorage.setItem(`active_session_${userData.id}`, sessionId);

      // 2. Cross-browser sync using our backend API
      fetch('/api/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: userData.id, sessionId })
      }).catch(err => console.error('Failed to sync session with server:', err));
    }
  },
  logout: () => {
    auth.set(initialState);
    if (browser) {
      localStorage.removeItem('auth');
    }
  },
  // Call this function when the app mounts to set up cross-device/cross-tab logout
  initSessionListener: () => {
    if (!browser) return;

    const checkSession = async () => {
      const state = get(auth);
      if (state.isAuthenticated && state.user?.id) {
        let shouldLogout = false;

        // Check 1: Local Storage (Instant cross-tab detection)
        const activeGlobalSession = localStorage.getItem(`active_session_${state.user.id}`);
        if (activeGlobalSession && activeGlobalSession !== state.sessionId) {
          shouldLogout = true;
        }

        // Check 2: Backend API (Cross-browser / Cross-device detection)
        if (!shouldLogout) {
          try {
            const res = await fetch(`/api/session?userId=${state.user.id}`);
            if (res.ok) {
              const data = await res.json();
              if (data.success && data.activeSession && data.activeSession !== state.sessionId) {
                shouldLogout = true;
              }
            }
          } catch (e) {
            // Ignore network errors silently
          }
        }

        if (shouldLogout) {
          console.warn('Session invalidated by login on another device.');
          authStore.logout();
        }
      }
    };

    // Periodic polling to check the server (every 3 seconds)
    setInterval(checkSession, 3000);

    // Listen for real-time storage events from other tabs
    window.addEventListener('storage', (event) => {
      const state = get(auth);
      if (state.isAuthenticated && state.user?.id) {
        if (event.key === `active_session_${state.user.id}`) {
          checkSession();
        }
      }
    });
  }
};
