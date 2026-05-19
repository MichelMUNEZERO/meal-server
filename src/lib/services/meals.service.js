import { apiFetch, USE_MOCK } from './api.js';
import { mockUser } from './mock-data.js';

function delay(ms = 400) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** @type {Record<string, import('./mock-data.js').MealPlanConfig>} */
const mockMealPlans = {
  u1: { ...mockUser.mealPlan },
  u2: { breakfast: true, lunch: true, dinner: true, daysRemaining: 22, totalDays: 30 },
  u3: { breakfast: false, lunch: false, dinner: false, daysRemaining: 0, totalDays: 30 }
};

export const mealsService = {
  /** Backend integration point */
  getPlanForUser: async (userId) => {
    if (USE_MOCK) {
      await delay();
      return mockMealPlans[userId] || {
        breakfast: false,
        lunch: false,
        dinner: false,
        daysRemaining: 0,
        totalDays: 30
      };
    }
    return apiFetch(`/users/${userId}/meal-plan/`);
  },

  /** Backend integration point */
  updatePlanForUser: async (userId, plan) => {
    if (USE_MOCK) {
      await delay();
      mockMealPlans[userId] = { ...mockMealPlans[userId], ...plan };
      return mockMealPlans[userId];
    }
    return apiFetch(`/users/${userId}/meal-plan/`, {
      method: 'PUT',
      body: JSON.stringify(plan)
    });
  },

  /** Backend integration point */
  getAllPlans: async () => {
    if (USE_MOCK) {
      await delay();
      return { ...mockMealPlans };
    }
    return apiFetch('/meal-plans/');
  }
};
