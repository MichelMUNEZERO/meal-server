import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  role: null // 'user', 'admin', or 'scanner'
};

const storedAuth = browser ? localStorage.getItem('auth') : null;
const auth = writable(storedAuth ? JSON.parse(storedAuth) : initialState);

if (browser) {
  auth.subscribe((value) => {
    localStorage.setItem('auth', JSON.stringify(value));
  });
}

export const authStore = {
  subscribe: auth.subscribe,
  login: (userData, token) => {
    auth.set({
      user: userData,
      token: token,
      isAuthenticated: true,
      role: userData.role || 'user'
    });
  },
  logout: () => {
    auth.set(initialState);
    if (browser) {
      localStorage.removeItem('auth');
    }
  }
};
