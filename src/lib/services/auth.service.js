import { apiFetch, USE_MOCK } from './api.js';
import { mockUser, mockAdmin, mockScanner, MOCK_CREDENTIALS } from './mock-data.js';

function delay(ms = 500) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export const authService = {
  /**
   * Backend integration point — POST /api/auth/login/
   * @param {string} email
   * @param {string} password
   */
  login: async (email, password) => {
    if (USE_MOCK) {
      await delay(700);
      const normalized = email.trim().toLowerCase();

      if (
        normalized === MOCK_CREDENTIALS.user.email &&
        password === MOCK_CREDENTIALS.user.password
      ) {
        return { user: mockUser, token: 'mock-user-token' };
      }
      if (
        normalized === MOCK_CREDENTIALS.admin.email &&
        password === MOCK_CREDENTIALS.admin.password
      ) {
        return { user: mockAdmin, token: 'mock-admin-token' };
      }
      if (
        normalized === MOCK_CREDENTIALS.scanner.email &&
        password === MOCK_CREDENTIALS.scanner.password
      ) {
        return { user: mockScanner, token: 'mock-scanner-token' };
      }
      throw new Error('Invalid email or password');
    }

    const data = await apiFetch('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    return { user: data.user, token: data.access || data.token };
  },

  /** Backend integration point */
  logout: async () => {
    if (USE_MOCK) {
      await delay(200);
      return true;
    }
    return apiFetch('/auth/logout/', { method: 'POST' });
  }
};
