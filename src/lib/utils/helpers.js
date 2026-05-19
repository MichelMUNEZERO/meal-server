import { MEAL_WINDOWS } from './constants.js';

/**
 * Returns the active meal window for the current time, if any.
 * @param {Date} [now]
 */
export function getCurrentMealWindow(now = new Date()) {
  const hour = now.getHours();
  return MEAL_WINDOWS.find((m) => hour >= m.start && hour < m.end) ?? null;
}

/**
 * @param {number} current
 * @param {number} total
 */
export function progressPercent(current, total) {
  if (!total || total <= 0) return 0;
  return Math.min(100, Math.round((current / total) * 100));
}

/**
 * @param {unknown[]} items
 * @param {number} page 1-based
 * @param {number} pageSize
 */
export function paginate(items, page, pageSize) {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(1, page), totalPages);
  const start = (safePage - 1) * pageSize;
  return {
    items: items.slice(start, start + pageSize),
    page: safePage,
    totalPages,
    total,
    start: total === 0 ? 0 : start + 1,
    end: Math.min(start + pageSize, total)
  };
}

/**
 * @param {string} value
 */
export function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

/**
 * @param {string} password
 */
export function isStrongPassword(password) {
  return password.length >= 8;
}
