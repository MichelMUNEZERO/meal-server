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
      // Set this session as the active one for this user globally across tabs
      localStorage.setItem(`active_session_${userData.id}`, sessionId);
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

    const checkSession = () => {
      const state = get(auth);
      if (state.isAuthenticated && state.user?.id) {
        const activeGlobalSession = localStorage.getItem(`active_session_${state.user.id}`);
        // If the global active session exists and doesn't match our current session, force logout
        if (activeGlobalSession && activeGlobalSession !== state.sessionId) {
          console.warn('Session invalidated by login on another device.');
          authStore.logout();
        }
      }
    };

    // Periodic polling as a fallback
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
