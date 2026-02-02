import apiClient from './client';

export const authAPI = {
  register: async (username, email, password) => {
    const response = await apiClient.post('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  login: async (username, password) => {
    const response = await apiClient.post('/api/auth/login', {
      username_or_email: username,
      password,
    });
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/api/auth/logout');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },

  updateProfile: async (updateData) => {
    const response = await apiClient.put('/api/auth/me', updateData);
    return response.data;
  },
};
