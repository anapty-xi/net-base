<template>
  <div class="account-container">
    <div class="profile-card">
      
      <div class="avatar-wrapper">
        <img 
          :src="user_placeholder" 
          alt="Аватар пользователя" 
          class="profile-avatar"
        />
      </div>

      <p class="userr-username">{{ username }}</p>
      
      <button @click="logout" class="logout-button">
        Выйти из аккаунта
      </button>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import user_placeholder from '../assets/user_placeholder.png';


const USER_URL = 'http://localhost:8000/user/user/'; 
const username = ref('загрузка...');
const router = useRouter();

  (async () => {
    try {

      const response = await axios.get(USER_URL);

      const user_data = response.data;
      
      if (user_data) {

        username.value = user_data.username
        

      } else {
        username.value = 'ошибка запроса'
      }
      
    } catch (err) {
      
    }
  })();

const logout = () => {

  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');

  if (axios.defaults.headers.common['Authorization']) {
    delete axios.defaults.headers.common['Authorization'];
  }

  console.log('Пользователь вышел. Токены удалены.');
  

  router.push({ path: '/login' }); 
};
</script>

<style scoped>
.account-container {

  justify-content: center;
  align-items: center;
  min-height: 100vh;

}

.profile-card {
  max-width: 380px;
  width: 100%;
  padding: 35px 25px;
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  background-color: var(--bg-card);
}

.avatar-wrapper {
  margin-bottom: 20px;
}

.profile-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--primary-light);
  box-shadow: 0 0 12px rgba(28, 124, 84, 0.15);
}

.user-username {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 25px;
}

.logout-button {
  width: 100%;
  padding: 13px;
  background-color: var(--error);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.05em;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #c62828;
}
</style>
