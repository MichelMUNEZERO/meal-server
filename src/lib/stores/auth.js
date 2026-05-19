import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  role: null,
  sessionId: null
};

const storedAuth = browser ? localStorage.getItem('auth') : null;

function parseStoredAuth() {
  if (!storedAuth) return initialState;
  try {
    return JSON.parse(storedAuth);
  } catch {
    return initialState;
  }
}

const auth = writable(parseStoredAuth());

if (browser) {
  auth.subscribe((value) => {
    if (value.isAuthenticated) {
      localStorage.setItem('auth', JSON.stringify(value));
    }
  });
}

function generateSessionId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

export const authStore = {
  subscribe: auth.subscribe,

  login: (userData, token) => {
    const sessionId = generateSessionId();

    auth.set({
      user: userData,
      token,
      isAuthenticated: true,
      role: userData.role || 'user',
      sessionId
    });

    if (browser && userData.id) {
      localStorage.setItem(`active_session_${userData.id}`, sessionId);

      // Backend integration point — sync session with Django when multi-device rules apply
      fetch('/api/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: userData.id, sessionId })
      }).catch(() => {});
    }
  },

  logout: async () => {
    const state = get(auth);

    if (browser && state.user?.id) {
      localStorage.removeItem(`active_session_${state.user.id}`);
    }

    auth.set(initialState);

    if (browser) {
      localStorage.removeItem('auth');
    }

    // Backend integration point — invalidate refresh token on Django
    try {
      const { authService } = await import('$lib/services/auth.service.js');
      await authService.logout();
    } catch {
      /* ignore logout API errors locally */
    }
  },

  initSessionListener: () => {
    if (!browser) return;

    const checkSession = async () => {
      const state = get(auth);
      if (!state.isAuthenticated || !state.user?.id) return;

      let shouldLogout = false;
      const activeGlobalSession = localStorage.getItem(`active_session_${state.user.id}`);

      if (activeGlobalSession && activeGlobalSession !== state.sessionId) {
        shouldLogout = true;
      }

      if (!shouldLogout) {
        try {
          const res = await fetch(`/api/session?userId=${state.user.id}`);
          if (res.ok) {
            const data = await res.json();
            if (data.success && data.activeSession && data.activeSession !== state.sessionId) {
              shouldLogout = true;
            }
          }
        } catch {
          /* network errors ignored in mock mode */
        }
      }

      if (shouldLogout) {
        authStore.logout();
      }
    };

    const interval = setInterval(checkSession, 5000);

    window.addEventListener('storage', (event) => {
      const state = get(auth);
      if (state.isAuthenticated && state.user?.id && event.key === `active_session_${state.user.id}`) {
        checkSession();
      }
    });

    return () => clearInterval(interval);
  }
};
