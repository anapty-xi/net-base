// src/utils/auth.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const AUTH_URL = `${API_BASE_URL}/user/`;

let isRefreshing = false;
let failedQueue = [];
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

export const setupInterceptors = (router) => {
  globalRouter = router;

  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // 🟢 Не перехватываем 401 на /login — просто возвращаем ошибку
      if (originalRequest.url.includes('/login')) {
        return Promise.reject(error);
      }

      // 🟡 На /refresh — если ошибка, значит, сессия полностью просрочена → logout
      if (originalRequest.url.includes('/refresh')) {
        logout();
        return Promise.reject(error);
      }

      // 🔴 Все остальные 401 — попытка обновить токен
      if (error.response?.status === 401) {
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
            throw new Error('No access token');
          }
        } catch (err) {
          console.error('Token refresh failed:', err);
          logout();
          return Promise.reject(error);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    }
  );
};

const logout = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  delete axios.defaults.headers.common['Authorization'];
  if (globalRouter) {
    globalRouter.push('/login');
  } else {
    window.location.href = '/login';
  }
};

export { logout };