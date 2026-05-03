import { mockUser, mockAdmin } from './mock-data';

export const authService = {
  login: async (email, password) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    if (email === 'michel@example.com' && password === 'password') {
      return { user: mockUser, token: 'mock-user-token' };
    } else if (email === 'admin@trackers.com' && password === 'Mich540el12!') {
      return { user: mockAdmin, token: 'mock-admin-token' };
    } else if (email === 'scanner@trackers.com' && password === 'scanner123') {
      return { user: { id: 's1', name: 'Scanner Joe', email: 'scanner@trackers.com', role: 'scanner' }, token: 'mock-scanner-token' };
    } else {
      throw new Error('Invalid email or password');
    }
  },
  
  logout: async () => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return true;
  },
  
  forgotPassword: async (email) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    return true;
  }
};
