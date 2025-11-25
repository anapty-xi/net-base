<template>
  <div class="db-table-view">
    <h3>Список Таблиц Базы Данных</h3>

    <div v-if="loading" class="state-message loading">
      Загрузка названий таблиц и информации о пользователе...
    </div>

    <div v-else-if="error" class="state-message error">
      Ошибка: {{ error }}
    </div>

    <ul v-else class="table-list">
      <li v-for="tableName in tables" :key="tableName" class="table-item">
        
        <input 
          v-if="isStaff" 
          type="checkbox" 
          :id="`checkbox-${tableName}`" 
          :value="tableName" 
          v-model="selectedTables"
          class="delete-checkbox"
        >
        
        <router-link :to="{ name:'TableView', params: {tableName: tableName} }" class="table-link">
          {{ tableName }}
        </router-link>

      </li>
    </ul>

    <div v-if="isStaff && selectedTables.length > 0" class="delete-actions">
      <button @click="deleteSelectedTables" :disabled="isDeleting" class="delete-button">
        {{ isDeleting ? 'Удаление...' : `Удалить выбранные (${selectedTables.length})` }}
      </button>
      <div v-if="deleteError" class="state-message error delete-error">
        Ошибка удаления: {{ deleteError }}
      </div>
    </div>
    
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';


const USER_INFO_URL = 'http://localhost:8000/user/user/'; 
const DB_INFO_URL = 'http://localhost:8000/db/get_table_info/'; 
const DB_DELETE_BASE_URL = 'http://localhost:8000/db/delete/'; 


const tables = ref([]); 
const isStaff = ref(false); 
const selectedTables = ref([]); 
const loading = ref(true); 
const error = ref(null); 
const isDeleting = ref(false); 
const deleteError = ref(null); 


const fetchData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const userResponse = await axios.get(USER_INFO_URL);
    isStaff.value = userResponse.data.is_staff; 

    const dbResponse = await axios.get(DB_INFO_URL);
    tables.value = Object.keys(dbResponse.data.tabels);

  } catch (err) {
    console.error("Не удалось выполнить запрос:", err);
    const endpoint = err.config.url.includes('/user') ? 'User-сервиса' : 'DB-сервиса';
    error.value = `Ошибка загрузки данных с ${endpoint}: ${err.message}`;
  } finally {
    loading.value = false;
  }
};


const deleteSelectedTables = async () => {
  if (selectedTables.value.length === 0 || isDeleting.value) return;

  isDeleting.value = true;
  deleteError.value = null;
  const tablesToDelete = [...selectedTables.value]; 

  const successfulDeletions = [];
  const failedDeletions = [];


  const deletePromises = tablesToDelete.map(tableName => {
    const deleteUrl = `${DB_DELETE_BASE_URL}${tableName+'/'}`;
    
    // Используем метод DELETE
    return axios.delete(deleteUrl) 
      .then(() => {
        successfulDeletions.push(tableName);
      })
      .catch(err => {
        console.error(`Ошибка при удалении таблицы ${tableName}:`, err);
        failedDeletions.push(tableName);
      });
  });

  await Promise.allSettled(deletePromises);

  if (failedDeletions.length > 0) {
    deleteError.value = `Не удалось удалить таблицы: ${failedDeletions.join(', ')}.`;
  }


  if (successfulDeletions.length > 0) {
    tables.value = tables.value.filter(t => !successfulDeletions.includes(t));
  }

  selectedTables.value = [];
  isDeleting.value = false;
};

onMounted(() => {
  fetchData();
});
</script>


<style scoped>

.db-table-view {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 1000px;
  margin: 40px auto;
  font-family: 'Arial', sans-serif;
}

h3 {
  color: #333;
  border-bottom: 2px solid #ccc;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

/*
 * 2. Сообщения о состоянии (Загрузка/Ошибка)
 */
.state-message {
  padding: 15px;
  border-radius: 4px;
  font-size: 1.1em;
  font-weight: bold;
  text-align: center;
  margin: 20px 0;
}

.loading {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.error {
  background-color: #fff2e8;
  color: #f5222d;
  border: 1px solid #ffbb96;
}


.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: #fff;
}


.data-table thead {
  background-color: #009879;
  color: #ffffff;
  text-align: left;
}

.data-table th {
  padding: 12px 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.table-list li {
  margin-bottom: 8px;
}

.table-link {
  display: block; /* Чтобы ссылка занимала всю ширину */
  padding: 10px 15px;
  background-color: #f8f8f8;
  border: 1px solid #eee;
  border-radius: 4px;
  text-decoration: none; /* Убираем подчеркивание */
  color: #007bff; /* Цвет ссылки */
  font-weight: 500;
  transition: background-color 0.2s, box-shadow 0.2s;
}

.table-link:hover {
  background-color: #e6f7ff; /* Приятный фон при наведении */
  color: #1890ff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Добавьте стили для улучшения внешнего вида */
.db-table-view {
  /* Базовый контейнер */
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-family: Arial, sans-serif;
}

.table-list {
  list-style: none;
  padding: 0;
}

.table-item {
  /* Для выравнивания чекбокса и ссылки */
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.delete-checkbox {
  margin-right: 10px;
  /* Увеличиваем размер для лучшей интерактивности */
  transform: scale(1.2); 
  cursor: pointer;
}

.table-link {
  text-decoration: none;
  color: #007bff;
  font-size: 1.1em;
  flex-grow: 1; /* Чтобы ссылка занимала оставшееся место */
  transition: color 0.2s;
}

.table-link:hover {
  color: #0056b3;
}

.delete-actions {
  margin-top: 20px;
  /* Выравниваем кнопку справа, включая сообщение об ошибке */
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.delete-button {
  padding: 10px 15px;
  background-color: #dc3545; /* Красный для удаления */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.delete-button:hover:not(:disabled) {
  background-color: #c82333;
}

.delete-button:disabled {
  background-color: #f8d7da; /* Светло-красный при отключении */
  color: #721c24;
  cursor: not-allowed;
}

/* Стили для сообщений о состоянии */
.state-message {
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 10px;
  font-size: 0.9em;
}

.loading {
  background-color: #e9ecef;
  color: #6c757d;
  text-align: center;
}

.error, .delete-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
.delete-error {
  /* Отступ для ошибки, если она рядом с кнопкой */
  margin-left: 15px;
}
</style>