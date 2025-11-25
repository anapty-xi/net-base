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

    <!-- Кнопка и форма для создания таблицы из CSV (только для isStaff) -->
    <div v-if="isStaff" class="create-actions">
      <button @click="showUploadForm = !showUploadForm" class="create-button">
        {{ showUploadForm ? 'Отмена' : 'Создать таблицу из CSV' }}
      </button>

      <div v-if="showUploadForm" class="upload-form">
        <input
          type="file"
          accept=".csv"
          @change="handleFileSelect"
          ref="fileInput"
          class="file-input"
        />
        <div v-if="uploadError" class="state-message error">
          Ошибка: {{ uploadError }}
        </div>
        <div class="upload-actions">
          <button @click="uploadCSV" :disabled="uploading" class="upload-button">
            {{ uploading ? 'Загрузка...' : 'Загрузить и создать' }}
          </button>
          <button @click="showUploadForm = false" :disabled="uploading" class="cancel-button">
            Отмена
          </button>
        </div>
      </div>
    </div>

    <!-- Блок удаления выбранных таблиц -->
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
const DB_CREATE_URL = 'http://localhost:8000/db/create/'
const DB_DELETE_BASE_URL = 'http://localhost:8000/db/delete/';


// Данные компонента
const tables = ref([]);
const isStaff = ref(false);
const selectedTables = ref([]);
const loading = ref(true);
const error = ref(null);
const isDeleting = ref(false);
const deleteError = ref(null);

// Новые переменные для загрузки CSV
const showUploadForm = ref(false);
const uploadFile = ref(null);
const uploading = ref(false);
const uploadError = ref(null);

// Получение данных о таблицах и пользователе
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
    const endpoint = err.config?.url.includes('/user') ? 'User-сервиса' : 'DB-сервиса';
    error.value = `Ошибка загрузки данных с ${endpoint}: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

// Удаление выбранных таблиц
const deleteSelectedTables = async () => {
  if (selectedTables.value.length === 0 || isDeleting.value) return;

  isDeleting.value = true;
  deleteError.value = null;
  const tablesToDelete = [...selectedTables.value];

  const successfulDeletions = [];
  const failedDeletions = [];

  const deletePromises = tablesToDelete.map(tableName => {
    const deleteUrl = `${DB_DELETE_BASE_URL}${tableName}/`;
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

// Обработка выбора CSV-файла
const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
    uploadFile.value = file;
    uploadError.value = null;
  } else {
    uploadFile.value = null;
    uploadError.value = 'Пожалуйста, выберите корректный CSV-файл.';
  }
};

// Отправка CSV на сервер для создания таблицы
const uploadCSV = async () => {
  if (!uploadFile.value || uploading.value) return;

  const formData = new FormData();
  formData.append('file', uploadFile.value);

  uploading.value = true;
  uploadError.value = null;

  try {
    await axios.post(DB_CREATE_URL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // Успешная загрузка — обновляем список таблиц
    await fetchData();
    showUploadForm.value = false;
    uploadFile.value = null;
  } catch (err) {
    console.error('Ошибка при загрузке CSV:', err);
    uploadError.value = err.response?.data?.error || 'Не удалось создать таблицу из CSV.';
  } finally {
    uploading.value = false;
  }
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

/* Сообщения о состоянии */
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

.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.delete-error {
  margin-left: 15px;
}

/* Список таблиц */
.table-list {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.table-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.delete-checkbox {
  margin-right: 10px;
  transform: scale(1.2);
  cursor: pointer;
}

.table-link {
  text-decoration: none;
  color: #007bff;
  font-size: 1.1em;
  flex-grow: 1;
  padding: 8px;
  transition: color 0.2s;
}

.table-link:hover {
  color: #0056b3;
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Кнопка создания таблицы */
.create-button {
  margin-top: 20px;
  padding: 10px 15px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s;
}

.create-button:hover:not(:disabled) {
  background-color: #218838;
}

/* Форма загрузки CSV */
.upload-form {
  margin-top: 15px;
  padding: 15px;
  border: 1px dashed #007bff;
  border-radius: 6px;
  background-color: #f9f9f9;
}

.file-input {
  width: 100%;
  margin-bottom: 10px;
}

.upload-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.upload-button,
.cancel-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95em;
}

.upload-button {
  background-color: #007bff;
  color: white;
}

.upload-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #545b62;
}

/* Кнопка удаления */
.delete-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.delete-button {
  padding: 10px 15px;
  background-color: #dc3545;
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
  background-color: #f8d7da;
  color: #721c24;
  cursor: not-allowed;
}
</style>
