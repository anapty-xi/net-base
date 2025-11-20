import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'


const routes = [
  {
    path: '/login', // URL, по которому будет доступна страница
    name: 'Login',
    component: LoginView // Указываем, какой компонент использовать
  },
  // ... другие маршруты (например, '/')
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
