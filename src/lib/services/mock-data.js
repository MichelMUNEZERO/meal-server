export const mockUser = {
  id: 'u1',
  name: 'Michel Munezero',
  email: 'michel@example.com',
  role: 'user',
  mealPlan: {
    breakfast: true,
    lunch: true,
    dinner: false,
    daysRemaining: 15,
    totalDays: 30,
    validUntil: '2026-05-30'
  }
};

export const mockAdmin = {
  id: 'a1',
  name: 'Admin User',
  email: 'admin@trackers.com',
  role: 'admin'
};

export const mockScanner = {
  id: 's1',
  name: 'Scanner Agent',
  email: 'scanner@trackers.com',
  role: 'scanner'
};

export const mockAttendance = [
  { id: 'att1', userId: 'u1', userName: 'Michel Munezero', date: '2026-05-01', time: '08:15', type: 'Breakfast', status: 'Present' },
  { id: 'att2', userId: 'u1', userName: 'Michel Munezero', date: '2026-05-01', time: '13:05', type: 'Lunch', status: 'Present' },
  { id: 'att3', userId: 'u1', userName: 'Michel Munezero', date: '2026-04-30', time: '08:20', type: 'Breakfast', status: 'Present' },
  { id: 'att4', userId: 'u2', userName: 'John Doe', date: '2026-05-01', time: '13:15', type: 'Lunch', status: 'Present' }
];

export const mockUsers = [
  { id: 'u1', name: 'Michel Munezero', email: 'michel@example.com', role: 'user', status: 'Active', plan: 'B/L' },
  { id: 'u2', name: 'John Doe', email: 'john@example.com', role: 'user', status: 'Active', plan: 'B/L/D' },
  { id: 'u3', name: 'Jane Smith', email: 'jane@example.com', role: 'user', status: 'Inactive', plan: 'None' }
];

/** Dev-only credentials — never shown in production UI */
export const MOCK_CREDENTIALS = {
  user: { email: 'michel@example.com', password: 'password' },
  admin: { email: 'admin@trackers.com', password: 'admin123' },
  scanner: { email: 'scanner@trackers.com', password: 'scanner123' }
};
