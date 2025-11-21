<template>
  <div class="table-schema-editor">
    <h1><span class="table-name-highlight">{{ tableName }}</span></h1>

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
            <div v-for="field in fields" :key="field.name" class="input-cell">
              
              <input 
                :id="field.name" 
                :name="field.name"
                type="text" 
                :placeholder="field.type"
                :required="!field.nullable"
                class="field-input-cell"
              />
              
            </div>
          </div>
          
        </div>
        
        <button type="submit" class="submit-button">Выполнить поиск / Сохранить</button>
      </form>
      
      <p v-if="fields.length === 0" class="state-message info">
        В таблице нет полей для отображения.
      </p>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';


const route = useRoute();
const tableName = route.params.tableName


const fields = ref([]);
const loading = ref(true);
const error = ref(null);


const BASE_URL = 'http://localhost:8000/db/get_table_info/'; 



const fetchSchema = async () => {
    

    const SCHEMA_URL = `${BASE_URL}${tableName}`; 



    try {
        const response = await axios.get(SCHEMA_URL);
        

        fields.value = response.data[tableName]; 
        console.log(response.data)

    } catch (err) {
        console.error(`Ошибка получения схемы для таблицы ${tableName}:`, err);
        error.value = `Не удалось загрузить схему таблицы. Ошибка: ${err.message}`;
    } finally {
        loading.value = false;
    }
};

// 4. Запуск получения данных при монтировании компонента
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
  max-width: 800px;
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

/* Сообщения о состоянии */
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
.instruction {
    margin-bottom: 25px;
    font-size: 1.1em;
    color: #555;
    font-style: italic;
}

/* Группа поля */
.field-group {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.field-label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
  font-size: 1.05em;
}

.field-type {
  font-weight: normal;
  color: #6c757d;
  font-size: 0.9em;
  margin-left: 5px;
}

.required {
  color: #f5222d;
  margin-left: 5px;
}

.field-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.field-input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
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

.submit-button:hover {
  background-color: #218838;
}


/* Ваши существующие стили */
.table-schema-editor {
  /* ... */
  max-width: 100%; /* Увеличим ширину, чтобы уместить много столбцов */
}

/* ... (прочие стили h1, state-message и т.д.) ... */

/* ---------------------------------------------------- */
/* НОВЫЕ СТИЛИ ДЛЯ ГОРИЗОНТАЛЬНОГО ОТОБРАЖЕНИЯ (Excel-стиль) */
/* ---------------------------------------------------- */

.data-table-layout {
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden; /* Обрезает содержимое, если ширина превышает контейнер */
  background-color: #fff;
  margin-bottom: 20px;
}

/* Класс для горизонтальных рядов с Flexbox */
.flex-row {
  display: flex;
  width: 100%;
}

/* Ячейка заголовка */
.header-cell {
  flex-grow: 1; /* Распределяем пространство равномерно */
  flex-basis: 0; /* Базовый размер 0, чтобы flex-grow работал лучше */
  padding: 10px 8px;
  font-weight: bold;
  text-align: center;
  border-right: 1px solid #ddd;
  background-color: #f0f0f0; /* Серый фон для заголовков */
  font-size: 0.9em;
  color: #333;
}

/* Убираем правую границу у последнего заголовка */
.header-cell:last-child {
  border-right: none;
}


/* Ячейка ввода */
.input-cell {
  flex-grow: 1; 
  flex-basis: 0; 
  padding: 5px 8px;
  border-right: 1px solid #ddd;
  border-top: 1px solid #ccc;
}

/* Убираем правую границу у последнего поля ввода */
.input-cell:last-child {
  border-right: none;
}

.field-input-cell {
  width: 100%;
  padding: 5px;
  border: 1px solid #eee; /* Более тонкая граница */
  border-radius: 4px;
  box-sizing: border-box;
  text-align: center; /* Центрируем текст */
}

/* ... (submit-button и прочие стили остаются без изменений) ... */

</style>