import axios from 'axios';
import { getAccessToken } from './auth';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
