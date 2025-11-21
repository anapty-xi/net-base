<template>
  <div class="db-table-view">
    <h3>Список Таблиц Базы Данных</h3>

    <div v-if="loading" class="state-message loading">
      Загрузка названий таблиц...
    </div>

    <div v-else-if="error" class="state-message error">
      Ошибка: {{ error }}
    </div>

    <ul v-else class="table-list">
      <li v-for="tableName in tabels" :key="tableName">
        {{ tableName }}
      </li>
    </ul>
    
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue';

import axios from 'axios';



const DB_URL = 'http://localhost:8000/db/get_table_info/'; 


const tabels = ref([])
const loading = ref(true);
const error = ref(null);


const fetchData = async () => {

  try {
    const response = await axios.get(DB_URL)
    
    tabels.value = Object.keys(response.data.tabels)

  } catch (err) {
    console.error("Не удалось получить данные таблицы:", err);
    error.value = `Ошибка загрузки данных: ${err.message}`;

    
  } finally {
    loading.value = false;
  }
};
onMounted(() => {
  fetchData();
})


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

</style>