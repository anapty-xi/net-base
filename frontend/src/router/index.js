import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import Homepage from '../views/Homepage.vue'
import TableView from '../views/TableView.vue';


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
  },
  {
    path: '/tables/:tableName',
    name: 'TableView',
    component: TableView,
    props: true
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
