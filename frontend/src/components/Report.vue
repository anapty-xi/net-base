<!-- ReportView.vue -->
<template>
  <div class="report-container">
    <h1>Отчёт по таблицам</h1>

    <div v-if="loading" class="state-message loading">
      Загрузка отчёта...
    </div>

    <div v-else-if="error" class="state-message error">
      Ошибка: {{ error }}
    </div>

    <div v-else-if="reportData.length === 0" class="state-message info">
      Нет данных для отображения.
    </div>

    <div v-else class="report-table-wrapper">
      <table class="excel-style-table">
        <thead>
          <tr>
            <th>Таблица</th>
            <th>Выполнение</th>
            <th>Всего</th>
            <th>Проверено</th>
            <th>Успешно</th>
            <th>Замечания</th>
            <th>Устранено сегодня</th>
            <th>Найдено сегодня</th>
            <th>Остаток</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in reportData" :key="row.title">
            <td class="cell-bold">{{ row.title }}</td>
            <td class="cell-percentage">{{ getCompletionPercent(row) }}</td>
            <td>{{ row.all_rows }}</td>
            <td>{{ row.checked }}</td>
            <td class="cell-success">{{ row.success }}</td>
            <td class="cell-warning">{{ row.remarks }}</td>
            <td>{{ row.elemenated_remarks_today }}</td>
            <td>{{ row.remarks_today }}</td>
            <td>{{ row.rest }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const reportData = ref([]);
const loading = ref(true);
const error = ref(null);

const BASE_URL = 'http://localhost:8000/'; 
const REPORT_URL = `${BASE_URL}analytics/tables_report/`;

const fetchReport = async () => {
  try {
    const response = await axios.get(REPORT_URL);
    if (Array.isArray(response.data)) {
      reportData.value = response.data;
    } else {
      throw new Error('Неверный формат данных: ожидается массив');
    }
  } catch (err) {
    error.value = `Не удалось загрузить отчёт: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

const getCompletionPercent = (row) => {
  if (!row.all_rows) return '0%';
  const percent = (row.success / row.all_rows) * 100;
  return `${percent.toFixed(1)}%`;
};

onMounted(() => {
  fetchReport();
});
</script>

<style scoped>
.report-container {
  padding: 30px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 20px auto;
  max-width: 1200px;
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 20px;
}

/* Excel-подобная таблица */
.report-table-wrapper {
  overflow-x: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
}

.excel-style-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  font-size: 0.95em;
}

.excel-style-table th,
.excel-style-table td {
  border: 1px solid #ddd;
  padding: 10px 12px;
  text-align: center;
  white-space: nowrap;
}

.excel-style-table th {
  background-color: #f0f0f0;
  color: #333;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.excel-style-table tr:nth-child(even) {
  background-color: #fafafa;
}

.excel-style-table tr:hover {
  background-color: #f1f8ff;
}

/* Стили ячеек */
.cell-bold {
  font-weight: 600;
  color: #1a1a1a;
}

.cell-success {
  color: #28a745;
  font-weight: 500;
}

.cell-warning {
  color: #d32f2f;
  font-weight: 500;
}

.cell-percentage {
  font-weight: 600;
  color: #1976d2;
}

/* Сообщения */
.state-message {
  padding: 16px;
  border-radius: 6px;
  font-weight: 500;
  text-align: center;
  margin: 20px 0;
}

.loading {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #90caf9;
}

.error {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ef9a9a;
}

.info {
  background-color: #fff3e0;
  color: #fb8c00;
  border: 1px solid #ffb74d;
}
</style>