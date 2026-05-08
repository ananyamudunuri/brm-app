// frontend/src/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  console.log('Token being used:', token ? `${token.substring(0, 50)}...` : 'No token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log('Making request to:', config.method?.toUpperCase(), config.baseURL + config.url);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log('Response success:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.config?.url);
    console.error('Error data:', error.response?.data);
    return Promise.reject(error);
  }
);

export default api;