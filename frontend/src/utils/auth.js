// src/utils/auth.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const AUTH_URL = `${API_BASE_URL}/user/`;

let isRefreshing = false;
let failedQueue = [];

// Убираем router из модуля
let globalRouter = null;

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Принимаем router извне
export const setupInterceptors = (router) => {
  globalRouter = router; // Сохраняем

  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status !== 401) {
        return Promise.reject(error);
      }

      if (
        originalRequest.url.includes('/login') ||
        originalRequest.url.includes('/refresh')
      ) {
        logout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = 'Bearer ' + token;
            return axios(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        logout();
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      isRefreshing = true;

      // Убираем Authorization для /refresh
      delete axios.defaults.headers.common['Authorization'];

      try {
        const response = await axios.post(`${AUTH_URL}refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        if (access) {
          localStorage.setItem('accessToken', access);
          axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
          originalRequest.headers['Authorization'] = `Bearer ${access}`;
          processQueue(null, access);
          return axios(originalRequest);
        } else {
          throw new Error('No access token returned');
        }
      } catch (err) {
        console.error('Token refresh failed:', err);
        logout(); // Вызываем logout
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }
  );
};

const logout = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  delete axios.defaults.headers.common['Authorization'];
  if (globalRouter) {
    globalRouter.push('/login'); // ✅ Теперь router доступен
  } else {
    // Резервный вариант
    window.location.href = '/login';
  }
};

export { logout };