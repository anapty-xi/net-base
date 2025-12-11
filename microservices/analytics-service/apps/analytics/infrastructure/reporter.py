import requests

from ..usecases.table_report_gateway import TableReportProtocol
from django.conf import settings
from requests import Response
from typing import Dict, List
from datetime import datetime

class Reporter(TableReportProtocol):
    '''
    Собирает данные для создания отчета 
    '''
    def __init__(self, table_title: str, table_cols: List[str]):
        '''
        Делает два запроса к сервису бд для получения схемы таблицы и всех ее строк. Если в схеме нет столбцов "проверено" или "дата"
        возвращает ошибку, так как это говорит о том что таблица не предусматривает аналитику
        '''
        self.db_url = settings.DB_OPERATIONS_URL
        self.table_title = table_title

        self.cols = table_cols
        self.rows: List[List[str]] = requests.get(f'{self.db_url}/db/get_rows/{table_title}/').data

        table_cols = list(map(lambda col: col.lower(), self.cols))
        self.checked_index: int = table_cols.index('проверено')
        self.date_index: int = table_cols.index('дата') 


    def get_rows_number(self) -> int:
        return len(self.rows)
    
    def get_cheked_number(self) -> int:
        counter = 0
        for row in self.rows:
            if row[self.checked_index] != '':
                counter += 1
        return counter
    
    def get_success_number(self) -> int:
        counter = 0
        for row in self.rows:
            if row[self.checked_index] == '+':
                counter += 1
        return counter
    
    def get_remarks_number(self) -> int:
        counter = 0
        for row in self.rows:
            if row[self.checked_index].lower() == 'з':
                counter += 1
        return counter
    
    def get_elem_remarks_td_number(self) -> int:
        counter = 0
        for row in self.rows:
            if row[self.checked_index].lower() == 'у' and row[self.date_index] == datetime.now().date().strftime('%d.%m.%Y'):
                counter += 1
        return counter
    
    def get_remarks_td_number(self) -> int:
        counter = 0
        for row in self.rows:
            if row[self.checked_index].lower() == 'з' and row[self.date_index] == datetime.now().date().strftime('%d.%m.%Y'):
                counter += 1
        return counter
    
    def get_cheked_td_number(self) -> int:
        counter = 0
        for row in self.rows:
            if row[self.date_index] == datetime.now().date().strftime('%d.%m.%Y'):
                counter += 1
        return counter
    
    @classmethod
    def get_tables_in_analytics() -> Dict[str, List[str]]:
        table_schemas = requests.get(f'{settings.DB_OPERATIONS_URL}/db/get_table/info/').data
        analytics_tables = {}
        for table_title, cols in table_schemas.values():
            if 'проверено' in cols and 'дата' in cols:
                analytics_tables[table_title] = cols
        return analytics_tables
