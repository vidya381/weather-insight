import apiClient from './client';

export const citiesAPI = {
  // Search cities
  searchCities: async (query, limit = 30) => {
    const response = await apiClient.get('/api/cities/search', {
      params: { q: query, limit },
    });
    return response.data;
  },

  // List all cities
  listCities: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/api/cities', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Get city by ID
  getCityById: async (cityId) => {
    const response = await apiClient.get(`/api/cities/${cityId}`);
    return response.data;
  },

  // Get user's favorite cities
  getFavorites: async () => {
    const response = await apiClient.get('/api/cities/favorites/list');
    return response.data;
  },

  // Add city to favorites
  addFavorite: async (cityId) => {
    const response = await apiClient.post(`/api/cities/favorites/${cityId}`);
    return response.data;
  },

  // Remove city from favorites
  removeFavorite: async (cityId) => {
    const response = await apiClient.delete(`/api/cities/favorites/${cityId}`);
    return response.data;
  },

  // Get favorite count
  getFavoriteCount: async () => {
    const response = await apiClient.get('/api/cities/favorites/count');
    return response.data;
  },
};
