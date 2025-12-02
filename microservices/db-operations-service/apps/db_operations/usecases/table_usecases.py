from ..entities.table import Table
from typing import Optional, List, Dict
from .table_gateway_protocol import TableGayeway


class UseCase:
    def __init__(self, infrastucture_class: TableGayeway):
        self.infrastucture_class = infrastucture_class

class CreateTable(UseCase):
    def has_checked(self, table: Table) -> Table:
        if any(col in ['Проверено', 'проверено'] for col in table.cols):
            for index, col in enumerate(table.cols):
                if col in ['Проверено', 'проверено']:
                    check_index = index
            for index, row in enumerate(table.rows):
                if row[check_index] not in ['+', 'з', 'З', '']: 
                    raise ValueError(f'Строка {index} содержит недопустимое значение "{row[check_index]}" для столбца. Допустимые значения - "з" "з" "+"')


    def has_date(self, table: Table) -> Table:
        pass
    def has_note(self, table: Table) -> Table:
        pass



    def create_table(self, title: str, cols: List[str], rows: List[List[str]], in_analytics: bool):
        table = Table(
            title,
            cols,
            rows,
            in_analytics
        )
        table = self.has_checked(table)
        table = self.has_date(table)
        table = self.has_note(table)
        return self.infrastructure_class.create_table(table)
    
class TableInfo(UseCase):
    def get_table_info(self, title=None):
        tables_data = self.infrastructure_class.get_table_info(title)
        table_entities = [Table(table[0], table[1], table[2]) for table in tables_data]
        return table_entities
    
class UpdateTable(UseCase):
    def update_table_data(self, title: str, row_id: str, updates: Dict[str:str]):
        return self.infrastructure_class.update_row(title, row_id, updates)
    
class DeleteTable(UseCase):
    def delete_table(self, title: str):
        return self.infrastructure_class.delete_table(title)
    
class GetRows(UseCase):
    def get_rows(self, title: str, query_params: Dict[str:str]):
        return self.infrastructure_class.get_rows(title, query_params)