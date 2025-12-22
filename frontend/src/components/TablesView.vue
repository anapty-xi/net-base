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
        
        <!-- Чекбокс для удаления (только staff) -->
        <input 
          v-if="isStaff" 
          type="checkbox" 
          :id="`checkbox-${tableName}`" 
          :value="tableName" 
          v-model="selectedTables"
          class="delete-checkbox"
        >
        
        <!-- Ссылка на таблицу -->
        <router-link :to="{ name: 'TableView', params: { tableName: tableName } }" class="table-link">
          {{ tableName }}
        </router-link>

        <!-- Кнопка "Скачать Excel" -->
        <button
          @click="downloadExcel(tableName)"
          class="download-button"
          :disabled="isDownloading[tableName]"
          :title="`Скачать таблицу ${tableName} как Excel`"
        >
          {{ isDownloading[tableName] ? 'Скачивание...' : '📥 Excel' }}
        </button>

      </li>
    </ul>

    <!-- Кнопки: Отчёт и Создать таблицу -->
    <div v-if="isStaff" class="action-row">
      <router-link to="/report" class="report-button small-button">
        Отчёт
      </router-link>
      <button @click="showUploadForm = !showUploadForm" class="create-button small-button">
        {{ showUploadForm ? 'Отмена' : 'Создать таблицу' }}
      </button>
    </div>

    <!-- Форма создания таблицы -->
    <div v-if="isStaff" class="create-actions">
      <div v-if="showUploadForm" class="upload-form">
        <input
          type="file"
          accept=".xlsx"
          @change="handleFileSelect"
          ref="fileInput"
          class="file-input"
        />
        <div class="analytics-checkbox">
          <input
            type="checkbox"
            id="inAnalytics"
            v-model="inAnalytics"
          />
          <label for="inAnalytics">Добавить в аналитику</label>
        </div>
        <div v-if="uploadError" class="state-message error">
          Ошибка: {{ uploadError }}
        </div>
        <div class="upload-actions">
          <button @click="uploadToServer" :disabled="uploading" class="upload-button">
            {{ uploading ? 'Загрузка...' : 'Загрузить и создать' }}
          </button>
          <button @click="showUploadForm = false" :disabled="uploading" class="cancel-button">
            Отмена
          </button>
        </div>
      </div>
    </div>

    <!-- Удаление выбранных таблиц -->
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

// URLs
const USER_INFO_URL = 'http://localhost:8000/user/user/';
const DB_INFO_URL = 'http://localhost:8000/db/get_table_info/';
const DB_CREATE_URL = 'http://localhost:8000/db/create/';
const DB_DELETE_BASE_URL = 'http://localhost:8000/db/delete/';
const DB_DOWNLOAD_URL = 'http://localhost:8000/db/table_file/';

// Реактивные данные
const tables = ref([]);
const isStaff = ref(false);
const selectedTables = ref([]);
const loading = ref(true);
const error = ref(null);
const isDeleting = ref(false);
const deleteError = ref(null);

const showUploadForm = ref(false);
const selectedFile = ref(null);  // ← переименовано: было uploadFile
const uploading = ref(false);
const uploadError = ref(null);
const inAnalytics = ref(false);
const isDownloading = ref({});

// Загрузка данных
const fetchData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const userResponse = await axios.get(USER_INFO_URL);
    isStaff.value = userResponse.data.is_staff;

    const dbResponse = await axios.get(DB_INFO_URL);
    tables.value = Object.keys(dbResponse.data);
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

// Обработка выбора XLSX-файла
const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (!file) {
    selectedFile.value = null;
    uploadError.value = null;
    return;
  }

  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ];

  if (!allowedTypes.includes(file.type)) {
    selectedFile.value = null;
    uploadError.value = 'Пожалуйста, выберите корректный XLSX-файл.';
    return;
  }

  if (!file.name.endsWith('.xlsx')) {
    selectedFile.value = null;
    uploadError.value = 'Файл должен иметь расширение .xlsx';
    return;
  }

  selectedFile.value = file;
  uploadError.value = null;
};

// Отправка XLSX-файла на сервер
const uploadToServer = async () => {
  if (!selectedFile.value || uploading.value) return;

  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('in_analytics', inAnalytics.value);

  uploading.value = true;
  uploadError.value = null;

  try {
    await axios.post(DB_CREATE_URL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    await fetchData();
    showUploadForm.value = false;
    selectedFile.value = null;
    inAnalytics.value = false;
  } catch (err) {
    console.error('Ошибка при загрузке XLSX:', err);
    uploadError.value =
      err.response?.data?.error ||
      err.response?.data?.detail ||
      'Не удалось создать таблицу из XLSX-файла.';
  } finally {
    uploading.value = false;
  }
};

// Скачивание таблицы как Excel
const downloadExcel = async (tableName) => {
  isDownloading.value[tableName] = true;
  try {
    const response = await axios.get(`${DB_DOWNLOAD_URL}${tableName}/`, {
      responseType: 'blob'
    });

    const contentType = response.headers['content-type'];
    if (contentType && contentType.includes('application/json')) {
      const errorBlob = await response.data.text();
      throw new Error(`Ошибка: ${errorBlob}`);
    }

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${tableName}.xlsx`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error(`Ошибка при скачивании ${tableName}:`, err);
    alert(`Не удалось скачать таблицу "${tableName}".`);
  } finally {
    isDownloading.value[tableName] = false;
  }
};

// Жизненный цикл
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.db-table-view,
.table-schema-editor {
  padding: 30px;
  background-color: var(--bg-page);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  max-width: 1000px;
  margin: 20px auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1, h3 {
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--primary-light);
  padding-bottom: 8px;
}

/* Сообщения */
.state-message {
  padding: 14px;
  border-radius: 6px;
  font-size: 0.95em;
  text-align: center;
  margin: 16px 0;
  font-weight: 500;
}

.loading {
  background-color: var(--primary-light);
  color: var(--primary-dark);
  border: 1px solid rgba(28, 124, 84, 0.3);
}

.error {
  background-color: #ffebee;
  color: var(--error);
  border: 1px solid #f5c6cb;
}

.info {
  background-color: #f0f8ff;
  color: var(--info);
  border: 1px solid #c4e2ff;
}

/* Кнопки */
.create-button,
.report-button,
.submit-button,
.global-update-button,
.delete-button,
.upload-button,
.cancel-button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  transition: background-color 0.2s;
}

.create-button,
.report-button {
  flex: 1;
  min-width: 160px;
  text-decoration: none;
  text-align: center;
  color: white;
}

.create-button {
  background-color: var(--primary);
}

.create-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.report-button {
  background-color: #17a2b8;
}

.report-button:hover {
  background-color: #138496;
}

.submit-button,
.global-update-button {
  background-color: var(--primary);
  color: white;
  width: 100%;
  margin-top: 20px;
}

.submit-button:hover:not(:disabled),
.global-update-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.delete-button {
  background-color: var(--error);
  color: white;
  padding: 10px 20px;
  font-weight: 600;
}

.delete-button:hover:not(:disabled) {
  background-color: #c62828;
}

/* Списки таблиц */
.table-list {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.table-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid var(--border);
  transition: background-color 0.1s;
}

.table-item:hover {
  background-color: var(--bg-table);
}

.delete-checkbox {
  margin-right: 12px;
  transform: scale(1.3);
  cursor: pointer;
}

.table-link {
  text-decoration: none;
  color: var(--primary);
  font-size: 1.05em;
  flex-grow: 1;
  padding: 10px;
  border-radius: 4px;
  transition: all 0.2s;
}

.table-link:hover {
  color: var(--primary-dark);
  background-color: var(--primary-light);
}

/* Формы */
.action-buttons {
  display: flex;
  gap: 14px;
  margin: 20px 0;
  flex-wrap: wrap;
  justify-content: center;
}

.upload-form {
  margin-top: 20px;
  padding: 20px;
  border: 2px dashed var(--primary);
  border-radius: 8px;
  background-color: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.file-input {
  width: 100%;
  margin-bottom: 14px;
}

.upload-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 16px;
}

.upload-button {
  background-color: var(--primary);
  color: white;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #545b62;
}

/* Таблицы */
.results-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--bg-card);
  margin-top: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.results-table th {
  background-color: var(--primary);
  color: white;
  font-weight: 600;
  padding: 12px 10px;
  text-align: center;
}

.results-table td {
  padding: 8px 10px;
  text-align: center;
  border: 1px solid var(--border);
}

.results-table tr:nth-child(even) {
  background-color: var(--bg-table);
}

.results-table input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  box-sizing: border-box;
  text-align: center;
}

.results-table input:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 2px rgba(28, 124, 84, 0.1);
}

.modern-button {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.action-row {
  display: flex;
  gap: 16px;
  margin: 20px 0;
  justify-content: center;
  flex-wrap: wrap;
}

.small-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: background-color 0.2s;
  flex: 1;
  min-width: 130px;
  max-width: 180px;
}

.report-button {
  background-color: #17a2b8;
  color: white;
}

.report-button:hover {
  background-color: #138496;
}

.create-button {
  background-color: var(--primary);
  color: white;
}

.create-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

/* Форма создания таблицы */
.create-actions {
  margin-top: 10px;
}

.upload-form {
  padding: 18px;
  border: 2px dashed var(--primary);
  border-radius: 8px;
  background-color: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.upload-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 14px;
}

.upload-button {
  background-color: var(--primary);
  color: white;
  padding: 10px 16px;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
  padding: 10px 16px;
}

.cancel-button:hover {
  background-color: #545b62;
}

/* Удаление таблиц */
.delete-actions {
  margin: 20px 0 0;
  padding-top: 16px;
  border-top: 1px solid var(--border); /* Визуальный разрыв */
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.delete-button {
  align-self: center;
  background-color: var(--error);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  min-width: 200px;
  font-size: 0.95em;
}

.delete-button:hover:not(:disabled) {
  background-color: #c62828;
}

.download-button {
  margin-left: auto;
  padding: 6px 10px;
  font-size: 0.85em;
  background-color: #1d6940;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-weight: 500;
  min-width: 80px;
}

.download-button:hover:not(:disabled) {
  background-color: #164d31;
}

.download-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Остальные стили — как в оригинале (ниже можно оставить все твои стили) */

/* Пример: оставь всё, что было... */
.db-table-view {
  padding: 30px;
  background-color: var(--bg-page);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  max-width: 1000px;
  margin: 20px auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h3 {
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--primary-light);
  padding-bottom: 8px;
}

.state-message {
  padding: 14px;
  border-radius: 6px;
  font-size: 0.95em;
  text-align: center;
  margin: 16px 0;
  font-weight: 500;
}

.loading {
  background-color: var(--primary-light);
  color: var(--primary-dark);
  border: 1px solid rgba(28, 124, 84, 0.3);
}

.error {
  background-color: #ffebee;
  color: var(--error);
  border: 1px solid #f5c6cb;
}

.info {
  background-color: #f0f8ff;
  color: var(--info);
  border: 1px solid #c4e2ff;
}

.table-list {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.table-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid var(--border);
  transition: background-color 0.1s;
}

.table-item:hover {
  background-color: var(--bg-table);
}

.delete-checkbox {
  margin-right: 12px;
  transform: scale(1.3);
  cursor: pointer;
}

.table-link {
  text-decoration: none;
  color: var(--primary);
  font-size: 1.05em;
  flex-grow: 1;
  padding: 10px;
  border-radius: 4px;
  transition: all 0.2s;
}

.table-link:hover {
  color: var(--primary-dark);
  background-color: var(--primary-light);
}

.action-row {
  display: flex;
  gap: 16px;
  margin: 20px 0;
  justify-content: center;
  flex-wrap: wrap;
}

.small-button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: background-color 0.2s;
  flex: 1;
  min-width: 130px;
  max-width: 180px;
}

.report-button {
  background-color: #17a2b8;
  color: white;
}

.report-button:hover {
  background-color: #138496;
}

.create-button {
  background-color: var(--primary);
  color: white;
}

.create-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.create-actions {
  margin-top: 10px;
}

.upload-form {
  padding: 18px;
  border: 2px dashed var(--primary);
  border-radius: 8px;
  background-color: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.upload-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 14px;
}

.upload-button {
  background-color: var(--primary);
  color: white;
  padding: 10px 16px;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
  padding: 10px 16px;
}

.cancel-button:hover {
  background-color: #545b62;
}

.delete-actions {
  margin: 20px 0 0;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.delete-button {
  align-self: center;
  background-color: var(--error);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  min-width: 200px;
  font-size: 0.95em;
}

.delete-button:hover:not(:disabled) {
  background-color: #c62828;
}
</style>

