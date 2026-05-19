import { browser } from '$app/environment';

/**
 * Toggle mock services vs real Django REST API.
 * Set VITE_USE_MOCK=false in .env when the backend is ready.
 */
export const USE_MOCK =
  import.meta.env.VITE_USE_MOCK !== 'false';

/** Backend integration point — set VITE_API_BASE_URL in production */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Base fetch wrapper for Django REST API calls.
 * @param {string} path
 * @param {RequestInit & { token?: string }} [options]
 */
export async function apiFetch(path, options = {}) {
  const { token, headers: customHeaders, ...rest } = options;

  const headers = {
    'Content-Type': 'application/json',
    ...(customHeaders || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else if (browser) {
    try {
      const stored = localStorage.getItem('auth');
      if (stored) {
        const { token: storedToken } = JSON.parse(stored);
        if (storedToken) headers['Authorization'] = `Bearer ${storedToken}`;
      }
    } catch {
      /* ignore parse errors */
    }
  }

  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;

  // Backend integration point — all authenticated API traffic goes through here
  const response = await fetch(url, { headers, ...rest });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || body.message || body.error || message;
    } catch {
      /* use default message */
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  return response.text();
}
