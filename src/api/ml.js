import apiClient from './client';

export const mlAPI = {
  // Get anomalies for a city
  getAnomalies: async (city, days = 30) => {
    const response = await apiClient.get(`/api/ml/anomalies/${city}`, {
      params: { days },
    });
    return response.data;
  },

  // Get weather patterns (clustering)
  getPatterns: async (city, days = 90) => {
    const response = await apiClient.get(`/api/ml/patterns/${city}`, {
      params: { days },
    });
    return response.data;
  },

  // Get trend analysis
  getTrends: async (city, metric = 'temperature', days = 90) => {
    const response = await apiClient.get(`/api/ml/trends/${city}`, {
      params: { metric, days },
    });
    return response.data;
  },

  // Run comprehensive analysis
  analyze: async (city) => {
    const response = await apiClient.post(`/api/ml/analyze/${city}`);
    return response.data;
  },

  // Check ML service health
  checkHealth: async () => {
    const response = await apiClient.get('/api/ml/health');
    return response.data;
  },
};
