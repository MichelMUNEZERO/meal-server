import { writable } from 'svelte/store';

const toasts = writable([]);

export const toastStore = {
  subscribe: toasts.subscribe,
  add: (message, type = 'info', duration = 3000) => {
    const id = Math.random().toString(36).substring(2, 9);
    toasts.update((all) => [{ id, message, type }, ...all]);
    
    if (duration > 0) {
      setTimeout(() => {
        toastStore.remove(id);
      }, duration);
    }
    return id;
  },
  remove: (id) => {
    toasts.update((all) => all.filter((t) => t.id !== id));
  },
  success: (message, duration) => toastStore.add(message, 'success', duration),
  error: (message, duration) => toastStore.add(message, 'error', duration),
  warning: (message, duration) => toastStore.add(message, 'warning', duration)
};
