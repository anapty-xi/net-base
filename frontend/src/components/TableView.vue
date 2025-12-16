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
                    :class="{'modified': row.isModified[field]}"
                    :readonly="field.toLowerCase() === 'id'"
                    class="field-input-cell"
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
            Успешно обновлено строк: {{ globalUpdateSuccess }}
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
        checkColumnIndex.value = fields.value.findIndex(field => 
          field.toLowerCase() === 'проверено'
        );
    } else {
        fields.value = [];
        pkField.value = null; 
        checkColumnIndex.value = -1;
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
        const response = await axios.post(SEARCH_URL, queryPayload);

        
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
        submitError.value = `Нет ни одной строки удволетворяющих запросу`;
    } finally {
        submitting.value = false;
    }
};

const getInputValue = (data, field) => {
  const fieldName = field.toLowerCase();
  const value = data[field];

  if (fieldName === 'проверено' && value === 'у') {
    return '+'; // "у" → показываем как "+"
  }

  return value;
};

const onInput = (row, field, event) => {
  // ✅ Блокируем любое поле с именем 'id' (регистронезависимо)
  if (field.toLowerCase() === 'id') {
    return;
  }

  const newValue = event.target.value.trim();
  const fieldName = field.toLowerCase();

  if (fieldName === 'проверено') {
    const originalValue = row.originalData[field];

    if (['з', 'З'].includes(originalValue) && newValue === '+') {
      row.data[field] = 'у';
    } else if (newValue === '+') {
      row.data[field] = 'у';
    } else {
      row.data[field] = newValue;
    }
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

            const promise = axios.patch(UPDATE_URL, singleUpdatePayload);
            
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
            globalUpdateError.value =  `Обновлено ${successfulUpdates} строк. Ошибка при обновлении ${failedUpdates} строк. Недопустимое значение.`;
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

:root {
  --primary: #1C7C54;
  --primary-dark: #1A5D43;
  --bg-page: #F8F9FA;
  --bg-card: #ffffff;
  --bg-input: #fcfcfc;
  --border: #ddd;
  --text-primary: #2C3E50;
  --text-secondary: #6C757D;
  --text-muted: #aaa;
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
  border: 1px dashed var(--text-muted);
  color: var(--text-secondary);
}

.state-message.error {
  background-color: #ffebee;
  color: var(--error);
  border: 1px solid #f5c6cb;
}

/* Форма поиска — теперь как отдельная секция */
.data-entry-form {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.data-table-layout {
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  background-color: var(--bg-input);
}

.flex-row {
  display: flex;
  width: 100%;
}

.header-row {
  background-color: transparent;
  border-bottom: 2px solid var(--border);
}

.header-cell {
  flex: 1;
  padding: 10px 8px;
  text-align: center;
  font-size: 0.9em;
  font-weight: 500;
  color: var(--text-muted); /* ✅ Бледный цвет заголовков */
  text-transform: none;
  letter-spacing: 0.5px;
}

.input-cell {
  flex: 1;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border);
  background-color: white;
}

.field-input-cell {
  width: 100%;
  padding: 10px 8px;
  border: 1px solid var(--border);
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

/* Маленькая кнопка поиска — слева над таблицей */
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

/* Контейнер для кнопок над таблицей */
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

.global-update-button {
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
}

.global-update-button:hover:not(:disabled) {
  background-color: var(--primary-dark);
}

.global-update-button:disabled {
  background-color: #94d3a2;
  color: #fff;
  cursor: not-allowed;
}

/* Блок с результатами — как отдельная секция */
.results-table-container {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.table-scroll-wrapper {
  overflow-x: auto;
  margin-top: 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
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
  color: var(--text-muted); /* ✅ Бледный цвет заголовков */
  font-weight: 500;
  font-size: 0.9em;
  padding: 10px 8px;
  text-align: center;
  border-bottom: 2px solid var(--border);
  letter-spacing: 0.5px;
}

.results-table td {
  padding: 0;
  border: 1px solid var(--border);
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

/* id-столбец — серый и неактивный */
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

</style>