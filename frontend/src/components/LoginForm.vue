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
import { useRouter } from 'vue-router'


const LOGIN_URL = 'http://localhost:8000/user/login/'; 
const router = useRouter()


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

      
      console.log('Успешный вход. Токен доступа сохранен:', access);
      router.push({path: '/homepage'});
      

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
  width: 22rem;
  margin: 50px auto;
  padding: 30px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background-color: var(--bg-card);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 18px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.95em;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--border);
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 1em;
  color: var(--text-primary);
  background-color: var(--bg-page);
  transition: border-color 0.2s;
}

input[type="text"]:focus,
input[type="password"]:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px rgba(28, 124, 84, 0.1);
}

button {
  width: 100%;
  padding: 12px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.05em;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

button:disabled {
  background-color: #94d3a2;
  cursor: not-allowed;
}

.error-message {
  color: var(--error);
  margin-top: 12px;
  font-size: 0.9em;
  text-align: center;
}
</style>