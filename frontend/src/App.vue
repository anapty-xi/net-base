<script setup>
import { RouterLink, RouterView } from 'vue-router'
import axios from 'axios';

import TheHeader from './components/Header.vue';
import TheFooter from './components/Footer.vue';

const token = localStorage.getItem('accessToken');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
} else {
  delete axios.defaults.headers.common['Authorization'];
}

</script>

<template>
  <div id="app">
    
    <TheHeader />

    <main class="app-content">
      <router-view />
    </main>

    <TheFooter />
  </div>
</template>


<style scoped>

#app {
  /* 1. Активируем Flexbox */
  display: flex; 
  
  /* 2. !!! УСТАНАВЛИВАЕМ КОЛОНОЧНОЕ НАПРАВЛЕНИЕ !!! */
  flex-direction: column; 
  
  /* 3. Гарантируем, что контейнер занимает всю высоту видимой области,
        чтобы Main мог растянуться (flex: 1) */
  min-height: 100vh;
}

main {
  /* 4. Позволяем области Main занять всё оставшееся пространство */
  flex: 1; 
  padding-bottom: 4rem;
}
</style>


