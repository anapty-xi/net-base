import requests
import logging

from ..usecases.table_report_gateway import TableReportProtocol
from django.conf import settings
from typing import Dict, List
from datetime import datetime
from ..entities.table_report import TableReport 
from django.conf import settings

logger = logging.getLogger(__name__)

class Reporter(TableReportProtocol):
    '''
    Собирает данные для создания отчета 
    '''
    def _get_rows_number(self, table_rows) -> int:
        return len(table_rows)
    
    def _get_cheked_number(self, table_rows) -> int:
        counter = 0
        for row in table_rows:
            if row[self.checked_index] != '':
                counter += 1
        return counter
    
    def _get_success_number(self, table_rows) -> int:
        counter = 0
        for row in table_rows:
            if row[self.checked_index] in ['+', 'у']:
                counter += 1
        return counter
    
    def _get_remarks_number(self, table_rows) -> int:
        counter = 0
        for row in table_rows:
            if row[self.checked_index].lower() == 'з':
                counter += 1
        return counter
    
    def _get_elem_remarks_td_number(self, table_rows) -> int:
        counter = 0
        for row in table_rows:
            if row[self.checked_index].lower() == 'у' and row[self.date_index] == datetime.now().date().strftime('%d.%m.%Y'):
                counter += 1
        return counter
    
    def _get_remarks_td_number(self, table_rows) -> int:
        counter = 0
        for row in table_rows:
            if row[self.checked_index].lower() == 'з' and row[self.date_index] == datetime.now().date().strftime('%d.%m.%Y'):
                counter += 1
        return counter
    
    def _get_cheked_td_number(self, table_rows) -> int:
        counter = 0
        for row in table_rows:
            if row[self.date_index] == datetime.now().date().strftime('%d.%m.%Y'):
                counter += 1
        return counter
    
    def get_table_report(self, table_title: str, table_cols: List[str], table_rows: List[List[str]]) -> TableReport:
        '''
        Собирает отчет с помощью функции класса
        '''
        cols = list(map(lambda col: col.lower(), table_cols))
        self.checked_index = cols.index('проверено')
        self.date_index = cols.index('дата')

        table_report = TableReport(
            title=table_title,
            all_rows=self._get_rows_number(table_rows),
            checked=self._get_cheked_number(table_rows),
            success=self._get_success_number(table_rows),
            remarks=self._get_remarks_number(table_rows),
            elemenated_remarks_today=self._get_elem_remarks_td_number(table_rows),
            remarks_today=self._get_remarks_td_number(table_rows),
            checked_today=self._get_cheked_td_number(table_rows),
            rest=self._get_rows_number(table_rows)-self._get_cheked_number(table_rows)
        )
        return table_report
    
    def get_analytics_schemes(self) -> Dict[str, List[str]]:
        '''
        Делает запрос к сервису бд для получения всех схем таблиц. Отбирает и возвращает только схемы таблиц соответсвующих требованиям аналитики
        '''
        all_schemas: Dict[str, List[str]] = requests.get(f'{settings.DB_OPERATIONS_SERVICE_URL}/db/get_table_info/', headers={'X-API-Key': settings.API_KEY}).json()
        logger.info(f'response {all_schemas}')
        analytics_tables = {}
        for table_title, cols in all_schemas.items():
            lower_cols = list(map(lambda col: col.lower(), cols))
            if 'проверено' in lower_cols and 'дата' in lower_cols:
                analytics_tables[table_title] = cols
        return analytics_tables
    
    def get_table_rows(self, table_title: str) -> List[List[str]]:
        '''
        Делает запрос к бд для получения всех строк таблицы
        '''
        return requests.post(f'{settings.DB_OPERATIONS_SERVICE_URL}/db/get_rows/{table_title}/', headers={'X-API-Key': settings.API_KEY}).json()
                              

        
