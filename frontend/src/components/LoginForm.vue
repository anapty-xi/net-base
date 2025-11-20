<template>
  <form @submit.prevent="loginUser" class="login-form">
    <h2>Вход в систему</h2>
    
    <div class="form-group">
      <label for="username">Имя пользователя:</label>
      <input type="text" id="username" v-model="credentials.username" required>
    </div>
    
    <div class="form-group">
      <label for="password">Пароль:</label>
      <input type="password" id="password" v-model="credentials.password" required>
    </div>
    
    <button type="submit" :disabled="isLoading">
      {{ isLoading ? 'Вход...' : 'Войти' }}
    </button>
    
    <p v-if="error" class="error-message">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';


const LOGIN_URL = 'http://localhost:8000/user/login/'; 


const credentials = reactive({
  username: '',
  password: ''
});


const isLoading = ref(false);
const error = ref(null);

const loginUser = async () => {
  isLoading.value = true;
  error.value = null; 
  
  try {

    const response = await axios.post(LOGIN_URL, {
      username: credentials.username,
      password: credentials.password
    });

    const { access, refresh } = response.data;
    
    if (access && refresh) {

      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      

      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      console.log('Успешный вход. Токен доступа сохранен:', access);
      

    } else {
      error.value = 'Сервер вернул некорректный ответ (нет токенов).';
    }
    
  } catch (err) {
    if (err.response.status == 400) {
      error.value = 'Логин и пароль обязательны';
      console.error(err);
    } else if (err.response.status == 401) {
      error.value = 'Данные не верны';
      console.error(err);
    } else {
      error.value = 'Ошибка сети или недоступность микросервиса.';
      console.error(err);
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-form {
  width: 20rem;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;

}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
input[type="text"], input[type="password"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #1C7C54;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background-color: #a5d6a7;
}
.error-message {
  color: red;
  margin-top: 10px;
}
</style>