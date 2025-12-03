from ..entities.table import Table
from typing import List
from datetime import date


class TableValidator:
    def special_col_index(self, cols: List[str], special_col_name: List[str]) -> int | None:
        if any(col in special_col_name for col in cols):
            for index, col in enumerate(cols):
                if col.lower() in special_col_name:
                    return int(index)
        return None
                
    def has_checked(self, table: Table) -> Table:
        check_index = self.special_col_index(table.cols, ['проверено'])
        if check_index:
            for index, row in enumerate(table.rows):
                if row[check_index] not in ['+', 'з', 'З', '']: 
                    raise ValueError(f'Строка {index} содержит недопустимое значение "{row[check_index]}" для столбца. Допустимые значения - "з" "з" "+"')
        else:
            table.cols.append('Проверено')
            for row in table.rows:
                row.append('')
        return table

    def has_date(self, table: Table) -> Table:
        date_index = self.special_col_index(table.cols, ['дата'])
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

    def has_note(self, table: Table) -> Table:
        note_index = self.special_col_index(table.cols, ['примечание', 'замечание']) 
        if  not note_index:
            table.cols.append('Примечание')
            for row in table.rows:
                row.append('')
        return table
    
    def validate_table(self, table: Table) -> Table:
        if table.in_analytics:
            table = self.has_checked(table)
            table = self.has_date(table)
            table = self.has_note(table)
        return table
        