<template>
  <div class="account-container">
    <div class="profile-card">
      
      <div class="avatar-wrapper">
        <img 
          src="UserPlaceholder" 
          alt="Аватар пользователя" 
          class="profile-avatar"
        />
      </div>

      <p class="user-email">{{ username }}</p>
      
      <button @click="logout" class="logout-button">
        Выйти из аккаунта
      </button>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import UserPlacehilder from '../assets/user_placeholder.png'


const USER_URL = 'http://localhost:8000/user/user/'; 
const username = 'ошибка'


  try {

    const response = await axios.get(LOGIN_URL);

    const user_data = response.data;
    
    if (user_data) {

      const username = user_data[username]
      

    } else {
      error.value = 'Сервер вернул некорректный ответ';
    }
    
  } catch (err) {
    pass
  }

const logout = () => {
  // 1. Удаляем все токены из локального хранилища
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  
  // 2. Очищаем заголовок авторизации Axios (если он был установлен)
  // Это важно, чтобы последующие запросы не уходили со старым токеном
  if (window.axios && window.axios.defaults.headers.common['Authorization']) {
    delete window.axios.defaults.headers.common['Authorization'];
  }

  console.log('Пользователь вышел. Токены удалены.');
  
  // 3. Перенаправляем пользователя на страницу входа
  // Предполагаем, что у вас есть маршрут с именем 'Login'
  router.push({ path: '/login' }); 
};
</script>

<style scoped>
.account-container {
  display: flex;
  justify-content: center;
  align-items: center;
  /* Занимает всю доступную высоту, как ваша форма входа */
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
  border-radius: 50%; /* Делаем круглым */
  object-fit: cover;
  border: 4px solid #73E2A7; /* Цвет вашего хедера */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.user-email {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 25px;
  word-wrap: break-word; /* Для длинных email */
}

.logout-button {
  width: 100%;
  padding: 12px;
  background-color: #f44336; /* Красный цвет для кнопки выхода */
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
