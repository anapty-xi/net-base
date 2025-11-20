<template>
  <div class="db-table-view">
    <h3>Просмотр Таблицы Базы Данных</h3>

    <div v-if="loading" class="state-message loading">
      Загрузка данных таблицы...
    </div>

    <div v-else-if="error" class="state-message error">
      Ошибка: {{ error }}
    </div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th v-for="colKey in tabels" :key="colKey">
            {{ colKey }}
          </th>
        </tr>
      </thead>
      

    </table>
  </div>
</template>



<script setup>
import { ref, onMounted } from 'vue';

import axios from 'axios';



const DB_URL = 'http://http://localhost:8000/db/get_table_info/'; 


const tabels = ref([])
const loading = ref(true);
const error = ref(null);




  try {
    const response = await axios.get(DB_URL)

    loading.value = true;
    
    tabels.value = Object.keys(response.data)

  } catch (err) {
    console.error("Не удалось получить данные таблицы:", err);
    error.value = `Ошибка загрузки данных: ${err.message}`;

    
  } finally {
    loading.value = false;
  }



</script>