import { apiFetch, USE_MOCK } from './api.js';
import { mockAttendance } from './mock-data.js';
import { getCurrentMealWindow } from '$lib/utils/helpers.js';

function delay(ms = 400) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Canonical QR payload shape shared between user app and scanner.
 * @param {string} userId
 * @param {string} userName
 * @param {string} mealType
 */
export function buildQRPayload(userId, userName, mealType) {
  const timestamp = Date.now();
  return {
    userId,
    userName,
    mealType,
    timestamp,
    // Backend integration point — replace with server-signed token
    signature: `mock-sig-${timestamp}`
  };
}

export const attendanceService = {
  /**
   * Backend integration point
   * @param {string} [userId]
   */
  getHistory: async (userId) => {
    if (USE_MOCK) {
      await delay();
      if (userId) return mockAttendance.filter((a) => a.userId === userId);
      return [...mockAttendance];
    }
    const path = userId ? `/attendance/?user=${userId}` : '/attendance/';
    return apiFetch(path);
  },

  /**
   * Backend integration point
   * @param {string} userId
   * @param {string} userName
   * @param {string} [mealType]
   */
  generateQR: async (userId, userName, mealType) => {
    const active = mealType || getCurrentMealWindow()?.type || 'Lunch';

    if (USE_MOCK) {
      await delay(300);
      return JSON.stringify(buildQRPayload(userId, userName, active));
    }

    const data = await apiFetch('/attendance/qr/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, meal_type: active })
    });
    return typeof data === 'string' ? data : JSON.stringify(data);
  },

  /**
   * Scanner verifies a scanned QR code.
   * Backend integration point
   * @param {string} rawPayload
   */
  verifyScan: async (rawPayload) => {
    if (USE_MOCK) {
      await delay(600);
      let parsed;
      try {
        parsed = JSON.parse(rawPayload);
      } catch {
        throw new Error('Invalid QR code format');
      }

      const active = getCurrentMealWindow();
      if (!active) throw new Error('No meal session is active right now');

      if (parsed.mealType && parsed.mealType !== active.type) {
        throw new Error(`This QR is for ${parsed.mealType}, not ${active.type}`);
      }

      return {
        success: true,
        user: {
          id: parsed.userId,
          name: parsed.userName || 'Guest'
        },
        mealType: parsed.mealType || active.type
      };
    }

    return apiFetch('/attendance/verify/', {
      method: 'POST',
      body: JSON.stringify({ payload: rawPayload })
    });
  }
};
