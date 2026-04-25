import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT_MS = Number(process.env.REACT_APP_API_TIMEOUT_MS || 30000);
const API_RETRIES = Number(process.env.REACT_APP_API_RETRIES || 2);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
});

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const shouldRetryRequest = (error, retryCount) => {
  if (retryCount >= API_RETRIES) {
    return false;
  }

  const status = error?.response?.status;
  const isTimeout = error?.code === 'ECONNABORTED' || String(error?.message || '').toLowerCase().includes('timeout');
  const isTransient = !status || status >= 500;

  return isTimeout || isTransient;
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error?.config;
    if (!config) {
      return Promise.reject(error);
    }

    config.__retryCount = config.__retryCount || 0;
    if (!shouldRetryRequest(error, config.__retryCount)) {
      return Promise.reject(error);
    }

    config.__retryCount += 1;
    const retryDelay = 500 * (2 ** (config.__retryCount - 1));
    await sleep(retryDelay);

    return api(config);
  }
);

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
