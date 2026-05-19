import { goto } from '$app/navigation';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth.js';
import { ROLES } from './constants.js';

/**
 * Client-side route guard. Server hooks should mirror this when Django auth exists.
 * @param {string} requiredRole
 * @param {string} [redirectTo='/login']
 * @returns {boolean}
 */
export function requireRole(requiredRole, redirectTo = '/login') {
  const state = get(authStore);

  if (!state.isAuthenticated) {
    goto(redirectTo);
    return false;
  }

  if (state.role !== requiredRole) {
    if (state.role === ROLES.ADMIN) goto('/admin');
    else if (state.role === ROLES.SCANNER) goto('/scanner');
    else goto('/dashboard');
    return false;
  }

  return true;
}

/**
 * @param {string[]} allowedRoles
 */
export function requireAnyRole(allowedRoles, redirectTo = '/login') {
  const state = get(authStore);

  if (!state.isAuthenticated) {
    goto(redirectTo);
    return false;
  }

  if (!allowedRoles.includes(state.role)) {
    if (state.role === ROLES.ADMIN) goto('/admin');
    else if (state.role === ROLES.SCANNER) goto('/scanner');
    else goto('/dashboard');
    return false;
  }

  return true;
}
