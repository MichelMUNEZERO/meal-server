import { mockAttendance } from './mock-data';

export const attendanceService = {
  /**
   * @param {string} userId
   */
  getHistory: async (userId) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    if (userId) {
      return mockAttendance.filter(a => a.userId === userId);
    }
    return mockAttendance;
  },
  
  /**
   * @param {string} userId
   * @param {string} mealType
   */
  generateQR: async (userId, mealType) => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const timestamp = Date.now();
    return JSON.stringify({
      userId,
      mealType,
      timestamp,
      signature: 'mock-sig-' + timestamp
    });
  }
};
