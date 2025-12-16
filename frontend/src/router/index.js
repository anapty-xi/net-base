import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import Homepage from '../views/Homepage.vue'
import TableView from '../views/TableView.vue';
import Report from '../views/Report.vue';

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
  },
  {
    path: '/report',
    name: 'Report',
    component: Report
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
