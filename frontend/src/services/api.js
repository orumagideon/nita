import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Data endpoints
  getData: (limit = null, offset = 0) => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit);
    params.append('offset', offset);
    return api.get(`/data?${params}`);
  },

  // Statistics
  getStats: (county = null, level = null) => {
    const params = new URLSearchParams();
    if (county) params.append('county', county);
    if (level) params.append('level', level);
    return api.get(`/stats?${params}`);
  },

  // Filter options
  getCounties: () => api.get('/counties'),
  getLevels: () => api.get('/levels'),

  // Search
  search: (query, field = null) => {
    const params = new URLSearchParams();
    params.append('query', query);
    if (field) params.append('field', field);
    return api.get(`/search?${params}`);
  },
};

export default api;
