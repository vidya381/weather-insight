import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only redirect to login for 401 errors if:
    // 1. We're not already on auth pages (login/register)
    // 2. It's not a login/register API call (to allow error messages to show)
    const isAuthPage = ['/login', '/register'].includes(window.location.pathname);
    const isAuthEndpoint = error.config?.url?.includes('/api/auth/login') ||
                           error.config?.url?.includes('/api/auth/register');

    if (error.response?.status === 401 && !isAuthPage && !isAuthEndpoint) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
