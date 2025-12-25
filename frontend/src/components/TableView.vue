<template>
  <div class="table-schema-editor">
    <h1>
      <span class="table-name-highlight">{{ tableName }}</span>
    </h1>

    <div v-if="loading" class="state-message loading">
      Загрузка схемы таблицы...
    </div>

    <div v-else-if="error" class="state-message error">
      Ошибка: {{ error }}
    </div>

    <div v-else class="schema-form">
      <form @submit.prevent="submitData" class="data-entry-form">
        <div class="table-controls">
          <button type="submit" class="submit-button" :disabled="submitting">
            {{ submitting ? '...' : 'Поиск' }}
          </button>
        </div>

        <div class="table-scroll-wrapper">
          <div class="filter-table">
            <div class="filter-table-row header-row">
              <div v-for="field in fields" :key="field" class="filter-table-cell header-cell">
                {{ field }}
              </div>
            </div>
            <div class="filter-table-row input-row">
              <div v-for="field in fields" :key="field" class="filter-table-cell input-cell">
                <input
                  :id="field"
                  :name="field"
                  type="text"
                  class="field-input-cell"
                  v-model="filterCriteria[field]"
                />
              </div>
            </div>
          </div>
        </div>
      </form>

      <p v-if="fields.length === 0" class="state-message info">
        В таблице нет полей для отображения.
      </p>

      <hr />

      <div v-if="dataResults.length > 0" class="results-table-container">
        <div class="table-scroll-wrapper">
          <table class="results-table">
            <thead>
              <tr>
                <th v-for="field in fields" :key="field">{{ field }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in paginatedResults" :key="row.pkValue || index">
                <td
                  v-for="field in fields"
                  :key="field"
                  class="result-cell-input"
                  :class="{ 'id-cell': field.toLowerCase() === 'id' }"
                >
                  <input
                    type="text"
                    :name="field"
                    :value="getInputValue(row.data, field)"
                    @input="onInput(row, field, $event)"
                    :class="{ modified: row.isModified[field] }"
                    :readonly="field.toLowerCase() === 'id'"
                    class="field-input-cell"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Пагинация -->
        <div v-if="totalPages > 1" class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="pagination-button">
            ← Назад
          </button>

          <span class="pagination-info">
            Страница {{ currentPage }} из {{ totalPages }}
          </span>

          <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-button">
            Вперёд →
          </button>
        </div>

        <hr class="update-separator" />

        <div class="global-update-actions">
          <button
            @click="updateAllModifiedRows"
            :disabled="!hasAnyModifications || isGlobalUpdating"
            class="submit-button global-update-button"
          >
            {{ isGlobalUpdating ? 'Обновление всех строк...' : 'Обновить все измененные строки' }}
          </button>

          <div v-if="globalUpdateError" class="state-message error update-error">
            Ошибка при массовом обновлении: {{ globalUpdateError }}
          </div>

          <div v-if="globalUpdateSuccess > 0" class="state-message success update-success">
            Успешно обновлено строк: {{ globalUpdateSuccess }}
          </div>
        </div>
      </div>

      <div v-else-if="submitted && dataResults.length === 0 && !submitting" class="state-message info">
        По вашему запросу строк не найдено.
      </div>

      <div v-if="submitError" class="state-message error">
        Ошибка поиска данных: {{ submitError }}
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';

const route = useRoute();
const tableName = route.params.tableName;

const fields = ref([]);
const pkField = ref(null);
const loading = ref(true);
const error = ref(null);

const filterCriteria = ref({});
const dataResults = ref([]);
const submitting = ref(false);
const submitted = ref(false);
const submitError = ref(null);

const hasAnyModifications = ref(false);
const isGlobalUpdating = ref(false);
const globalUpdateError = ref(null);
const globalUpdateSuccess = ref(0);

const currentPage = ref(1);
const rowsPerPage = 100;

const BASE_URL = 'http://127.0.0.1:8000/db/';
const SEARCH_URL = `${BASE_URL}get_rows/${tableName}/`;
const UPDATE_URL = `${BASE_URL}update_row/${tableName}/`;

const enrichRow = (rowData) => {
  const enriched = {
    data: rowData,
    originalData: { ...rowData },
    pkValue: rowData[pkField.value],
    isModified: {},
    hasModifications: false,
  };
  fields.value.forEach(field => {
    enriched.isModified[field] = false;
  });
  return enriched;
};

const checkColumnIndex = ref(-1);

const fetchSchema = async () => {
  const SCHEMA_URL = `${BASE_URL}get_table_info/${tableName}/`;
  try {
    const response = await axios.get(SCHEMA_URL);
    const allFields = response.data[tableName];
    if (Array.isArray(allFields) && allFields.length > 0) {
      pkField.value = allFields[0];
      fields.value = allFields;
      checkColumnIndex.value = fields.value.findIndex(field => field.toLowerCase() === 'проверено');
    } else {
      fields.value = [];
      pkField.value = null;
    }
    fields.value.forEach(field => {
      filterCriteria.value[field] = '';
    });
  } catch (err) {
    error.value = `Не удалось загрузить схему таблицы: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

const submitData = async () => {
  submitting.value = true;
  submitted.value = true;
  submitError.value = null;
  dataResults.value = [];
  hasAnyModifications.value = false;
  currentPage.value = 1;

  const queryPayload = Object.keys(filterCriteria.value).reduce((acc, key) => {
    const value = filterCriteria.value[key];
    if (value && value.trim() !== '') {
      acc[key] = value.trim();
    }
    return acc;
  }, {});

  try {
    const response = await axios.post(SEARCH_URL, queryPayload);
    const structuredRows = response.data.rows || response.data;

    if (!Array.isArray(structuredRows) || fields.value.length === 0) {
      throw new Error("Неверный формат данных.");
    }

    const restructuredRows = structuredRows.map(flatRow => {
      if (!Array.isArray(flatRow) || flatRow.length !== fields.value.length) {
        console.warn('Некорректная строка:', flatRow);
        return null;
      }
      const rowData = {};
      fields.value.forEach((field, i) => {
        rowData[field] = flatRow[i] == null ? '' : String(flatRow[i]);
      });
      return enrichRow(rowData);
    }).filter(Boolean);

    dataResults.value = restructuredRows;

  } catch (err) {
    submitError.value = 'Нет строк, удовлетворяющих запросу.';
  } finally {
    submitting.value = false;
  }
};

// Вычисляем отображаемые строки
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  return dataResults.value.slice(start, end);
});

// Общее количество страниц
const totalPages = computed(() => {
  return Math.ceil(dataResults.value.length / rowsPerPage) || 1;
});

// Управление страницами
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

const getInputValue = (data, field) => {
  if (field.toLowerCase() === 'проверено' && data[field] === 'у') {
    return '+';
  }
  return data[field];
};

const onInput = (row, field, event) => {
  if (field.toLowerCase() === 'id') return;

  const newValue = event.target.value.trim();
  const fieldName = field.toLowerCase();

  if (fieldName === 'проверено') {
    row.data[field] = newValue === '+' ? 'у' : newValue;
  } else {
    row.data[field] = newValue;
  }

  markAsModified(row, field);
};

const markAsModified = (row, fieldName) => {
  if (!row.isModified[fieldName]) {
    row.isModified[fieldName] = true;
    row.hasModifications = true;
    hasAnyModifications.value = true;
  }
  globalUpdateError.value = null;
  globalUpdateSuccess.value = 0;
};

const updateAllModifiedRows = async () => {
  if (!hasAnyModifications.value || isGlobalUpdating.value || !pkField.value) return;

  isGlobalUpdating.value = true;
  const promises = [];
  const modifiedRows = [];

  dataResults.value.forEach(row => {
    if (row.hasModifications) {
      const updates = {};
      fields.value.forEach(f => {
        if (row.isModified[f]) updates[f] = row.data[f];
      });
      promises.push(axios.patch(UPDATE_URL, {
        row_pk: String(row.pkValue),
        updates
      }));
      modifiedRows.push(row);
    }
  });

  if (promises.length === 0) {
    isGlobalUpdating.value = false;
    return;
  }

  try {
    const results = await Promise.allSettled(promises);
    let success = 0;
    results.forEach((r, i) => {
      if (r.status === 'fulfilled') {
        Object.keys(modifiedRows[i].isModified).forEach(f => {
          modifiedRows[i].isModified[f] = false;
        });
        modifiedRows[i].hasModifications = false;
        success++;
      }
    });
    globalUpdateSuccess.value = success;
    hasAnyModifications.value = dataResults.value.some(r => r.hasModifications);
  } catch (err) {
    globalUpdateError.value = 'Ошибка: ' + err.message;
  } finally {
    isGlobalUpdating.value = false;
  }
};

onMounted(() => {
  fetchSchema();
});
</script>

<style scoped>
:root {
  --primary: #1C7C54;
  --primary-dark: #1A5D43;
  --bg-page: #F8F9FA;
  --bg-card: #ffffff;
  --bg-input: #fcfcfc;
  --text-primary: #2C3E50;
  --text-secondary: #6C757D;
  --error: #d32f2f;
  --success: #28a745;
}

.table-schema-editor {
  padding: 30px;
  background-color: var(--bg-page);
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  max-width: 100%;
  margin: 20px auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text-primary);
}

h1 {
  color: var(--text-primary);
  font-weight: 600;
  text-align: center;
  margin-bottom: 10px;
  font-size: 1.8em;
}

.table-name-highlight {
  color: var(--primary);
  font-weight: 700;
}

/* Общие сообщения */
.state-message {
  padding: 14px;
  border-radius: 6px;
  font-size: 0.95em;
  text-align: center;
  margin: 18px 0;
  font-weight: 500;
}

.state-message.info,
.state-message.loading {
  background-color: var(--bg-card);
  border: 1px dashed var(--text-secondary);
  color: var(--text-secondary);
}

.state-message.error {
  background-color: #ffebee;
  color: var(--error);
  border: 1px solid #f5c6cb;
}

/* Форма поиска */
.data-entry-form {
  background-color: var(--bg-card);
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Таблица фильтров */
.filter-table {
  display: table;
  width: 100%;
  table-layout: auto;
  border-collapse: collapse;
  background-color: var(--bg-input);
  min-width: 800px;
}

.filter-table-row {
  display: table-row;
}

.filter-table-cell {
  display: table-cell;
  padding: 10px 8px;
  text-align: center;
  border-bottom: 1px solid #ddd;
  box-sizing: border-box;
  vertical-align: top;
}

.header-cell {
  font-size: 0.9em;
  font-weight: 500;
  color: var(--text-secondary);
  background-color: transparent;
  border-bottom: 2px solid #ddd;
}

.input-cell {
  padding: 6px 8px;
  background-color: white;
  border-bottom: 1px solid #ddd;
}

.field-input-cell {
  width: 100%;
  padding: 10px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  text-align: center;
  font-size: 0.95em;
  background-color: white;
  transition: border-color 0.2s;
}

.field-input-cell:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px rgba(28, 124, 84, 0.1);
}

/* Кнопка поиска */
.submit-button {
  display: inline-flex;
  padding: 8px 14px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-self: flex-start;
  margin-top: 10px;
  margin-left: 2px;
}

.submit-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.submit-button:disabled {
  background-color: #94d3a2;
  cursor: not-allowed;
}

/* Контейнер для кнопки поиска */
.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0 10px;
  padding: 0 2px;
}

.table-controls .submit-button {
  margin: 0;
}

/* Блок с результатами */
.results-table-container {
  background-color: var(--bg-card);
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.table-scroll-wrapper {
  overflow-x: auto;
  margin-top: 12px;
  border-radius: 6px;
  border: 1px solid #ddd;
  -webkit-overflow-scrolling: touch;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
  table-layout: auto;
  background-color: white;
}

.results-table th {
  background-color: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9em;
  padding: 10px 8px;
  text-align: center;
  border-bottom: 2px solid #ddd;
  letter-spacing: 0.5px;
}

.results-table td {
  padding: 0;
  border: 1px solid #ddd;
  text-align: center;
  font-size: 0.95em;
}

.result-cell-input input {
  width: 100%;
  height: 100%;
  padding: 10px 6px;
  border: none;
  background-color: transparent;
  text-align: center;
  font-size: 0.95em;
  box-sizing: border-box;
  transition: background-color 0.2s;
}

.result-cell-input input:focus {
  background-color: #f0f8ff;
  outline: 2px solid var(--primary);
  border-radius: 0;
}

.result-cell-input input.modified {
  background-color: #e6ffed;
  color: var(--primary);
  font-weight: 500;
  border: 1px solid #a3d9b1;
  border-radius: 4px;
}

/* Столбец ID — неактивный */
.result-cell-input.id-cell {
  background-color: #fafafa;
  color: var(--text-secondary);
  font-style: italic;
}

.result-cell-input.id-cell input {
  background-color: #fafafa !important;
  color: var(--text-secondary) !important;
  cursor: not-allowed;
  font-style: italic;
}

/* Сообщения об обновлении */
.update-error,
.update-success {
  margin-top: 15px;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.95em;
  text-align: center;
}

.update-error {
  background-color: #ffebee;
  color: var(--error);
  border: 1px solid #f5c6cb;
}

.update-success {
  background-color: #e6ffed;
  color: var(--success);
  border: 1px solid #a3d9b1;
}

/* Пагинация */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin: 20px 0;
  font-size: 0.95em;
  color: var(--text-secondary);
}

.pagination-button {
  padding: 8px 16px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.95em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.pagination-button:disabled {
  background-color: #94d3a2;
  cursor: not-allowed;
  color: #fff;
}

.pagination-info {
  font-weight: 500;
  color: var(--text-primary);
}
</style>