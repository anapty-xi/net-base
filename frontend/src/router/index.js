import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import Homepage from '../views/Homepage.vue'


const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView 
  },
  {
    path: '/homepage',
    name: 'Homepage',
    component: Homepage
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
