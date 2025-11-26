import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to get CSRF token from cookies
const getCsrfToken = () => {
  const cookies = document.cookie.split(';');
  const csrfCookie = cookies.find(cookie => cookie.trim().startsWith('csrftoken='));
  if (csrfCookie) {
    return csrfCookie.split('=')[1].trim();
  }
  return null;
};

// Request interceptor to add CSRF token
api.interceptors.request.use(
  (config) => {
    // Only add CSRF token for state-changing methods
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle CSRF token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // If CSRF error, try to get a fresh token
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
      // Fetch CSRF token by making a GET request to the API root
      try {
        await axios.get(
          process.env.REACT_APP_API_URL?.replace('/api', '') || 'http://localhost:8000',
          { withCredentials: true }
        );
        // Retry the original request
        const csrfToken = getCsrfToken();
        if (csrfToken && error.config) {
          error.config.headers['X-CSRFToken'] = csrfToken;
          return api.request(error.config);
        }
      } catch (e) {
        console.error('Failed to refresh CSRF token:', e);
      }
    }
    return Promise.reject(error);
  }
);

export default api;

