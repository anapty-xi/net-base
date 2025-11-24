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
        <div class="data-table-layout">
          <div class="header-row flex-row">
            <div v-for="field in fields" :key="field" class="header-cell">
              {{ field }}
            </div>
          </div>
          <div class="input-row flex-row">
            <div
              v-for="field in fields"
              :key="field"
              class="input-cell"
            >
              <input
                :id="field"
                :name="field"
                type="text"
                :placeholder="field"
                class="field-input-cell"
                v-model="filterCriteria[field]" 
              />
            </div>
          </div>
        </div>

        <button type="submit" class="submit-button" :disabled="submitting">
          {{ submitting ? 'Поиск...' : 'Выполнить поиск' }}
        </button>
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
                <th v-for="field in fields" :key="field">
                  {{ field }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in dataResults" :key="row.pkValue || index">
                
                <td v-for="field in fields" :key="field" class="result-cell-input">
                  <input
                    type="text"
                    :name="field"
                    v-model="row.data[field]" 
                    :class="{'modified': row.isModified[field]}"
                    @input="markAsModified(row, field)" 
                  />
                </td>
                
              </tr>
            </tbody>
          </table>
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
            ✅ Успешно обновлено строк: {{ globalUpdateSuccess }}
          </div>
        </div>
      </div>
      
      <div v-else-if="submitted && dataResults.length === 0 && !submitting">
          <p class="state-message info">
            По вашему запросу строк не найдено.
          </p>
      </div>

      <div v-if="submitError" class="state-message error">
        Ошибка поиска данных: {{ submitError }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
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

const BASE_URL = 'http://localhost:8000/db/'; 
const SEARCH_URL = `${BASE_URL}get_rows/${tableName}/`; 
const UPDATE_URL = `${BASE_URL}update_row/${tableName}/`; 

const enrichRow = (rowData) => {
    const enriched = {
        data: rowData,
        pkValue: rowData[pkField.value], 
        isModified: {}, 
        hasModifications: false, 
    };
    
    fields.value.forEach(field => {
        enriched.isModified[field] = false; 
    });
    return enriched;
};

const fetchSchema = async () => {
  const SCHEMA_URL = `${BASE_URL}get_table_info/${tableName}/`;

  try {
    const response = await axios.get(SCHEMA_URL);
    
    const allFields = response.data[tableName];
    
    if (Array.isArray(allFields) && allFields.length > 0) {
        pkField.value = allFields[0]; 
        fields.value = allFields; 
    } else {
        fields.value = [];
        pkField.value = null; 
    }
    
    fields.value.forEach(field => {
        filterCriteria.value[field] = '';
    });
    
    } catch (err) {
    error.value = `Не удалось загрузить схему таблицы. Ошибка: ${err.message}`;
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

    const queryPayload = Object.keys(filterCriteria.value).reduce((acc, key) => {
        const value = filterCriteria.value[key];
        if (value && value.trim() !== '') {
            acc[key] = value.trim(); 
        }
        return acc;
    }, {});
    
    try {
        const response = await axios.post(SEARCH_URL, {'conditions': queryPayload});
        
        const structuredRows = response.data.rows || response.data; 
        
        if (!Array.isArray(structuredRows) || fields.value.length === 0) {
             throw new Error("Неверный формат данных от сервера или отсутствует схема таблицы.");
        }

        const restructuredRows = [];
        const fieldNames = fields.value;
        const expectedColumns = fieldNames.length;
        
        for (const flatRow of structuredRows) {
            
            if (!Array.isArray(flatRow) || flatRow.length !== expectedColumns) {
                console.warn('Пропущена строка из-за несовпадения количества столбцов:', flatRow);
                continue; 
            }

            const rowData = {};
            
            for (let j = 0; j < expectedColumns; j++) {
                const fieldName = fieldNames[j];
                const fieldValue = flatRow[j];
                
                rowData[fieldName] = (fieldValue === null || fieldValue === undefined) ? '' : String(fieldValue); 
            }
            
            restructuredRows.push(enrichRow(rowData));
        }
        
        dataResults.value = restructuredRows;
        
    } catch (err) {
        submitError.value = `Не удалось выполнить поиск. Ошибка: ${err.message}`;
    } finally {
        submitting.value = false;
    }
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
    if (!hasAnyModifications.value || isGlobalUpdating.value || !pkField.value) {
        return; 
    }
isGlobalUpdating.value = true;
    globalUpdateError.value = null;
    globalUpdateSuccess.value = 0;

    const updatePromises = [];
    const modifiedRows = [];

    dataResults.value.forEach(row => {
        if (row.hasModifications) {
            const updates = {};
            fields.value.forEach(field => {
                if (row.isModified[field]) {
                    updates[field] = row.data[field];
                }
            });
            
            const singleUpdatePayload = {
                row_pk: String(row.pkValue),
                updates: updates
            };

            const promise = axios.post(UPDATE_URL, singleUpdatePayload);
            
            updatePromises.push(promise);
            modifiedRows.push(row);
        }
    });

    if (updatePromises.length === 0) {
        isGlobalUpdating.value = false;
        return;
    }

    try {
        const results = await Promise.allSettled(updatePromises);
        
        let successfulUpdates = 0;
        let failedUpdates = 0;
        
        results.forEach((result, index) => {
            const row = modifiedRows[index];
            
            if (result.status === 'fulfilled') {
                fields.value.forEach(field => {
                    row.isModified[field] = false;
                });
                row.hasModifications = false;
                successfulUpdates++;
            } else {
                failedUpdates++;
                console.error( `Ошибка обновления строки ${row.pkValue}: `, result.reason);
            }
        });
        
        globalUpdateSuccess.value = successfulUpdates;
        
        if (failedUpdates > 0) {
            globalUpdateError.value =  `Обновлено ${successfulUpdates} строк. Ошибка при обновлении ${failedUpdates} строк. Проверьте консоль для деталей.`;
        } else {
            hasAnyModifications.value = false;
        }
        
        hasAnyModifications.value = dataResults.value.some(row => row.hasModifications);

    } catch (error) {
        globalUpdateError.value = `Критическая ошибка при отправке запросов: ${error.message}`;
    } finally {
        isGlobalUpdating.value = false;
    }
};

onMounted(() => {
  fetchSchema();
});
</script>


<style scoped>
.table-schema-editor {
  padding: 30px;
  background-color: #f7f7f7;
  border-radius: 10px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
  max-width: 100%;
  margin: 40px auto;
  font-family: 'Arial', sans-serif;
}

h1 {
  color: #333;
  border-bottom: 3px solid #007bff;
  padding-bottom: 10px;
  margin-bottom: 30px;
}

.table-name-highlight {
  color: #007bff;
  font-weight: bold;
}

/* 1. Сообщения о состоянии (Loading/Error/Info) */
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

.info {
  background-color: #f0f0f0;
  color: #555;
  border: 1px solid #ccc;
}

/* 2. Стили Формы Фильтрации (Горизонтальный Layout) */
.data-table-layout {
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden; 
  background-color: #fff;
  margin-bottom: 20px;
  display: flex; 
  flex-direction: column;
}

.flex-row {
  display: flex;
  width: 100%;
}

.header-row {
  border-bottom: 1px solid #ccc;
}

.header-cell {
  flex-grow: 1; 
  flex-basis: 0; 
  padding: 10px 8px;
  font-weight: bold;
  text-align: center;
  border-right: 1px solid #ddd;
  background-color: #f0f0f0;
  font-size: 0.9em;
  color: #333;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.header-cell:last-child {
  border-right: none;
}

.input-cell {
  flex-grow: 1; 
  flex-basis: 0; 
  padding: 5px 8px;
  border-right: 1px solid #ddd;
}

.input-cell:last-child {
  border-right: none;
}

.field-input-cell {
  width: 100%;
  padding: 5px;
  border: 1px solid #eee; 
  border-radius: 4px;
  box-sizing: border-box;
  text-align: center;
}

.field-input-cell:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 1px rgba(0, 123, 255, 0.25);
}

.submit-button {
  display: block;
  width: 100%;
  padding: 12px;
  margin-top: 30px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-button:hover:not(:disabled) {
  background-color: #218838;
}

.submit-button:disabled {
  background-color: #94d3a2;
  cursor: not-allowed;
}

/* 3. Стили Таблицы Результатов и Обновления */

.table-scroll-wrapper {
  overflow-x: auto;
  margin-top: 15px;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  min-width: 800px;
  table-layout: fixed;
}

.results-table th, .results-table td {
  padding: 0;
  border: 1px solid #e0e0e0;
  text-align: left;
  font-size: 0.9em;
  height: 40px; 
}

.results-table th {
  padding: 8px 10px;
  background-color: #007bff;
  color: white;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.result-cell-input {
  padding: 0; 
}

.results-table input {
  width: 100%;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: none;
  background-color: transparent;
  transition: background-color 0.2s;
}

/* Фокус на поле ввода */
.results-table input:focus {
  background-color: #fffde7; 
  outline: 1px solid #ffc107;
  border-radius: 0;
}

/* Выделение измененного поля */
.results-table input.modified {
  background-color: #e6ffed; /* Светло-зеленый фон */
  color: #1890ff;
}

/* 4. Стили Общей Кнопки и Сообщений */

.update-separator {
  margin: 15px 0;
  border: 0;
  border-top: 1px solid #eee;
}

.global-update-actions {
  margin-top: 25px;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: #ffffff;
  text-align: center;
}

.global-update-button {
  /* Переопределяем submit-button для глобальной кнопки */
  margin-top: 0;
  width: 90%;
  padding: 15px;
  font-size: 1.2em;
  background-color: #007bff; /* Синий цвет для действия обновления */
}

.global-update-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.update-error {
  margin-top: 15px;
  background-color: #fff2e8;
  color: #f5222d;
  border: 1px solid #ffbb96;
}

.update-success {
  margin-top: 15px;
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
  font-size: 1em;
}

</style>