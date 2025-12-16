from ..entities.table import Table
from typing import List, Dict
from datetime import date
import datetime

class TableValidator:
    '''
    Класс для проверки входной таблицы на соответсвие бизнес логике создания таюлиц. Может изменять входные данные
    '''
    def _special_col_index(self, cols: List[str], special_col_name: List[str]) -> int | None:
        '''
        Поиск определенного столбца из переданного набора эталонов
        '''
        cols = list(map(lambda col: col.lower(), cols))
        if any(col in special_col_name for col in cols):
            for special_name in special_col_name:
                if special_name in cols:
                    return cols.index(special_name)
        return None
                
    def _has_checked(self, table: Table) -> Table:
        '''
        Поиск столбца отвечающего за состояние проверки записи. Если его нет - создается, если есть записи проверяются на соответствие столбцу
        '''
        check_index = self._special_col_index(table.cols, ['проверено'])
        if check_index:
            for index, row in enumerate(table.rows):
                if row[check_index] not in ['+', 'з', 'З', '']: 
                    raise ValueError(f'Строка {index} содержит недопустимое значение "{row[check_index]}" для столбца. Допустимые значения - "з" "з" "+"')
        else:
            table.cols.append('Проверено')
            for row in table.rows:
                row.append('')
        return table

    def _has_date(self, table: Table) -> Table:
        '''
        Поиск столбца отвечающего за дату обновления записи. Если его нет - создается, если есть записи проверяются на соответствие столбцу
        '''
        date_index = self._special_col_index(table.cols, ['дата'])
        if date_index:
            for index, row in enumerate(table.rows):
                if row[date_index] == '':
                    continue
                day, month, year = row[date_index].split('.')
                try:
                    date.fromisoformat(f'{year}-{month}-{day}')
                except ValueError:
                    raise ValueError(f'Строка {index} содержит недопустимое значение {row[date_index]} для стобца. Допустимые значения - в формате year.month.day')
        else:
            table.cols.append('Дата')
            for row in table.rows:
                row.append('')
        return table

    def _has_note(self, table: Table) -> Table:
        '''
        Поиск столбца отвечающего за примечание к записи. Если его нет - создается
        '''
        note_index = self._special_col_index(table.cols, ['примечание', 'замечание']) 
        if  not note_index:
            table.cols.append('Примечание')
            for row in table.rows:
                row.append('')
        return table
    
    def validate_table(self, table: Table) -> Table:
        '''
        Функция применяет к таблице все методы валидации таблицы класса 
        '''
        if table.in_analytics:
            table = self._has_checked(table)
            table = self._has_date(table)
            table = self._has_note(table)
        return table
        

class UpdatesValidator(): #TODO: в таблицу модет не быть этих столбцов
    '''
    Валидирует словарь для обновления таблицы. Если обновляется столбец "Проверено", то проверяет значение обновления и изменяет дату
    '''
    def cheked_field_validation(self, table_cols: List[str], **updates) -> Dict[str, str]:
        table_cols_lower = list(map(lambda col: col.lower(), table_cols))
        check_field = table_cols[table_cols_lower.index('проверено')]
        date_field = table_cols[table_cols_lower.index('дата')]

        if check_field in updates.keys():
            if updates[check_field] not in ['+', 'з', 'З', '', 'у']:
                raise ValueError(f'Значение словаря обновления "{check_field}" = "{updates[check_field]}", что не удволетворяет условиям столбца')
            updates[date_field] = str(datetime.datetime.now().strftime('%d.%m.%Y'))
        return updates
