import { apiFetch, USE_MOCK } from './api.js';
import { mockUsers } from './mock-data.js';

let mockUsersStore = [...mockUsers];

function delay(ms = 400) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export const usersService = {
  /** Backend integration point */
  getAll: async () => {
    if (USE_MOCK) {
      await delay();
      return [...mockUsersStore];
    }
    return apiFetch('/users/');
  },

  /** Backend integration point */
  getById: async (id) => {
    if (USE_MOCK) {
      await delay();
      const user = mockUsersStore.find((u) => u.id === id);
      if (!user) throw new Error('User not found');
      return user;
    }
    return apiFetch(`/users/${id}/`);
  },

  /** Backend integration point */
  update: async (id, payload) => {
    if (USE_MOCK) {
      await delay();
      mockUsersStore = mockUsersStore.map((u) =>
        u.id === id ? { ...u, ...payload } : u
      );
      const updated = mockUsersStore.find((u) => u.id === id);
      if (!updated) throw new Error('User not found');
      return updated;
    }
    return apiFetch(`/users/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
  },

  /**
   * Request password reset email (forgot-password flow).
   * Backend integration point
   */
  requestPasswordReset: async (email) => {
    if (USE_MOCK) {
      await delay(600);
      return { success: true, message: 'If an account exists, a reset link was sent.' };
    }
    return apiFetch('/auth/password-reset/', {
      method: 'POST',
      body: JSON.stringify({ email })
    });
  },

  /**
   * Reset password with token from email link.
   * Backend integration point
   */
  resetPasswordWithToken: async (token, newPassword) => {
    if (USE_MOCK) {
      await delay(600);
      if (!token || newPassword.length < 8) {
        throw new Error('Invalid token or password too short');
      }
      return { success: true };
    }
    return apiFetch('/auth/password-reset/confirm/', {
      method: 'POST',
      body: JSON.stringify({ token, password: newPassword })
    });
  },

  /**
   * Authenticated user changes own password.
   * Backend integration point
   */
  changePassword: async (currentPassword, newPassword) => {
    if (USE_MOCK) {
      await delay(600);
      if (!currentPassword || newPassword.length < 8) {
        throw new Error('Please provide a valid current and new password (min 8 characters)');
      }
      return { success: true };
    }
    return apiFetch('/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });
  },

  /**
   * Admin triggers reset email for a user.
   * Backend integration point
   */
  adminSendPasswordReset: async (userId) => {
    if (USE_MOCK) {
      await delay(500);
      const user = mockUsersStore.find((u) => u.id === userId);
      if (!user) throw new Error('User not found');
      return { success: true, email: user.email };
    }
    return apiFetch(`/users/${userId}/send-password-reset/`, { method: 'POST' });
  }
};
