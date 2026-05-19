/** Shared app constants — safe for client and server imports */

export const ROLES = {
  USER: 'user',
  ADMIN: 'admin',
  SCANNER: 'scanner'
};

export const MEAL_TYPES = {
  BREAKFAST: 'Breakfast',
  LUNCH: 'Lunch',
  DINNER: 'Dinner'
};

export const MEAL_WINDOWS = [
  { type: MEAL_TYPES.BREAKFAST, start: 6, end: 11 },
  { type: MEAL_TYPES.LUNCH, start: 12, end: 15 },
  { type: MEAL_TYPES.DINNER, start: 19, end: 22 }
];

export const QR_EXPIRY_SECONDS = 60;

export const PAGINATION_DEFAULT_SIZE = 10;
