<template>
  <div class="report-container">
    <h1>Отчёт по таблицам</h1>

    <!-- Форма ввода даты -->
    <div class="date-input-section">
      <label for="report-date">Выберите дату (дд.мм.гггг):</label>
      <input
        id="report-date"
        v-model="dateInput"
        type="text"
        placeholder="Например: 31.12.2024"
        @keyup.enter="handleDateSubmit"
      />
      <button @click="handleDateSubmit">Загрузить</button>
      <div v-if="dateError" class="error-message">
        {{ dateError }}
      </div>
    </div>

    <!-- Сообщения состояния -->
    <div v-if="loading" class="state-message loading">
      Загрузка отчёта...
    </div>

    <div v-else-if="error" class="state-message error">
      Ошибка: {{ error }}
    </div>

    <div v-else-if="reportData.length === 0" class="state-message info">
      Нет данных для отображения.
    </div>

    <!-- Таблица -->
    <div v-else class="report-table-wrapper">
      <table class="excel-style-table">
        <thead>
          <tr>
            <th>Дата</th>
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
          <tr v-for="(row, index) in reportData" :key="index">
            <td>{{ displayedDate }}</td>
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
// ✅ Сначала — все функции, используемые в шаблоне
function getCompletionPercent(row) {
  if (!row || typeof row !== 'object') return '0%';
  if (!row.all_rows || row.all_rows === 0) return '0%';
  const percent = (row.success || 0) / row.all_rows * 100;
  return `${percent.toFixed(1)}%`;
}

// Импорты
import { ref, onMounted } from 'vue';
import axios from 'axios';

// Реактивные данные
const reportData = ref([]);
const loading = ref(false);
const error = ref(null);
const dateInput = ref('');
const dateError = ref('');
const displayedDate = ref('');

// Конфигурация
const BASE_URL = 'http://127.0.0.1:8000/';
const REPORT_URL = `${BASE_URL}analytics/tables_report/`;

// Форматирование даты в dd.mm.yyyy
const formatDate = (date) => {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}.${month}.${year}`;
};

// Установка сегодняшней даты по умолчанию
const setTodayDate = () => {
  const today = new Date();
  dateInput.value = formatDate(today);
  displayedDate.value = dateInput.value;
};

// Валидация формата dd.mm.yyyy
const validateDate = (value) => {
  const regex = /^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})$/;
  if (!regex.test(value)) return 'Неверный формат. Используйте: дд.мм.гггг';

  const [day, month, year] = value.split('.').map(Number);
  const date = new Date(year, month - 1, day);

  if (
    date.getFullYear() !== year ||
    date.getMonth() !== month - 1 ||
    date.getDate() !== day
  ) {
    return 'Неверная дата (например, 32 февраля)';
  }

  return '';
};

// Загрузка отчёта
const fetchReport = async () => {
  const err = validateDate(dateInput.value);
  if (err) {
    dateError.value = err;
    return;
  }
  dateError.value = '';
  loading.value = true;
  error.value = null;
  reportData.value = [];

  try {
    const response = await axios.get(REPORT_URL, {
      params: { date: dateInput.value },
    });

    if (Array.isArray(response.data)) {
      reportData.value = response.data;
      displayedDate.value = dateInput.value;
    } else {
      throw new Error('Неверный формат данных: ожидается массив');
    }
  } catch (err) {
    error.value = `Не удалось загрузить отчёт: ${
      err.response?.data?.error || err.message || 'неизвестная ошибка'
    }`;
  } finally {
    loading.value = false;
  }
};

// Обработка отправки формы
const handleDateSubmit = () => {
  fetchReport();
};

// При монтировании — загружаем отчёт за сегодня
onMounted(() => {
  setTodayDate();
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

/* Форма ввода даты */
.date-input-section {
  margin-bottom: 24px;
  text-align: center;
}

.date-input-section label {
  font-weight: 500;
  color: #333;
  margin-right: 8px;
}

.date-input-section input {
  padding: 8px 12px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 180px;
}

.date-input-section button {
  margin-left: 8px;
  padding: 8px 16px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.date-input-section button:hover {
  background-color: #1565c0;
}

.error-message {
  color: #c62828;
  font-size: 0.9em;
  margin-top: 6px;
  text-align: left;
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