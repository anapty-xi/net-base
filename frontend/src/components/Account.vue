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
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh; 
}

.profile-card {
  max-width: 350px;
  width: 100%;
  padding: 30px 20px;
  border: 1px solid #ddd;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  text-align: center;
  background-color: white;
}

.avatar-wrapper {
  margin-bottom: 20px;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%; 
  object-fit: cover;
  border: 4px solid #73E2A7;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.user-username {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 25px;
  word-wrap: break-word; 
}

.logout-button {
  width: 100%;
  padding: 12px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #d32f2f;
}
</style>
