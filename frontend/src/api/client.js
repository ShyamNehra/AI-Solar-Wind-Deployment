import axios from 'axios';

// Central API Base URL Configuration with Dynamic Hostname Fallback
const getDefaultApiUrl = () => {
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${window.location.hostname}:8000`;
  }
  return 'http://localhost:8000';
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || getDefaultApiUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60-second timeout — GIS parallel mirror racing resolves in ≤5s; 60s covers cold ML-pipeline start
});

// Interceptor to inject JWT token if user is logged in
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;