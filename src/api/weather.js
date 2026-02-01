import apiClient from './client';

export const weatherAPI = {
  // Get current weather for a city
  getCurrentWeather: async (city) => {
    const response = await apiClient.get(`/api/weather/current/${city}`);
    return response.data;
  },

  // Get weather forecast
  getForecast: async (city, days = 5) => {
    const response = await apiClient.get(`/api/weather/forecast/${city}`, {
      params: { days },
    });
    return response.data;
  },

  // Get weather history
  getHistory: async (city, days = 7) => {
    const response = await apiClient.get(`/api/weather/history/${city}`, {
      params: { days },
    });
    return response.data;
  },

  // Get daily aggregates
  getDailyAggregates: async (city, days = 7) => {
    const response = await apiClient.get(`/api/weather/history/${city}/daily`, {
      params: { days },
    });
    return response.data;
  },

  // Compare multiple cities
  compareCities: async (cities) => {
    const citiesParam = Array.isArray(cities) ? cities.join(',') : cities;
    const response = await apiClient.get('/api/weather/compare', {
      params: { cities: citiesParam },
    });
    return response.data;
  },
};
